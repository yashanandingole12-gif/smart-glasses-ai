import json
import time
import logging
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.app.config import settings
from backend.app.services.llm_service import ToolCall
from backend.app.services.llm_router import llm_router, RoutingTier, FailureCategory
from backend.app.services.tool_registry import registry
from backend.app.services.context_engine import context_engine
from backend.app.services.memory_repository import memory_repository
from backend.app.models.schemas import RiskLevel, AgentAction

logger = logging.getLogger("SmartGlasses.AgentGraph")

class AgentState(TypedDict):
    session_id: str
    user_message: str
    language: Optional[str]
    locale: Optional[str]
    messages: List[Dict[str, str]]
    context_payload: Dict[str, Any]
    actions: List[Dict[str, Any]]
    requires_confirmation: bool
    confirmation_prompt: Optional[str]
    final_response: Optional[str]
    iteration_count: int
    timings: Dict[str, Any]
    routing_metadata: Dict[str, Any]

def load_session_and_context(state: AgentState) -> Dict[str, Any]:
    """Node: Load bounded past conversation history and build minimal necessary context."""
    session_id = state["session_id"]
    user_msg = state["user_message"]
    lang = state.get("language") or "auto"
    loc = state.get("locale") or "en-IN"

    # Bounded recent history
    history = memory_repository.get_session_history(session_id, limit=settings.RECENT_MESSAGES_LIMIT)
    messages = list(history)

    # Minimal system prompt
    ctx = state.get("context_payload") or {}
    t_info = ctx.get("time", {})
    l_info = ctx.get("location", {})
    c_info = ctx.get("calendar", {})

    lang_instructions = (
        "Respond concisely in 1-2 sentences in the same language and script as user query. "
        "Keep responses brief, wearable-friendly, and voice-optimized.\n"
    )

    system_prompt = (
        f"You are the AI assistant inside smart glasses.\n"
        f"{lang_instructions}"
        f"Time: {t_info.get('local_time', '08:15 AM')} ({t_info.get('period', 'morning')})\n"
    )
    if l_info.get("is_available") and l_info.get("city") not in ["Unavailable", "Unknown", None]:
        system_prompt += f"Location: {l_info.get('city')}\n"

    if c_info.get("next_event"):
        ne = c_info["next_event"]
        system_prompt += f"Next Event: {ne.get('title')} at {ne.get('start_time')}\n"

    messages = [{"role": "system", "content": system_prompt}] + messages
    messages.append({"role": "user", "content": user_msg})

    return {
        "messages": messages,
        "iteration_count": 0,
        "actions": [],
        "timings": state.get("timings") or {},
        "routing_metadata": state.get("routing_metadata") or {}
    }

async def call_llm_node(state: AgentState) -> Dict[str, Any]:
    """Node: Call LLM via multi-tier Router with latency budget & fallback cascade."""
    messages = state["messages"]
    ctx = state.get("context_payload", {})
    user_msg = state["user_message"].lower()
    timings = dict(state.get("timings") or {})
    routing_meta = dict(state.get("routing_metadata") or {})

    # Selective tool binding
    has_email_intent = any(
        kw in user_msg or kw in state["user_message"]
        for kw in ["email", "mail", "gmail", "ईमेल", "तपासा", "संदेश", "चेक", "unread", "inbox"]
    )

    tools = None
    if has_email_intent:
        tools = [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            }
            for t in registry.list_tools()
            if "gmail" in t.name
        ]

    # Select starting tier based on complexity
    starting_tier = RoutingTier.PRIMARY if has_email_intent else RoutingTier.FAST

    # Route through LLM Router with timeout budget
    t0 = time.time()
    router_resp = await llm_router.generate_with_budget(
        messages=messages,
        tools=tools,
        context_payload=ctx,
        starting_tier=starting_tier
    )
    duration_ms = (time.time() - t0) * 1000.0

    if "llm_first_response_ms" not in timings:
        timings["llm_first_response_ms"] = duration_ms
    else:
        timings["llm_final_response_ms"] = duration_ms

    routing_meta["tier_used"] = router_resp.tier_used.value
    routing_meta["provider"] = router_resp.provider
    routing_meta["model"] = router_resp.model
    routing_meta["fallback_chain"] = router_resp.fallback_chain
    routing_meta["failure_category"] = router_resp.failure_category.value

    iter_count = state["iteration_count"] + 1

    if router_resp.tool_calls:
        return {
            "actions": [
                {
                    "tool_name": tc.name,
                    "tool_input": tc.arguments,
                    "status": "requested"
                }
                for tc in router_resp.tool_calls
            ],
            "iteration_count": iter_count,
            "timings": timings,
            "routing_metadata": routing_meta
        }
    else:
        return {
            "final_response": router_resp.content or "I am ready to help.",
            "iteration_count": iter_count,
            "timings": timings,
            "routing_metadata": routing_meta
        }

async def execute_tool_node(state: AgentState) -> Dict[str, Any]:
    """Node: Execute requested tool or prepare confirmation."""
    actions = state.get("actions", [])
    messages = list(state["messages"])
    timings = dict(state.get("timings") or {})
    updated_actions = []
    requires_conf = False
    conf_prompt = None

    t_tool_start = time.time()
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

        messages.append({
            "role": "tool",
            "content": res_str,
            "name": tool_name
        })

    timings["tool_ms"] = (time.time() - t_tool_start) * 1000.0

    if requires_conf:
        return {
            "actions": updated_actions,
            "requires_confirmation": True,
            "confirmation_prompt": conf_prompt,
            "final_response": conf_prompt,
            "timings": timings
        }

    return {
        "messages": messages,
        "actions": updated_actions,
        "timings": timings
    }

def route_after_llm(state: AgentState) -> str:
    """Conditional Edge: Section 10 & 11 - Strict iteration limit enforcement."""
    if state.get("requires_confirmation"):
        return END
    if state.get("final_response"):
        return END
    # Stop safely if max agent steps exceeded
    if state.get("iteration_count", 0) >= settings.MAX_AGENT_STEPS:
        logger.warning(f"Agent reached MAX_AGENT_STEPS ({settings.MAX_AGENT_STEPS}). Stopping.")
        return END
    if state.get("actions"):
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

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)

agent_graph = build_smart_glasses_graph()

async def run_agent(
    session_id: str,
    user_message: str,
    context_payload: Dict[str, Any],
    language: str = "auto",
    locale: str = "en-IN"
) -> Dict[str, Any]:
    """Execute LangGraph agent workflow with routing and safe step limiting."""
    t_start = time.time()
    initial_state: AgentState = {
        "session_id": session_id,
        "user_message": user_message,
        "language": language,
        "locale": locale,
        "messages": [],
        "context_payload": context_payload,
        "actions": [],
        "requires_confirmation": False,
        "confirmation_prompt": None,
        "final_response": None,
        "iteration_count": 0,
        "timings": {},
        "routing_metadata": {}
    }

    config = {"configurable": {"thread_id": session_id}}
    result = await agent_graph.ainvoke(initial_state, config=config)

    total_agent_ms = (time.time() - t_start) * 1000.0
    timings = result.get("timings") or {}
    timings["agent_ms"] = total_agent_ms

    final_resp = result.get("final_response") or "I processed your request."
    routing_meta = result.get("routing_metadata") or {}

    # Save to memory
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
        "confirmation_prompt": result.get("confirmation_prompt"),
        "timings": timings,
        "routing_metadata": routing_meta,
        "steps_count": result.get("iteration_count", 1)
    }
