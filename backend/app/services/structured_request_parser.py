import re
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field

from backend.app.services.entity_resolver import entity_resolver, ResolutionStatus, Contact

logger = logging.getLogger("SmartGlasses.StructuredRequestParser")

class ParsedIntent(str, Enum):
    # Device & Telephony Controls
    CALL_MAKE = "call_make"
    CALL_ANSWER = "call_answer"
    CALL_REJECT = "call_reject"
    CALL_HANGUP = "call_hangup"
    CALL_INCOMING_QUERY = "call_incoming_query"
    DEVICE_STATE = "device_state"

    # Deterministic Local
    DETERMINISTIC_MATH = "deterministic_math"
    DETERMINISTIC_TIME = "deterministic_time"
    DETERMINISTIC_BATTERY = "deterministic_battery"
    DETERMINISTIC_LOCATION = "deterministic_location"

    # Communication & Messaging
    SMS_SEARCH = "sms_search"
    SMS_READ = "sms_read"
    SMS_SEND = "sms_send"
    SMS_REPLY = "sms_reply"

    # Email
    EMAIL_SEARCH = "email_search"
    EMAIL_READ = "email_read"
    EMAIL_SEND = "email_send"
    EMAIL_REPLY = "email_reply"

    # Calendar
    CALENDAR_QUERY = "calendar_query"
    CALENDAR_FREE_TIME = "calendar_free_time"
    CALENDAR_CREATE = "calendar_create"

    # Search & Information
    WEB_SEARCH = "web_search"
    RESEARCH_SEARCH = "research_search"
    SEARCH_FOLLOW_UP = "search_follow_up"

    # Conversational & Complex
    CONFIRMATION = "confirmation"
    CANCELLATION = "cancellation"
    GENERAL_QA = "general_qa"
    COMPLEX_AGENT = "complex_agent"

class StructuredRequest(BaseModel):
    intent: ParsedIntent
    raw_query: str
    entity: Optional[str] = None
    resolved_contact: Optional[Contact] = None
    topic: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    date_target: Optional[str] = None
    time_target: Optional[str] = None
    is_unread_only: bool = False
    is_read_content: bool = False
    is_follow_up: bool = False
    follow_up_modifier: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0

