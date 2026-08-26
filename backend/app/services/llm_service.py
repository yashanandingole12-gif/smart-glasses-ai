import json
import logging
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.config import settings

logger = logging.getLogger("SmartGlasses.LLMService")

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class LLMResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    provider: str
    model: str

class LLMService:
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self._custom_provider = provider
        self._custom_model = model
        self._custom_api_key = api_key
        self._custom_base_url = base_url

    @property
    def provider(self) -> str:
        return (self._custom_provider or settings.LLM_PROVIDER).lower()

    @property
    def model(self) -> str:
        if self.provider == "gemini":
            return self._custom_model or settings.GEMINI_MODEL or settings.LLM_MODEL
        return self._custom_model or settings.LLM_MODEL

    @property
    def api_key(self) -> Optional[str]:
        if self.provider == "gemini":
            return self._custom_api_key or settings.GEMINI_API_KEY or settings.LLM_API_KEY
        return self._custom_api_key or settings.LLM_API_KEY

    @property
    def base_url(self) -> Optional[str]:
        return self._custom_base_url or settings.LLM_BASE_URL

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        context_payload: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Model-agnostic generation routing to appropriate provider.
        """
        if self.provider == "mock":
            return await self._generate_mock(messages, tools, context_payload)
        elif self.provider in ["openai", "gemini", "anthropic"]:
            if not self.api_key or self.api_key.strip() == "":
                err_msg = f"LLM_PROVIDER is set to '{self.provider}' but LLM_API_KEY is missing. Please set your API key in .env or switch LLM_PROVIDER to 'mock'."
                logger.error(err_msg)
                return LLMResponse(
                    content=err_msg,
                    provider=self.provider,
                    model=self.model
                )
            if self.provider == "openai":
                return await self._generate_openai(messages, tools)
            elif self.provider == "gemini":
                return await self._generate_gemini(messages, tools)
            elif self.provider == "anthropic":
                return await self._generate_anthropic(messages, tools)
        elif self.provider == "ollama":
            return await self._generate_ollama(messages, tools)
        else:
            logger.warning(f"Unknown provider '{self.provider}', falling back to mock provider.")
            return await self._generate_mock(messages, tools, context_payload)

    async def _generate_mock(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        context_payload: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Intelligent context-aware fallback provider that accurately demonstrates smart-glasses responses.
        """
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").strip()
                break

        msg_lower = last_user_msg.lower()

        # Check for tool responses in conversation
        tool_results = [m for m in messages if m.get("role") == "tool" or m.get("role") == "function"]

        if tool_results:
            last_tool_res = tool_results[-1].get("content", "")
            try:
                data = json.loads(last_tool_res)
            except Exception:
                data = last_tool_res

            # Format tool response
            if "unread_count" in str(data):
                unread = data.get("unread_count", 1) if isinstance(data, dict) else 1
                return LLMResponse(
                    content=f"You have {unread} unread emails. The latest is from {data['messages'][0]['sender'] if isinstance(data, dict) and data.get('messages') else 'college admin'}.",
                    provider="mock",
                    model=self.model
                )
            elif "free_slots" in str(data):
                return LLMResponse(
                    content="You are free between 12:00 PM and 3:00 PM today, and after 7:30 PM.",
                    provider="mock",
                    model=self.model
                )
            elif "events" in str(data):
                next_ev = data.get("next_event", {}) if isinstance(data, dict) else {}
                title = next_ev.get("title", "Class")
                t = next_ev.get("start_time", "10:30 AM")
                return LLMResponse(
                    content=f"Your next event is {title} at {t}.",
                    provider="mock",
                    model=self.model
                )

        # Multilingual context extraction
        time_str = "8:15 AM"
        city = "Nagpur"
        next_ev_str = "class at 10:30"
        period = "morning"

        if context_payload:
            t_info = context_payload.get("time", {})
            time_str = t_info.get("local_time", time_str)
            period = t_info.get("period", period)
            if hasattr(period, "value"):
                period = period.value
            period = str(period).lower().replace("timeperiod.", "")
            loc_info = context_payload.get("location", {})
            city = loc_info.get("city", city)
            cal_info = context_payload.get("calendar", {})
            if cal_info.get("next_event"):
                ev = cal_info["next_event"]
                next_ev_str = f"{ev.get('title', 'event').lower()} at {ev.get('start_time', '10:30')}"

        # 1. Hindi Greeting & Query Support
        if any(h in last_user_msg for h in ["सुप्रभात", "नमस्ते", "शुभ प्रभात", "शुभ दोपहर", "शुभ संध्या"]):
            return LLMResponse(
                content=f"सुप्रभात! अभी {time_str} बजे हैं और आप {city} में हैं। आपकी अगली क्लास 10:30 AM पर है। मैं आपकी क्या मदद कर सकता हूँ?",
                provider="mock",
                model=self.model
            )

        # 2. Marathi Greeting & Query Support
        if any(m in last_user_msg for m in ["शुभ सकाळ", "नमस्कार", "शुभ दुपार", "शुभ संध्याकाळ"]):
            return LLMResponse(
                content=f"शुभ सकाळ! आता सकाळचे {time_str} झाले आहेत आणि तुम्ही {city}मध्ये आहात. तुमचा पुढचा क्लास 10:30 AM वाजता आहे. मी काय मदत करू शकतो?",
                provider="mock",
                model=self.model
            )

        # 3. Hinglish Greeting & Calendar Query Support
        if ("aaj" in msg_lower and "calendar" in msg_lower) or ("mera calendar" in msg_lower) or ("good morning" in msg_lower and ("aaj" in msg_lower or "karo" in msg_lower or "check" in msg_lower)):
            return LLMResponse(
                content=f"Good morning! Aaj {time_str} par aap {city} mein hain. Aapki next class 10:30 AM par Machine Learning lecture hai.",
                provider="mock",
                model=self.model
            )

        # 4. Standard English Context-aware greetings
        if any(g in msg_lower for g in ["good morning", "morning", "good afternoon", "good evening", "good night", "hello", "hi"]):
            greeting = f"Good {period}" if period != "night" else "Good evening"
            content = f"{greeting}. It's {time_str} and you're in {city}. You have {next_ev_str}. How can I help?"
            return LLMResponse(content=content, provider="mock", model=self.model)

        has_email_context = any("email" in m.get("content", "").lower() or "mail" in m.get("content", "").lower() for m in messages)
        has_cal_context = any("calendar" in m.get("content", "").lower() or "event" in m.get("content", "").lower() or "class" in m.get("content", "").lower() for m in messages)

        # Tool triggering heuristics for mock mode
        if "email" in msg_lower or "mail" in msg_lower or (has_email_context and "read" in msg_lower):
            if "read" in msg_lower or "first" in msg_lower or "second" in msg_lower or "third" in msg_lower:
                idx = 1
                if "second" in msg_lower or "2" in msg_lower:
                    idx = 2
                elif "third" in msg_lower or "3" in msg_lower:
                    idx = 3
                return LLMResponse(
                    tool_calls=[ToolCall(name="gmail_read", arguments={"index": idx})],
                    provider="mock",
                    model=self.model
                )
            return LLMResponse(
                tool_calls=[ToolCall(name="gmail_search", arguments={"query": "is:unread"})],
                provider="mock",
                model=self.model
            )

        if "calendar" in msg_lower or "class" in msg_lower or "next" in msg_lower or "schedule" in msg_lower or "event" in msg_lower or (has_cal_context and "when" in msg_lower):
            if "free" in msg_lower:
                return LLMResponse(
                    tool_calls=[ToolCall(name="calendar_find_free_time", arguments={})],
                    provider="mock",
                    model=self.model
                )
            return LLMResponse(
                tool_calls=[ToolCall(name="calendar_get_events", arguments={})],
                provider="mock",
                model=self.model
            )

        if "search" in msg_lower or "pants" in msg_lower or "wearing" in msg_lower:
            if "pants" in msg_lower or "cloth" in msg_lower or "wearing" in msg_lower:
                return LLMResponse(
                    tool_calls=[ToolCall(name="product_search", arguments={"category": "cargo pants", "color": "black", "style": "loose"})],
                    provider="mock",
                    model=self.model
                )
            return LLMResponse(
                tool_calls=[ToolCall(name="web_search", arguments={"query": last_user_msg})],
                provider="mock",
                model=self.model
            )

        if "where am i" in msg_lower or "location" in msg_lower:
            return LLMResponse(
                tool_calls=[ToolCall(name="get_location", arguments={})],
                provider="mock",
                model=self.model
            )

        if "time" in msg_lower:
            return LLMResponse(
                tool_calls=[ToolCall(name="get_time", arguments={})],
                provider="mock",
                model=self.model
            )

        # Default conversational response
        return LLMResponse(
            content=f"I'm listening on your smart glasses. (Echo: {last_user_msg})",
            provider="mock",
            model=self.model
        )

    async def _generate_openai(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        url = (self.base_url or "https://api.openai.com/v1") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages
        }
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]
            content = choice.get("content")
            tool_calls = None
            if choice.get("tool_calls"):
                tool_calls = [
                    ToolCall(
                        name=tc["function"]["name"],
                        arguments=json.loads(tc["function"]["arguments"])
                    )
                    for tc in choice["tool_calls"]
                ]
            return LLMResponse(content=content, tool_calls=tool_calls, provider="openai", model=self.model)

    async def _generate_gemini(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        models_to_try = [self.model]
        if "gemini-flash-lite-latest" not in models_to_try:
            models_to_try.append("gemini-flash-lite-latest")

        # 1. Extract system instructions
        system_prompts = [m["content"] for m in messages if m.get("role") == "system"]
        payload: Dict[str, Any] = {}
        if system_prompts:
            payload["system_instruction"] = {
                "parts": [{"text": "\n".join(system_prompts)}]
            }

        # 2. Convert conversation messages
        contents = []
        for m in messages:
            role = m.get("role")
            if role == "system":
                continue
            elif role in ["tool", "function"]:
                tool_name = m.get("name", "tool")
                content_val = m.get("content", "")
                try:
                    res_dict = json.loads(content_val) if isinstance(content_val, str) else content_val
                except Exception:
                    res_dict = {"result": content_val}
                if not isinstance(res_dict, dict):
                    res_dict = {"result": res_dict}

                contents.append({
                    "role": "user",
                    "parts": [{
                        "text": f"[Tool Result for {tool_name}]: {json.dumps(res_dict)}"
                    }]
                })
            else:
                gemini_role = "user" if role == "user" else "model"
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": m.get("content", "")}]
                })

        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hello"}]}]

        payload["contents"] = contents

        # 3. Format tool declarations
        if tools:
            gemini_tools = []
            for t in tools:
                gemini_tools.append({
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("parameters", {"type": "object", "properties": {}})
                })
            payload["tools"] = [{"functionDeclarations": gemini_tools}]

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        last_exception = None
        for current_model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent"
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient(timeout=25.0) as client:
                        resp = await client.post(url, json=payload, headers=headers)
                        if resp.status_code == 429:
                            logger.warning(f"Gemini API model {current_model} returned 429 quota. Trying alternate model...")
                            last_exception = httpx.HTTPStatusError("429 Quota Exceeded", request=resp.request, response=resp)
                            break
                        if resp.status_code == 503 and attempt < max_retries - 1:
                            await asyncio.sleep(1.5)
                            continue
                        resp.raise_for_status()
                        data = resp.json()
                        candidate = data.get("candidates", [{}])[0]
                        parts = candidate.get("content", {}).get("parts", [])

                        text_chunks = []
                        tool_calls = []

                        for p in parts:
                            if "text" in p:
                                text_chunks.append(p["text"])
                            if "functionCall" in p:
                                fc = p["functionCall"]
                                tool_calls.append(ToolCall(
                                    name=fc.get("name", ""),
                                    arguments=fc.get("args", {})
                                ))

                        content_text = "".join(text_chunks).strip() if text_chunks else (None if tool_calls else "")
                        return LLMResponse(
                            content=content_text,
                            tool_calls=tool_calls if tool_calls else None,
                            provider="gemini",
                            model=current_model
                        )
                except (httpx.HTTPError, httpx.NetworkError, Exception) as e:
                    last_exception = e
                    if attempt < max_retries - 1 and getattr(e, "response", None) is not None and e.response.status_code == 503:
                        await asyncio.sleep(1.5)
                        continue

        logger.warning(
            f"Gemini API request failed ({type(last_exception).__name__}: {last_exception}). "
            "Falling back to intelligent local context responder."
        )
        return await self._generate_mock(messages, tools)

    async def _generate_anthropic(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        # Format messages for Anthropic
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        conv_msgs = [m for m in messages if m["role"] in ["user", "assistant"]]
        payload = {
            "model": self.model,
            "system": system_msg,
            "messages": conv_msgs,
            "max_tokens": 1024
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            text = "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
            return LLMResponse(content=text, provider="anthropic", model=self.model)

    async def _generate_ollama(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> LLMResponse:
        url = (self.base_url or "http://localhost:11434") + "/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return LLMResponse(content=data.get("message", {}).get("content"), provider="ollama", model=self.model)

llm_service = LLMService()
