import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("SmartGlasses.SmartGlassFormatter")

class SmartGlassResponseFormatter:
    """
    Standardized response formatter for smart glasses wearables.
    Rules:
    1. 1 to 3 sentences max.
    2. Speakable text (no markdown formatting, no unpronounceable symbols, no raw URLs).
    3. Grounded in actual tool/context results without hallucination.
    4. Max 5 items for lists.
    5. Clean Hindi / Marathi / English phrasing.
    """

    @staticmethod
    def clean_text_for_speech(text: str) -> str:
        """Removes markdown symbols, URLs, excess punctuation, and formatting."""
        if not text:
            return ""
        # Remove URLs
        cleaned = re.sub(r"https?://\S+", "", text)
        # Remove markdown bold/italics/code/bullets
        cleaned = re.sub(r"[\*\_`#>]", "", cleaned)
        cleaned = re.sub(r"^\s*[-•\d+\.]+\s+", "", cleaned, flags=re.MULTILINE)
        # Collapse whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def format_email_search(self, results: List[Dict[str, Any]], query_topic: Optional[str] = None, sender: Optional[str] = None, unread_only: bool = False, language: str = "auto", raw_query: str = "") -> str:
        is_hi = language == "hi" or any("\u0900" <= c <= "\u097f" for c in raw_query)
        is_mr = language == "mr"

        if not results:
            if is_hi:
                if query_topic:
                    return f"मुझे {query_topic} से संबंधित कोई ईमेल नहीं मिला।"
                elif sender:
                    return f"मुझे {sender} से कोई ईमेल नहीं मिला।"
                return "आपके इनबॉक्स में कोई नया ईमेल नहीं है।" if unread_only else "आपके इनबॉक्स में कोई ईमेल नहीं है।"
            elif is_mr:
                if query_topic:
                    return f"मला {query_topic} बद्दल कोणताही ईमेल सापडला नाही."
                elif sender:
                    return f"मला {sender} कडून कोणताही ईमेल सापडला नाही."
                return "तुमच्या इनबॉक्समध्ये कोणतेही नवीन ईमेल नाहीत." if unread_only else "तुमच्या इनबॉक्समध्ये कोणतेही ईमेल नाहीत."

            if query_topic and sender:
                return f"I couldn't find any emails from {sender} about {query_topic}."
            elif query_topic:
                return f"I couldn't find any emails related to {query_topic}."
            elif sender:
                return f"I couldn't find any emails from {sender}."
            return "You have no unread emails." if unread_only else "You have no emails in your inbox."

        count = len(results)
        first = results[0]
        first_sender = first.get("sender", "Unknown")
        first_sender_name = first_sender.split("<")[0].strip() if "<" in first_sender else first_sender
        first_subject = first.get("subject", "No Subject")
        first_snippet = self.clean_text_for_speech(first.get("snippet", ""))

        if is_hi:
            if query_topic:
                return f"आपके पास {query_topic} के बारे में {count} ईमेल हैं। नवीनतम ईमेल {first_sender_name} से है: '{first_subject}'।"
            if count == 1:
                return f"आपके पास {first_sender_name} से 1 ईमेल है: '{first_subject}'।"
            return f"आपके पास {count} ईमेल हैं। नवीनतम {first_sender_name} से: '{first_subject}'।"

        if is_mr:
            if query_topic:
                return f"तुमच्याकडे {query_topic} बद्दल {count} ईमेल आहेत. नवीनतम ईमेल {first_sender_name} कडून आहे: '{first_subject}'."
            return f"तुमच्याकडे {count} ईमेल आहेत. नवीनतम {first_sender_name} कडून: '{first_subject}'."

        if query_topic:
            if count == 1:
                return f"You have 1 email about {query_topic} from {first_sender_name} with subject '{first_subject}'."
            return f"You have {count} emails about {query_topic}. The latest is from {first_sender_name} regarding '{first_subject}'."

        if sender:
            if count == 1:
                return f"You have 1 email from {sender}. The subject is '{first_subject}'."
            return f"You have {count} emails from {sender}. The latest says: {first_snippet[:100]}."

        if count == 1:
            return f"You have 1 {'unread ' if unread_only else ''}email from {first_sender_name}: '{first_subject}'."
        return f"You have {count} {'unread ' if unread_only else ''}emails. The latest is from {first_sender_name}: '{first_subject}'."

    def format_email_read(self, email_data: Dict[str, Any]) -> str:
        sender = email_data.get("sender", "Unknown")
        sender_name = sender.split("<")[0].strip() if "<" in sender else sender
        subject = email_data.get("subject", "No Subject")
        body = self.clean_text_for_speech(email_data.get("body") or email_data.get("snippet", ""))
        
        # Limit body length for voice speech (approx 200 chars)
        if len(body) > 220:
            body = body[:220] + "..."

        return f"Email from {sender_name}: '{subject}'. {body}"

    def format_sms_search(self, messages: List[Dict[str, Any]], sender: Optional[str] = None) -> str:
        if not messages:
            if sender:
                return f"You have no recent messages from {sender}."
            return "You have no recent messages."

        count = len(messages)
        first = messages[0]
        first_sender = first.get("sender", sender or "Unknown")
        first_text = self.clean_text_for_speech(first.get("text", ""))

        if count == 1:
            return f"Message from {first_sender}: '{first_text}'"
        
        # Summarize up to 3 messages
        lines = [f"From {m.get('sender', 'Unknown')}: '{self.clean_text_for_speech(m.get('text', ''))[:60]}'" for m in messages[:3]]
        return f"You have {count} messages. " + "; ".join(lines)

    def format_call_action(self, action: str, contact_name: Optional[str] = None, phone: Optional[str] = None) -> str:
        if action == "call_make":
            if contact_name and phone:
                return f"Calling {contact_name} at {phone}."
            elif contact_name:
                return f"Calling {contact_name}."
            return "Initiating call."
        elif action == "call_answer":
            return "Answering the incoming call."
        elif action == "call_reject":
            return "Rejecting the incoming call."
        elif action == "call_hangup":
            return "Call ended."
        elif action == "call_incoming_query":
            return f"Incoming call from {contact_name or 'Unknown'}."
        return "Call action completed."

    def format_search_summary(self, topic: str, snippet_or_text: str) -> str:
        cleaned = self.clean_text_for_speech(snippet_or_text)
        if len(cleaned) > 250:
            cleaned = cleaned[:250] + "..."
        return f"Here is what I found for {topic}: {cleaned}"

smart_glass_formatter = SmartGlassResponseFormatter()
