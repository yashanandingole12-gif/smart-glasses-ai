import json
import logging
import asyncio
import time
import httpx
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel
from backend.app.config import settings

logger = logging.getLogger("SmartGlasses.LLMService")

from enum import Enum

class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class GeminiCircuitBreaker:
    def __init__(self, cooldown_seconds: float = 60.0):
        self.cooldown = cooldown_seconds
        self.state = CircuitState.CLOSED
        self.opened_at: float = 0.0
        self.discovered_model: Optional[str] = None
        self._discovery_attempted = False
        self._invalid_models: Set[str] = set()

    def is_available(self) -> bool:
        if self.state == CircuitState.OPEN:
            if time.time() - self.opened_at > self.cooldown:
                self.state = CircuitState.HALF_OPEN
                logger.info("Gemini circuit transitioned OPEN -> HALF_OPEN (probing recovery).")
                return True
            return False
        return True

    def record_success(self, model: str):
        if self.state != CircuitState.CLOSED:
            logger.info("Gemini probe succeeded! Circuit transitioned to CLOSED.")
        self.state = CircuitState.CLOSED
        self.discovered_model = model

    def record_429(self):
        self.state = CircuitState.OPEN
        self.opened_at = time.time()
        logger.warning("Gemini 429 Quota Exceeded. Circuit OPEN for %ds cooldown.", int(self.cooldown))

    def record_404(self, model: str):
        self._invalid_models.add(model)
        logger.warning("Marked Gemini model '%s' as INVALID (404 Not Found).", model)

gemini_circuit_breaker = GeminiCircuitBreaker(cooldown_seconds=60.0)

