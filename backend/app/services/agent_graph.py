import json
import logging
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.app.services.llm_service import llm_service, ToolCall
from backend.app.services.tool_registry import registry
from backend.app.services.context_engine import context_engine
from backend.app.services.memory_repository import memory_repository
from backend.app.models.schemas import RiskLevel, AgentAction

logger = logging.getLogger("SmartGlasses.AgentGraph")

class AgentState(TypedDict):
    session_id: str
    user_message: str
    messages: List[Dict[str, str]]
    context_payload: Dict[str, Any]
    actions: List[Dict[str, Any]]
    requires_confirmation: bool
    confirmation_prompt: Optional[str]
    final_response: Optional[str]
    iteration_count: int

def load_session_and_context(state: AgentState) -> Dict[str, Any]:
    """Node: Load past conversation history and enrich with Context Engine."""
    session_id = state["session_id"]
    user_msg = state["user_message"]

    # 1. Load short-term history from SQLite
    history = memory_repository.get_session_history(session_id, limit=6)
    messages = list(history)

    # 2. Build system context message
    ctx = state.get("context_payload") or {}
    t_info = ctx.get("time", {})
    l_info = ctx.get("location", {})
    c_info = ctx.get("calendar", {})

    system_prompt = (
        f"You are the AI assistant inside smart glasses.\n"
        f"Keep responses natural, concise, helpful, and wearable-friendly.\n"
        f"Current Time: {t_info.get('local_time', '08:15 AM')} ({t_info.get('period', 'morning')})\n"
        f"Current Location: {l_info.get('city', 'Nagpur')}, {l_info.get('country', 'India')}\n"
    )
    if c_info.get("next_event"):
        ne = c_info["next_event"]
        system_prompt += f"Next Calendar Event: {ne.get('title')} at {ne.get('start_time')}\n"

    # Prepend or update system message
    messages = [{"role": "system", "content": system_prompt}] + messages
    messages.append({"role": "user", "content": user_msg})

    return {
        "messages": messages,
        "iteration_count": 0,
        "actions": []
    }

async def call_llm_node(state: AgentState) -> Dict[str, Any]:
    """Node: Call LLM with tool definitions and current messages."""
    messages = state["messages"]
    ctx = state.get("context_payload", {})
    tools = [
        {
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters
        }
        for t in registry.list_tools()
    ]

    llm_resp = await llm_service.generate(messages, tools=tools, context_payload=ctx)

    if llm_resp.tool_calls:
        # Save tool calls in state
        return {
            "actions": [
                {
                    "tool_name": tc.name,
                    "tool_input": tc.arguments,
                    "status": "requested"
                }
                for tc in llm_resp.tool_calls
            ],
            "iteration_count": state["iteration_count"] + 1
        }
    else:
        return {
            "final_response": llm_resp.content or "I am ready to help.",
            "iteration_count": state["iteration_count"] + 1
        }

async def execute_tool_node(state: AgentState) -> Dict[str, Any]:
    """Node: Execute requested tool or prepare confirmation."""
    actions = state.get("actions", [])
    messages = list(state["messages"])
    updated_actions = []
    requires_conf = False
    conf_prompt = None

    for act in actions:
        tool_name = act["tool_name"]
        tool_input = act["tool_input"]
        tool_def = registry.get_tool(tool_name)

        if not tool_def:
            res_str = json.dumps({"error": f"Tool {tool_name} not found"})
        elif tool_def.requires_confirmation or tool_def.risk_level == RiskLevel.HIGH_RISK_WRITE:
            requires_conf = True
            conf_prompt = f"I am ready to run {tool_name} with {tool_input}. Should I proceed?"
            updated_actions.append({
                "tool_name": tool_name,
                "tool_input": tool_input,
                "risk_level": tool_def.risk_level.value,
                "status": "pending_confirmation"
            })
            continue
        else:
            try:
                result = registry.execute(tool_name, **tool_input)
                res_str = json.dumps(result) if not isinstance(result, str) else result
                updated_actions.append({
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "risk_level": tool_def.risk_level.value,
                    "status": "executed",
                    "result": result
                })
            except Exception as e:
                res_str = json.dumps({"error": str(e)})
                updated_actions.append({
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "risk_level": tool_def.risk_level.value if tool_def else "READ",
                    "status": "error",
                    "result": str(e)
                })

        # Append tool execution result to message history for next LLM turn
        messages.append({
            "role": "tool",
            "content": res_str,
            "name": tool_name
        })

    if requires_conf:
        return {
            "actions": updated_actions,
            "requires_confirmation": True,
            "confirmation_prompt": conf_prompt,
            "final_response": conf_prompt
        }

    return {
        "messages": messages,
        "actions": updated_actions
    }

def route_after_llm(state: AgentState) -> str:
    """Conditional Edge: Determine if tools need executing or finish."""
    if state.get("requires_confirmation"):
        return END
    if state.get("final_response"):
        return END
    if state.get("actions") and state.get("iteration_count", 0) <= 3:
        return "execute_tool"
    return END

def build_smart_glasses_graph():
    graph = StateGraph(AgentState)

    graph.add_node("load_session_and_context", load_session_and_context)
    graph.add_node("call_llm", call_llm_node)
    graph.add_node("execute_tool", execute_tool_node)

    graph.add_edge(START, "load_session_and_context")
    graph.add_edge("load_session_and_context", "call_llm")
    graph.add_conditional_edges("call_llm", route_after_llm, {
        "execute_tool": "execute_tool",
        END: END
    })
    graph.add_edge("execute_tool", "call_llm")

    # In-memory checkpointer for conversational continuity
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)

agent_graph = build_smart_glasses_graph()

async def run_agent(session_id: str, user_message: str, context_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute LangGraph agent workflow for a given user turn."""
    initial_state: AgentState = {
        "session_id": session_id,
        "user_message": user_message,
        "messages": [],
        "context_payload": context_payload,
        "actions": [],
        "requires_confirmation": False,
        "confirmation_prompt": None,
        "final_response": None,
        "iteration_count": 0
    }

    config = {"configurable": {"thread_id": session_id}}
    result = await agent_graph.ainvoke(initial_state, config=config)

    final_resp = result.get("final_response") or "I processed your request."

    # Save to SQLite memory repository
    memory_repository.save_message(session_id, "user", user_message)
    memory_repository.save_message(session_id, "assistant", final_resp)

    return {
        "response": final_resp,
        "actions": [
            AgentAction(
                tool_name=a["tool_name"],
                tool_input=a.get("tool_input", {}),
                risk_level=a.get("risk_level", RiskLevel.READ),
                status=a.get("status", "executed"),
                result=a.get("result")
            )
            for a in result.get("actions", [])
        ],
        "requires_confirmation": result.get("requires_confirmation", False),
        "confirmation_prompt": result.get("confirmation_prompt")
    }
