import re
import logging
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel
from backend.app.services.conversation_context_engine import conversation_context_engine

logger = logging.getLogger("SmartGlasses.FollowUpResolver")

class ResolvedFollowUp(BaseModel):
    is_follow_up: bool
    augmented_message: str
    target_capability: Optional[str] = None  # "qa", "gmail", "calendar", "sms", "search", "contact", "calculation"
    action_type: Optional[str] = None        # "read_ordinal", "query_attribute", "reply", "continue_subject", "compare", "mutate"
    resolved_parameters: Dict[str, Any] = {}
    direct_answer: Optional[str] = None

class FollowUpResolver:
    """
    Deterministic Active Referent & Follow-Up Resolver.
    Resolves pronouns, ordinals ('first one', 'second email'), anaphora ('tell me more', 'who sent it'),
    and cross-tool context BEFORE routing to LLM or tool dispatchers.
    """

    def resolve(self, session_id: str, message: str) -> ResolvedFollowUp:
        raw = message.strip()
        q = raw.lower().rstrip("?.,! ")
        ctx = conversation_context_engine.get_session(session_id)

        # 1. Positional / Ordinal selectors: "read the first one", "open the second email", "first event", "email 1"
        ordinal_match = re.search(r"\b(first|second|third|fourth|fifth|1st|2nd|3rd|4th|5th|1|2|3|4|5)\b", q)
        ordinal_map = {
            "first": 1, "1st": 1, "1": 1,
            "second": 2, "2nd": 2, "2": 2,
            "third": 3, "3rd": 3, "3": 3,
            "fourth": 4, "4th": 4, "4": 4,
            "fifth": 5, "5th": 5, "5": 5
        }

        # 1.1 Gmail Ordinal Reading
        if any(w in q for w in ["read", "open", "show", "check", "what is"]) and any(w in q for w in ["first", "second", "third", "1st", "2nd", "3rd", "email 1", "email 2", "mail 1", "mail 2", "one"]):
            if ctx.active_email and ctx.active_email.get("messages"):
                idx_str = ordinal_match.group(1) if ordinal_match else "first"
                idx = ordinal_map.get(idx_str, 1)
                msgs = ctx.active_email["messages"]
                if 1 <= idx <= len(msgs):
                    target_msg = msgs[idx - 1]
                    ctx.active_email["selected"] = target_msg
                    sender = target_msg.get("sender", "Unknown")
                    subject = target_msg.get("subject", "No Subject")
                    snippet = target_msg.get("snippet", "")
                    body = target_msg.get("body") or snippet
                    return ResolvedFollowUp(
                        is_follow_up=True,
                        augmented_message=f"Read email {idx} with id {target_msg.get('id')}",
                        target_capability="gmail",
                        action_type="read_ordinal",
                        resolved_parameters={"index": idx, "message_id": target_msg.get("id"), "email": target_msg},
                        direct_answer=f"Email {idx} from {sender}: '{subject}'. {body}"
                    )

        # 1.2 Calendar Ordinal Reading: "what's the first one?", "first event", "second meeting"
        if any(w in q for w in ["first", "second", "third", "1st", "2nd", "3rd"]) and (any(w in q for w in ["event", "meeting", "schedule", "one"]) or q.startswith("what is the first")):
            if ctx.active_calendar and ctx.active_calendar.get("events"):
                idx_str = ordinal_match.group(1) if ordinal_match else "first"
                idx = ordinal_map.get(idx_str, 1)
                evts = ctx.active_calendar["events"]
                if 1 <= idx <= len(evts):
                    target_evt = evts[idx - 1]
                    ctx.active_calendar["selected"] = target_evt
                    title = target_evt.get("title", "Event")
                    start = target_evt.get("start_time", "Scheduled time")
                    loc = target_evt.get("location", "")
                    loc_str = f" at {loc}" if loc else ""
                    return ResolvedFollowUp(
                        is_follow_up=True,
                        augmented_message=f"Details for calendar event {idx}: {title}",
                        target_capability="calendar",
                        action_type="read_ordinal",
                        resolved_parameters={"index": idx, "event": target_evt},
                        direct_answer=f"Event {idx} is '{title}' at {start}{loc_str}."
                    )

        # 2. Sender & Attribute Questions: "who sent it?", "who is the sender?", "who sent that message?", "who texted?"
        if re.search(r"\b(?:who sent|who is the sender|who messaged|who texted|who wrote|sender)\b", q):
            # Check active SMS
            if ctx.active_sms and (ctx.active_sms.get("selected") or ctx.active_sms.get("messages") or ctx.active_sms.get("contact")):
                contact = ctx.active_sms.get("contact")
                if not contact:
                    selected_sms = ctx.active_sms.get("selected") or ctx.active_sms["messages"][0]
                    contact = selected_sms.get("contactName") or selected_sms.get("address") or "Unknown"
                return ResolvedFollowUp(
                    is_follow_up=True,
                    augmented_message=f"Who sent the active SMS: {contact}",
                    target_capability="sms",
                    action_type="query_attribute",
                    resolved_parameters={"attribute": "sender", "sender": contact},
                    direct_answer=f"That message was sent by {contact}."
                )
            # Check active Gmail
            if ctx.active_email and (ctx.active_email.get("selected") or ctx.active_email.get("messages")):
                selected_email = ctx.active_email.get("selected") or ctx.active_email["messages"][0]
                sender = selected_email.get("sender", "Unknown")
                sender_name = sender.split("<")[0].strip() if "<" in sender else sender
                return ResolvedFollowUp(
                    is_follow_up=True,
                    augmented_message=f"Who sent the active email: {sender}",
                    target_capability="gmail",
                    action_type="query_attribute",
                    resolved_parameters={"attribute": "sender", "sender": sender},
                    direct_answer=f"That email was sent by {sender_name}."
                )


        # 3. Continuation & Elaboration: "tell me more", "explain that", "what about his early life?", "tell me details"
        continuation_patterns = [
            r"^(?:tell me more|more details|explain that|elaborate|continue|tell me the details)\??$",
            r"^(?:what about|tell me about)\s+(?:his|her|their|its)\s+([a-zA-Z0-9\s]+)\??$"
        ]
        if any(re.match(p, q) for p in continuation_patterns) or q in ["tell me more", "explain that", "tell me details"]:
            # Match subtopic if specified ("what about his early life")
            subtopic = None
            m_sub = re.match(r"^(?:what about|tell me about)\s+(?:his|her|their|its)\s+([a-zA-Z0-9\s]+)\??$", q)
            if m_sub:
                subtopic = m_sub.group(1).strip()

            if ctx.active_subject:
                subj = ctx.active_subject
                aug = f"Tell me more about {subj} ({subtopic})" if subtopic else f"Tell me more about {subj}."
                return ResolvedFollowUp(
                    is_follow_up=True,
                    augmented_message=aug,
                    target_capability="qa",
                    action_type="continue_subject",
                    resolved_parameters={"subject": subj, "subtopic": subtopic}
                )
            elif ctx.active_document:
                doc_name = ctx.active_document.get("filename", "document")
                return ResolvedFollowUp(
                    is_follow_up=True,
                    augmented_message=f"Explain more details about the uploaded document {doc_name}.",
                    target_capability="document",
                    action_type="continue_subject",
                    resolved_parameters={"document": ctx.active_document}
                )

        # 4. Search Comparisons: "compare the first two", "compare them"
        if "compare" in q and ("two" in q or "them" in q or "both" in q or "first two" in q):
            if ctx.active_search and len(ctx.active_search.get("results", [])) >= 2:
                res1 = ctx.active_search["results"][0]
                res2 = ctx.active_search["results"][1]
                t1 = res1.get("title", "Option 1")
                t2 = res2.get("title", "Option 2")
                return ResolvedFollowUp(
                    is_follow_up=True,
                    augmented_message=f"Compare search results: 1) {t1} vs 2) {t2}",
                    target_capability="search",
                    action_type="compare",
                    resolved_parameters={"item1": res1, "item2": res2}
                )

        # 5. Search Refinement: "search more", "show more search results"
        if q in ["search more", "more search results", "show more"]:
            if ctx.active_search and ctx.active_search.get("query"):
                sq = ctx.active_search["query"]
                return ResolvedFollowUp(
                    is_follow_up=True,
                    augmented_message=f"Search more results for query: {sq}",
                    target_capability="search",
                    action_type="continue_subject",
                    resolved_parameters={"query": sq}
                )

        # 6. Temporal Calendar Shift: "what about tomorrow?", "what about next week?"
        if q in ["what about tomorrow", "what about tomorrow?", "how about tomorrow", "tomorrow"]:
            return ResolvedFollowUp(
                is_follow_up=True,
                augmented_message="What is on my calendar tomorrow?",
                target_capability="calendar",
                action_type="continue_subject",
                resolved_parameters={"temporal_filter": "tomorrow"}
            )

        # 7. SMS / Email Follow-up Reply: "reply that I'll call later", "reply to it"
        m_reply_sms = re.search(r"^reply\s+(?:to\s+(?:him|her|it|them)\s+)?(?:that\s+)?(.+)$", q)
        if m_reply_sms:
            reply_text = m_reply_sms.group(1).strip()
            # If active SMS is present
            if ctx.active_sms and (ctx.active_sms.get("contact") or ctx.active_sms.get("phone")):
                contact = ctx.active_sms.get("contact") or ctx.active_sms.get("phone")
                phone = ctx.active_sms.get("phone") or ""
                return ResolvedFollowUp(
                    is_follow_up=True,
                    augmented_message=f"Send SMS to {contact}: {reply_text}",
                    target_capability="sms",
                    action_type="reply",
                    resolved_parameters={
                        "recipient": contact,
                        "phone": phone,
                        "body": reply_text,
                        "requires_confirmation": True
                    }
                )
            # If active Email is present
            if ctx.active_email and (ctx.active_email.get("selected") or ctx.active_email.get("thread_id")):
                target_email = ctx.active_email.get("selected") or (ctx.active_email["messages"][0] if ctx.active_email["messages"] else {})
                sender = target_email.get("sender", "Unknown")
                thread_id = target_email.get("thread_id") or target_email.get("id")
                return ResolvedFollowUp(
                    is_follow_up=True,
                    augmented_message=f"Reply to email from {sender} (thread {thread_id}): {reply_text}",
                    target_capability="gmail",
                    action_type="reply",
                    resolved_parameters={
                        "recipient": sender,
                        "thread_id": thread_id,
                        "body": reply_text,
                        "requires_confirmation": True
                    }
                )

        # 8. Contact Action Pronoun Resolution: "call him", "message her", "email him"
        if q in ["call him", "call her", "phone him", "phone her", "call them"]:
            if ctx.active_contact and ctx.active_contact.get("phone"):
                c_name = ctx.active_contact.get("name", "Contact")
                c_phone = ctx.active_contact.get("phone")
                return ResolvedFollowUp(
                    is_follow_up=True,
                    augmented_message=f"Call {c_name} at {c_phone}",
                    target_capability="contact",
                    action_type="mutate",
                    resolved_parameters={"action": "call", "contact": ctx.active_contact, "phone": c_phone}
                )

        return ResolvedFollowUp(
            is_follow_up=False,
            augmented_message=raw
        )

follow_up_resolver = FollowUpResolver()