async def discover_valid_gemini_model(api_key: str) -> Optional[str]:
    """Discover available generateContent models on Google AI Studio for the configured API key."""
    if not api_key:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "").replace("models/", "") for m in data.get("models", [])]
                gen_models = [m for m in models if "flash" in m or "pro" in m]
                for preferred in ["gemini-2.0-flash", "gemini-1.5-flash-latest", "gemini-flash-latest", "gemini-1.5-flash", "gemini-pro"]:
                    if preferred in gen_models:
                        logger.info("Gemini Model Discovery: Selected '%s' from %d available models.", preferred, len(gen_models))
                        return preferred
                if gen_models:
                    logger.info("Gemini Model Discovery: Selected '%s'", gen_models[0])
                    return gen_models[0]
    except Exception as e:
        logger.debug("Gemini model discovery skipped/failed: %s", e)
    return None

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

            # Format tool response with multilingual awareness
            if "unread_count" in str(data):
                unread = data.get("unread_count", 1) if isinstance(data, dict) else 1
                sender = data['messages'][0]['sender'] if isinstance(data, dict) and data.get('messages') else 'college admin'
                if any(h in last_user_msg for h in ["ईमेल", "चेक", "करो", "संदेश"]):
                    return LLMResponse(
                        content=f"आपके पास {unread} अपठित ईमेल हैं। नवीनतम ईमेल {sender} से है।",
                        provider="mock",
                        model=self.model
                    )
                elif any(m in last_user_msg for m in ["तपासा", "वाचा"]):
                    return LLMResponse(
                        content=f"तुमच्याकडे {unread} न वाचलेले ईमेल आहेत. नवीनतम ईमेल {sender} कडून आहे.",
                        provider="mock",
                        model=self.model
                    )
                elif "mere" in msg_lower or "batao" in msg_lower or "karo" in msg_lower:
                    return LLMResponse(
                        content=f"Aapke paas {unread} unread emails hain. Latest email {sender} se aaya hai.",
                        provider="mock",
                        model=self.model
                    )
                return LLMResponse(
                    content=f"You have {unread} unread emails. The latest is from {sender}.",
                    provider="mock",
                    model=self.model
                )
            elif "error" in str(data).lower() or "unauthorized" in str(data).lower() or "unauthenticated" in str(data).lower() or "401" in str(data):
                if any(h in last_user_msg for h in ["ईमेल", "चेक", "करो"]):
                    return LLMResponse(
                        content="आपका Gmail खाता अभी कनेक्ट नहीं है। कृपया ऐप से Google लॉगिन करें।",
                        provider="mock",
                        model=self.model
                    )
                elif any(m in last_user_msg for m in ["तपासा", "वाचा"]):
                    return LLMResponse(
                        content="तुमचे Gmail खाते सध्या कनेक्ट केलेले नाही. कृपया ॲपवरून Google लॉगिन करा.",
                        provider="mock",
                        model=self.model
                    )
                elif "mere" in msg_lower or "batao" in msg_lower or "karo" in msg_lower:
                    return LLMResponse(
                        content="Aapka Gmail account abhi connected nahi hai. Please Google login check karein.",
                        provider="mock",
                        model=self.model
                    )
                return LLMResponse(
                    content="Your Gmail account is not connected. Please sign in with Google in the mobile app.",
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
                events_list = data.get("events", []) if isinstance(data, dict) else []
                if not events_list:
                    return LLMResponse(
                        content="I don't see any events scheduled for today.",
                        provider="mock",
                        model=self.model
                    )
                next_ev = data.get("next_event", {}) if isinstance(data, dict) else {}
                title = next_ev.get("title", "Class")
                t = next_ev.get("start_time", "10:30 AM")
                return LLMResponse(
                    content=f"Your next event is {title} at {t}.",
                    provider="mock",
                    model=self.model
                )
            else:
                return LLMResponse(
                    content="I checked your request and processed the details.",
                    provider="mock",
                    model=self.model
                )

        # Multilingual context extraction
        time_str = "8:15 AM"
        city = "Nagpur"
        has_events = False
        next_ev_str = None
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
                has_events = True
            elif cal_info.get("today_events"):
                has_events = True

        # 1. Hindi Greeting & Query Support
        if any(h in last_user_msg for h in ["सुप्रभात", "नमस्ते", "शुभ प्रभात", "शुभ दोपहर", "शुभ संध्या"]):
            cal_phrase = f"आपकी अगली क्लास {next_ev_str} पर है।" if has_events else "आज आपके कैलेंडर में कोई इवेंट रिकॉर्ड नहीं है।"
            return LLMResponse(
                content=f"सुप्रभात! अभी {time_str} बजे हैं और आप {city} में हैं। {cal_phrase} मैं आपकी क्या मदद कर सकता हूँ?",
                provider="mock",
                model=self.model
            )

        # 2. Marathi Greeting & Query Support
        if any(m in last_user_msg for m in ["शुभ सकाळ", "नमस्कार", "शुभ दुपार", "शुभ संध्याकाळ"]):
            cal_phrase = f"तुमचा पुढचा क्लास {next_ev_str} वाजता आहे." if has_events else "आज तुमच्या कॅलेंडरमध्ये कोणतेही कार्यक्रम शेड्यूल केलेले नाहीत."
            return LLMResponse(
                content=f"शुभ सकाळ! आता सकाळचे {time_str} झाले आहेत आणि तुम्ही {city}मध्ये आहात. {cal_phrase} मी काय मदत करू शकतो?",
                provider="mock",
                model=self.model
            )

        # 3. Hinglish Greeting & Calendar Query Support
        if ("aaj" in msg_lower and "calendar" in msg_lower) or ("mera calendar" in msg_lower) or ("good morning" in msg_lower and ("aaj" in msg_lower or "karo" in msg_lower or "check" in msg_lower)):
            cal_phrase = f"Aapki next class {next_ev_str} hai." if has_events else "Aaj aapke calendar mein koi events scheduled nahi hain."
            return LLMResponse(
                content=f"Good morning! Aaj {time_str} par aap {city} mein hain. {cal_phrase}",
                provider="mock",
                model=self.model
            )

        # 4. Standard English Context-aware greetings
        if any(g in msg_lower for g in ["good morning", "morning", "good afternoon", "good evening", "good night", "hello", "hi"]):
            greeting = f"Good {period}" if period != "night" else "Good evening"
            loc_phrase = f"You're currently near {city}." if city not in ["Unavailable", "Unknown"] else ""
            if has_events and next_ev_str:
                cal_phrase = f"You have {next_ev_str}."
            else:
                cal_phrase = "You have no upcoming calendar events recorded for today."
            
            content = f"{greeting}. {loc_phrase} {cal_phrase} How can I help?".replace("  ", " ").strip()
            return LLMResponse(content=content, provider="mock", model=self.model)

        has_email_context = any("email" in m.get("content", "").lower() or "mail" in m.get("content", "").lower() for m in messages)
        has_cal_context = any("calendar" in m.get("content", "").lower() or "event" in m.get("content", "").lower() or "class" in m.get("content", "").lower() for m in messages)

        # Tool triggering heuristics for mock mode (Multilingual: English, Hindi, Marathi, Hinglish)
        is_email_query = (
            "email" in msg_lower or "mail" in msg_lower or
            "ईमेल" in last_user_msg or "तपासा" in last_user_msg or
            ("चेक" in last_user_msg and "करो" in last_user_msg) or
            (has_email_context and ("read" in msg_lower or "padho" in msg_lower or "वाचा" in last_user_msg))
        )
        if is_email_query:
            if "read" in msg_lower or "first" in msg_lower or "second" in msg_lower or "third" in msg_lower or "वाचा" in last_user_msg or "पढ़ो" in last_user_msg:
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
            content="I am listening on your smart glasses.",
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
            "messages": messages,
            "max_tokens": 120,
            "temperature": 0.2
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
        if not gemini_circuit_breaker.is_available():
            logger.info("Gemini Circuit is OPEN (429 Rate Limit Cooldown). Bypassing cloud probes directly in 0ms.")
            return await self._generate_mock(messages, tools)

        # 1. Dynamic Discovery check if not yet performed
        if not gemini_circuit_breaker._discovery_attempted and self.api_key:
            gemini_circuit_breaker._discovery_attempted = True
            discovered = await discover_valid_gemini_model(self.api_key)
            if discovered:
                gemini_circuit_breaker.discovered_model = discovered

        primary_model = gemini_circuit_breaker.discovered_model or self.model or "gemini-flash-latest"

        candidate_models = [
            primary_model,
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-pro"
        ]
        models_to_try = [m for m in candidate_models if m and m not in gemini_circuit_breaker._invalid_models]
        if not models_to_try:
            gemini_circuit_breaker._invalid_models.clear()
            models_to_try = [primary_model]

        # 2. Extract system instructions
        system_prompts = [m["content"] for m in messages if m.get("role") == "system"]
        payload: Dict[str, Any] = {}
        if system_prompts:
            payload["system_instruction"] = {
                "parts": [{"text": "\n".join(system_prompts)}]
            }

        # 3. Convert conversation messages
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

        # 4. Format tool declarations
        if tools:
            gemini_tools = []
            for t in tools:
                gemini_tools.append({
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("parameters", {"type": "object", "properties": {}})
                })
            payload["tools"] = [{"functionDeclarations": gemini_tools}]

        # 5. Wearable Ultra-Low-Latency Constraints (Cap tokens to 120 for instant response)
        payload["generationConfig"] = {
            "maxOutputTokens": 120,
            "temperature": 0.2,
            "topP": 0.8
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        last_exception = None
        for current_model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent"
            hit_rate_limit = False
            try:
                async with httpx.AsyncClient(timeout=2.5) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 429:
                        gemini_circuit_breaker.record_429()
                        last_exception = httpx.HTTPStatusError("429 Quota Exceeded", request=resp.request, response=resp)
                        hit_rate_limit = True
                        break
                    if resp.status_code == 404:
                        gemini_circuit_breaker.record_404(current_model)
                        last_exception = httpx.HTTPStatusError("404 Model Not Found", request=resp.request, response=resp)
                        continue
                    if resp.status_code == 400:
                        gemini_circuit_breaker.record_404(current_model)
                        last_exception = httpx.HTTPStatusError("400 Bad Request", request=resp.request, response=resp)
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
                    gemini_circuit_breaker.record_success(current_model)
                    return LLMResponse(
                        content=content_text,
                        tool_calls=tool_calls if tool_calls else None,
                        provider="gemini",
                        model=current_model
                    )
            except (httpx.HTTPError, httpx.NetworkError, Exception) as e:
                last_exception = e
                if getattr(e, "response", None) is not None and e.response.status_code == 429:
                    gemini_circuit_breaker.record_429()
                    break

            if hit_rate_limit:
                break

        logger.warning(
            f"Gemini API request failed across all models ({type(last_exception).__name__}: {last_exception}). "
            "Gracefully falling back to intelligent on-device mock generator."
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