class StructuredRequestParser:
    """
    Authoritative Request Normalizer:
    - Extracts semantic intent, query slots, entity targets, and temporal parameters.
    - Prevents confusing broad capability with specific user query constraints.
    - Resolves conversational follow-ups and modifier references against session memory.
    """

    def parse(self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> StructuredRequest:
        if not query or not query.strip():
            return StructuredRequest(intent=ParsedIntent.GENERAL_QA, raw_query="", confidence=0.0)

        q_raw = query.strip()
        q = q_raw.lower()
        q_norm = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", q)).strip()

        # 0. Affirmative / Confirmation Intent Check (for 2-Step Safe Action Execution)
        confirm_exact = {
            "yes", "yeah", "yep", "sure", "ok", "okay", "confirm", "proceed", "send", "send it", "do it",
            "yes send it", "yes send", "yes please", "yes proceed", "yes do it", "please send", "please send it",
            "send the email", "send email", "send sms", "send message", "haan", "haanji", "haan bhejo",
            "ho", "kar do", "bhejo", "bhej do", "thik hai"
        }
        if q_norm in confirm_exact or any(phrase in q_norm for phrase in ["send it", "send the email", "send email", "yes please", "yes send", "proceed with"]):
            return StructuredRequest(
                intent=ParsedIntent.CONFIRMATION,
                raw_query=q_raw
            )

        # 0. Cancellation Intent Check
        cancel_exact = {
            "no", "nope", "cancel", "dont send", "dont do it", "stop", "nah", "nahi", "nako", "mat bhejo", "reject", "dont"
        }
        if q_norm in cancel_exact or any(phrase in q_norm for phrase in ["dont send", "dont do", "cancel it", "cancel that", "stop it", "mat bhejo"]):
            return StructuredRequest(
                intent=ParsedIntent.CANCELLATION,
                raw_query=q_raw
            )

        # 1. Device & Call Controls (Highest Priority - Section 14, 15, 16)
        call_req = self._parse_call_intent(q_raw, q)
        if call_req:
            return call_req

        # 2. Deterministic Math Check (Section 24)
        math_req = self._parse_math_intent(q_raw, q)
        if math_req:
            return math_req

        # 3. Deterministic Time/Battery/Location Check
        det_req = self._parse_device_context_intent(q_raw, q)
        if det_req:
            return det_req

        # 4. SMS Queries (Section 17, 18, 19)
        sms_req = self._parse_sms_intent(q_raw, q)
        if sms_req:
            return sms_req

        # 5. Gmail Queries (Section 3, 4, 5, 6)
        email_req = self._parse_email_intent(q_raw, q, conversation_history)
        if email_req:
            return email_req

        # 6. Calendar Queries & Follow-ups (Section 7, 8, 9, 10)
        cal_req = self._parse_calendar_intent(q_raw, q, conversation_history)
        if cal_req:
            return cal_req

        # 7. Academic Research / arXiv Search
        research_req = self._parse_research_intent(q_raw, q)
        if research_req:
            return research_req

        # 8. Web Search & Contextual Follow-up (Section 20, 21, 22)
        search_req = self._parse_search_intent(q_raw, q, conversation_history)
        if search_req:
            return search_req

        # 9. General Single-Turn QA / Conversational
        return StructuredRequest(
            intent=ParsedIntent.GENERAL_QA,
            raw_query=q_raw,
            confidence=0.8
        )

    def _parse_call_intent(self, q_raw: str, q: str) -> Optional[StructuredRequest]:
        # Answering incoming call
        if any(kw in q for kw in ["answer the call", "answer call", "pick up the call", "pick up call", "accept call", "receive call"]):
            return StructuredRequest(intent=ParsedIntent.CALL_ANSWER, raw_query=q_raw)

        # Rejecting incoming call
        if any(kw in q for kw in ["reject the call", "reject call", "decline call", "decline the call", "ignore call"]):
            return StructuredRequest(intent=ParsedIntent.CALL_REJECT, raw_query=q_raw)

        # Ending active call
        if any(kw in q for kw in ["hang up", "end the call", "end call", "disconnect call", "cut the call", "stop call"]):
            return StructuredRequest(intent=ParsedIntent.CALL_HANGUP, raw_query=q_raw)

        # Querying incoming caller identity
        if any(kw in q for kw in ["who is calling", "who's calling", "whose call is this", "caller name", "who is on the line"]):
            return StructuredRequest(intent=ParsedIntent.CALL_INCOMING_QUERY, raw_query=q_raw)

        # Making a phone call: "call [name]" or "phone [name]" or "dial [name]"
        call_patterns = [
            r"^(?:call|phone|dial|ring|make a call to)\s+([a-zA-Z0-9\s]+?)(?:\s+please|\s+now)?$",
            r"^(?:please\s+)?(?:call|phone|dial)\s+([a-zA-Z0-9\s]+)$"
        ]
        for pat in call_patterns:
            m = re.match(pat, q, re.IGNORECASE)
            if m:
                target = m.group(1).strip()
                # Clean filler words
                target_clean = re.sub(r"^(?:my|the|to)\s+", "", target).strip()
                res = entity_resolver.resolve_contact(target_clean)
                contact = res.contact if res.status == ResolutionStatus.RESOLVED else None
                return StructuredRequest(
                    intent=ParsedIntent.CALL_MAKE,
                    raw_query=q_raw,
                    entity=target_clean,
                    resolved_contact=contact,
                    parameters={
                        "resolution_status": res.status.value,
                        "clarification_prompt": res.clarification_prompt,
                        "candidates": [c.model_dump() for c in res.candidates]
                    }
                )

        return None

    def _parse_math_intent(self, q_raw: str, q: str) -> Optional[StructuredRequest]:
        # Exclude coding, programming, Python, building, and script queries
        if any(w in q for w in ["python", "code", "script", "program", "app", "write a", "build", "create a", "how to"]):
            return None

        # Quick math regex check
        math_symbols = ["+", "-", "*", "/", "x", "^", "%", "times", "plus", "minus", "divided by", "multiplied by", "calculate", "what is", "solve"]
        has_symbol = any(s in q for s in ["+", "*", "/", "divided by", "times", "multiplied by", "plus", "minus"])
        has_digit = any(c.isdigit() for c in q)

        if has_digit and (has_symbol or "calculate" in q or "evaluate" in q or ("what is" in q and any(c.isdigit() for c in q))):
            # Check if it doesn't contain heavy semantic non-math words
            if not any(w in q for w in ["email", "calendar", "event", "sms", "call", "search", "recipe", "cook", "tie", "shoe", "weather", "car", "shop", "trip"]):
                return StructuredRequest(
                    intent=ParsedIntent.DETERMINISTIC_MATH,
                    raw_query=q_raw
                )
        return None

    def _parse_device_context_intent(self, q_raw: str, q: str) -> Optional[StructuredRequest]:
        if any(kw in q for kw in ["what time is it", "what's the time", "current time", "tell me the time", "samay kya", "kitne baje"]):
            return StructuredRequest(intent=ParsedIntent.DETERMINISTIC_TIME, raw_query=q_raw)
        if any(kw in q for kw in ["what's my battery", "battery percentage", "battery status", "battery level", "how much battery"]):
            return StructuredRequest(intent=ParsedIntent.DETERMINISTIC_BATTERY, raw_query=q_raw)
        if any(kw in q for kw in ["where am i", "current location", "what city is this", "my location"]):
            return StructuredRequest(intent=ParsedIntent.DETERMINISTIC_LOCATION, raw_query=q_raw)
        return None

    def _parse_sms_intent(self, q_raw: str, q: str) -> Optional[StructuredRequest]:
        sms_keywords = ["sms", "text message", "text messages", "messages", "texts", "मैसेज", "मेसेज", "एसएमएस"]
        is_sms_context = any(kw in q for kw in sms_keywords)

        # SMS Send: "Send [Name] a message saying [text]" or "Text [Name] [text]"
        send_patterns = [
            r"^(?:send\s+an?\s+sms\s+to|send\s+a?\s*text\s+to|send\s+sms\s+to|send\s+message\s+to|text\s+to|text)\s+([a-zA-Z\s]+?)\s+(?:saying|that|:)\s+(.+)$",
            r"^(?:send\s+)([a-zA-Z\s]+?)\s+(?:a\s+message\s+saying|a\s+text\s+saying|message|text|that|:)\s+(.+)$",
            r"^(?:tell\s+)([a-zA-Z\s]+?)\s+(?:that|saying|:)\s+(.+)$"
        ]
        for pat in send_patterns:
            m = re.match(pat, q, re.IGNORECASE)
            if m:
                person = m.group(1).strip()
                body = m.group(2).strip()
                res = entity_resolver.resolve_contact(person)
                contact = res.contact if res.status == ResolutionStatus.RESOLVED else None
                return StructuredRequest(
                    intent=ParsedIntent.SMS_SEND,
                    raw_query=q_raw,
                    recipient=person,
                    resolved_contact=contact,
                    parameters={
                        "body": body,
                        "resolution_status": res.status.value,
                        "clarification_prompt": res.clarification_prompt
                    }
                )

        # SMS Reply: "Reply to Rahul [text]" or "Reply to that message [text]"
        if q.startswith("reply to"):
            body = q_raw
            return StructuredRequest(
                intent=ParsedIntent.SMS_REPLY,
                raw_query=q_raw,
                parameters={"body": body}
            )

        # SMS Query / Search: "Did Rahul message me?" or "What did Rahul say?" or "Read SMS from Rahul"
        contact_sms_patterns = [
            r"^(?:did|has)\s+([a-zA-Z\s]+?)\s+(?:message|text|sms|send\s+me|write)\b",
            r"^what\s+did\s+([a-zA-Z\s]+?)\s+(?:say|text|message|send)\b",
            r"^(?:read|check|show|get)\s+(?:the\s+)?(?:latest\s+)?(?:sms|text|message|messages)\s+(?:from|by)\s+([a-zA-Z\s]+)$",
            r"^(?:check\s+messages\s+from|read\s+messages\s+from)\s+([a-zA-Z\s]+)$"
        ]
        for pat in contact_sms_patterns:
            m = re.search(pat, q, re.IGNORECASE)
            if m:
                person = m.group(1).strip()
                res = entity_resolver.resolve_contact(person)
                return StructuredRequest(
                    intent=ParsedIntent.SMS_SEARCH,
                    raw_query=q_raw,
                    sender=person,
                    resolved_contact=res.contact if res.status == ResolutionStatus.RESOLVED else None,
                    parameters={"resolution_status": res.status.value}
                )

        # Read latest SMS
        if is_sms_context:
            return StructuredRequest(
                intent=ParsedIntent.SMS_READ,
                raw_query=q_raw,
                is_read_content="read" in q or "say" in q or "what did" in q
            )

        return None

    def _parse_email_intent(self, q_raw: str, q: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[StructuredRequest]:
        email_keywords = ["email", "emails", "gmail", "inbox", "mail", "mails", "ईमेल", "इमेल", "मेल"]
        has_email_word = any(kw in q for kw in email_keywords)

        # Sending / Composing email: "Send email to [recipient]..."
        if any(kw in q for kw in ["send email", "send an email", "compose email", "email to", "send mail", "send a mail", "mail to"]):
            recipient = ""
            subject = "Update"
            body = q_raw

            m_to = re.search(r"(?:to|unto)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[a-zA-Z\s]+?)(?:\s+saying|\s+about|\s+with|\s+that|$)", q_raw, re.IGNORECASE)
            if m_to:
                recipient = m_to.group(1).strip()

            m_say = re.search(r"(?:saying|that|body is|message is)\s+(.+)$", q_raw, re.IGNORECASE)
            if m_say:
                body = m_say.group(1).strip()

            return StructuredRequest(
                intent=ParsedIntent.EMAIL_SEND,
                raw_query=q_raw,
                recipient=recipient,
                parameters={"subject": subject, "body": body}
            )

        # Follow-up email reading: "Read the latest one", "Read the internship email", "Read the reply", "Read the first one"
        if ("read" in q or "open" in q or "tell me what it says" in q or "say it" in q) and not any(kw in q for kw in ["sms", "text", "calendar", "message"]):
            is_prev_email = False
            if history:
                for h in reversed(history[-4:]):
                    if any(kw in h.get("content", "").lower() for kw in email_keywords):
                        is_prev_email = True
                        break
            ordinal_match = re.search(r"\b(first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|last|latest)\b", q)
            if is_prev_email or has_email_word or ordinal_match or any(k in q for k in ["linkedin", "internship", "college", "professor"]):
                idx = 1
                if ordinal_match:
                    ord_word = ordinal_match.group(1).lower()
                    if ord_word in ["first", "1st"]:
                        idx = 1
                    elif ord_word in ["second", "2nd"]:
                        idx = 2
                    elif ord_word in ["third", "3rd"]:
                        idx = 3
                    elif ord_word in ["fourth", "4th"]:
                        idx = 4
                    elif ord_word in ["fifth", "5th"]:
                        idx = 5
                # Extract entity / topic if specified in read command
                topic = None
                for t in ["internship", "project", "exam", "fees", "ticket", "interview", "admission", "seminar", "flight", "booking"]:
                    if t in q:
                        topic = t
                        break
                sender = None
                for s in ["linkedin", "github", "amazon", "google", "swiggy", "zomato", "college", "professor", "university", "internshala", "iit", "angel one"]:
                    if s in q:
                        sender = s
                        break
                return StructuredRequest(
                    intent=ParsedIntent.EMAIL_READ,
                    raw_query=q_raw,
                    topic=topic,
                    sender=sender,
                    is_read_content=True,
                    is_follow_up=is_prev_email,
                    parameters={"index": idx}
                )

        if has_email_word or any(ent in q for ent in ["linkedin", "github", "amazon", "swiggy", "zomato", "internshala", "angel one"]):
            is_unread = any(w in q for w in ["unread", "new", "recent", "latest"])
            # Extract topic & sender filters (Section 3, 4, 5)
            topic = None
            sender = None
            date_filter = None

            # 1. Topic extraction
            topic_match = re.search(r"(?:related to|about|regarding|concerning|mentioning|topic|for)\s+([a-zA-Z0-9\s]+?)(?:\s+emails?|\s+mails?|\s+from|\s+this|\s+last|$)", q, re.IGNORECASE)
            if topic_match:
                topic = topic_match.group(1).strip()
            else:
                for t in ["internship", "internships", "project", "projects", "exam", "exams", "fees", "ticket", "tickets", "interview", "interviews", "admission", "seminar", "placement", "placements", "salary", "invoice", "receipt", "hackathon"]:
                    if t in q:
                        topic = t
                        break

            # 2. Sender / Company entity extraction
            for s in ["linkedin", "github", "amazon", "google", "swiggy", "zomato", "college", "professor", "university", "internshala", "iit", "angel one", "rahul", "sneha", "amit", "priya", "apple", "microsoft", "uber", "netflix", "twitter"]:
                if s in q:
                    sender = s
                    break

            # 3. Temporal filters
            if "this week" in q:
                date_filter = "this_week"
            elif "last week" in q:
                date_filter = "last_week"
            elif "this month" in q:
                date_filter = "this_month"
            elif "last month" in q:
                date_filter = "last_month"
            elif "today" in q:
                date_filter = "today"
            elif "yesterday" in q:
                date_filter = "yesterday"

            # Clean topic of filler keywords if matched
            if topic:
                topic = re.sub(r"\b(?:my|the|an|a|only|emails?|mails?|inbox)\b", "", topic).strip()

            filters = {}
            if topic:
                filters["topic"] = topic
            if sender:
                filters["sender"] = sender
            if is_unread:
                filters["is_unread"] = True
            if date_filter:
                filters["date"] = date_filter

            return StructuredRequest(
                intent=ParsedIntent.EMAIL_SEARCH,
                raw_query=q_raw,
                topic=topic,
                sender=sender,
                is_unread_only=is_unread,
                filters=filters
            )

        return None

    def _parse_calendar_intent(self, q_raw: str, q: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[StructuredRequest]:
        cal_keywords = ["calendar", "event", "events", "schedule", "meeting", "meetings", "appointment", "class", "classes", "agenda", "free time", "कॅलेंडर", "इवेंट", "कार्यक्रम"]
        has_cal_word = any(kw in q for kw in cal_keywords)

        # Planning / Creating event: "Schedule a meeting...", "Create an event..."
        if any(kw in q for kw in ["schedule a", "schedule an", "create event", "create an event", "add event", "book a", "book an", "set meeting", "plan a", "plan an"]):
            return StructuredRequest(
                intent=ParsedIntent.CALENDAR_CREATE,
                raw_query=q_raw,
                parameters={"raw": q_raw}
            )

        # Free time query
        if "free" in q and (has_cal_word or "when am i" in q or "free time" in q):
            return StructuredRequest(
                intent=ParsedIntent.CALENDAR_FREE_TIME,
                raw_query=q_raw,
                date_target="today" if "today" in q or "tomorrow" not in q else "tomorrow"
            )

        # Multi-turn Follow-up: "What about tomorrow?", "What about Tuesday?", "What about next week?"
        if q.startswith("what about") or q.startswith("and tomorrow") or q.startswith("how about") or q.startswith("what of"):
            is_prev_calendar = False
            if history:
                for h in reversed(history[-4:]):
                    if any(kw in h.get("content", "").lower() for kw in cal_keywords) or "event" in h.get("content", "").lower():
                        is_prev_calendar = True
                        break
            if is_prev_calendar or has_cal_word:
                target_date = self._extract_date_target(q)
                return StructuredRequest(
                    intent=ParsedIntent.CALENDAR_QUERY,
                    raw_query=q_raw,
                    date_target=target_date,
                    is_follow_up=True
                )

        # Direct Calendar query: "What do I have tomorrow?", "What is on my calendar today?"
        if has_cal_word or (("what do i have" in q or "what is on my" in q or "whats on" in q or "do i have anything" in q or "my schedule" in q or "first event" in q or "next event" in q) and not any(kw in q for kw in ["email", "mail", "sms", "text"])):
            target_date = self._extract_date_target(q)
            return StructuredRequest(
                intent=ParsedIntent.CALENDAR_QUERY,
                raw_query=q_raw,
                date_target=target_date
            )

        return None

    def _extract_date_target(self, q: str) -> str:
        if "tomorrow" in q:
            return "tomorrow"
        elif "yesterday" in q:
            return "yesterday"
        elif "this evening" in q or "tonight" in q:
            return "tonight"
        elif "next week" in q:
            return "next_week"
        elif "this week" in q:
            return "this_week"
        elif "next monday" in q:
            return "next_monday"
        elif "monday" in q:
            return "monday"
        elif "tuesday" in q:
            return "tuesday"
        elif "wednesday" in q:
            return "wednesday"
        elif "thursday" in q:
            return "thursday"
        elif "friday" in q:
            return "friday"
        elif "saturday" in q:
            return "saturday"
        elif "sunday" in q:
            return "sunday"
        elif "next event" in q or "upcoming" in q or "first event" in q:
            return "upcoming"
        return "today"

    def _parse_research_intent(self, q_raw: str, q: str) -> Optional[StructuredRequest]:
        research_triggers = [
            "search arxiv", "arxiv", "find research papers", "scientific papers", "academic papers",
            "research papers on", "research papers about", "research paper", "search papers on", "search papers about",
            "find papers on", "find papers about", "papers on", "papers about", "paper on", "paper about",
            "research on", "literature on", "literature review on", "semantic scholar", "google scholar", "scholar search",
            "research engine", "eva research"
        ]
        if any(t in q for t in research_triggers):
            clean_topic = q_raw
            for t in [
                "search arxiv for", "search arxiv on", "find research papers on", "find research papers about",
                "find papers on", "find papers about", "academic papers on", "academic papers about",
                "research papers on", "research papers about", "research paper on", "research paper about",
                "search papers on", "search papers about", "papers on", "papers about", "paper on", "paper about",
                "research on", "literature on", "literature review on", "semantic scholar", "google scholar", "arxiv",
                "research engine", "eva research"
            ]:
                if t in q:
                    idx = q.find(t)
                    clean_topic = q_raw[idx + len(t):].strip(" ?:.,")
                    break
            return StructuredRequest(
                intent=ParsedIntent.RESEARCH_SEARCH,
                raw_query=q_raw,
                topic=clean_topic or q_raw
            )
        return None

    def _parse_search_intent(self, q_raw: str, q: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[StructuredRequest]:
        search_triggers = [
            "search web for", "search the web for", "search web", "search for", "look up", "google search for",
            "search", "find", "what is the latest", "what's the latest", "latest news on", "news about",
            "best car", "which car is best", "laptop under", "smartwatch under", "internships in",
            "pet shop", "pet store", "best pet", "kaha hai", "kahan hai", "kidhar hai", "kaha milega",
            "best restaurant", "best shop", "best store", "best hospital", "near me", "in nagpur",
            "places in", "hotels in", "top 5", "top 10", "recommend"
        ]

        # Follow-up search modifier: "Only Bangalore", "Only in Bangalore", "Which pays the most?", "Which one is cheapest?"
        if history:
            is_prev_search = False
            for h in reversed(history[-3:]):
                if any(st in h.get("content", "").lower() for st in ["found", "options", "result", "search", "internship", "laptop", "car", "shop", "place"]):
                    is_prev_search = True
                    break
            if is_prev_search:
                if q.startswith("only ") or q.startswith("just ") or "which pays" in q or "which one" in q or "which is best" in q or "show more" in q:
                    return StructuredRequest(
                        intent=ParsedIntent.SEARCH_FOLLOW_UP,
                        raw_query=q_raw,
                        is_follow_up=True,
                        follow_up_modifier=q_raw
                    )

        # Match direct search or local discovery / recommendations queries
        if any(trig in q for trig in [
            "search web", "search the web", "look up", "google search", "latest news",
            "pet shop", "pet store", "kaha hai", "kahan hai", "kaha milega", "kidhar hai",
            "best shop", "best store", "best restaurant", "best hospital", "near me",
            "internships in", "which car", "laptop under", "smartwatch under", "tourist spots",
            "places to visit", "top 5", "top 10"
        ]):
            clean_query = q_raw
            for trig in ["search web for", "search the web for", "look up on web", "google search for", "search for", "look up"]:
                if trig in q:
                    idx = q.find(trig)
                    clean_query = q_raw[idx + len(trig):].strip(" ?:.,")
                    break
            return StructuredRequest(
                intent=ParsedIntent.WEB_SEARCH,
                raw_query=q_raw,
                topic=clean_query or q_raw
            )

        return None

structured_request_parser = StructuredRequestParser()
