import re
from typing import Dict, Any, Optional
from enum import Enum

class FormalityStyle(str, Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    BALANCED = "balanced"

class DetectedLanguage(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"
    HINGLISH = "hinglish"

class PersonalityEngine:
    """
    Canonical LARA Persona & Tone Preservation Engine.
    Ensures online LLM and offline deterministic engines share the same tone,
    directness, and communication style.
    """

    SYSTEM_PROMPT_CORE = (
        "You are LARA — a smart glasses personal executive companion. "
        "You are direct, clear, grounded, and concise. Never overly cheerful, subservient, or sycophantic. "
        "Keep conversational replies brief and wearable-friendly. "
        "When explaining processes, how-to questions, recipes, or general knowledge, provide clear, structured instructions without conversational filler. "
        "Never invent personal data. Never use conversational filler like 'Sure!', 'Certainly!', 'I would be happy to help!'. "
        "Preserve the user's natural language and communication formality."
    )

    def analyze_tone(self, user_message: str) -> Dict[str, Any]:
        """Analyze user input for language and formality signals."""
        msg = user_message.strip()
        msg_lower = msg.lower()

        # 1. Detect language
        lang = self._detect_language(msg, msg_lower)

        # 2. Detect formality
        formality = self._detect_formality(msg_lower)

        return {
            "language": lang,
            "formality": formality,
            "is_voice_optimized": True
        }

    def _detect_language(self, msg: str, msg_lower: str) -> DetectedLanguage:
        # Check Devanagari script
        has_devanagari = bool(re.search(r"[\u0900-\u097F]", msg))
        if has_devanagari:
            # Check Marathi specific words
            marathi_markers = ["आहे", "आहेत", "नाही", "काय", "झाले", "करा", "सांगा", "वाचा", "तपासा", "कुठे", "सकाळ", "दाखव", "माझं", "माझे", "कॅलेंडर", "शुभ", "नमस्कार"]
            if any(w in msg for w in marathi_markers):
                return DetectedLanguage.MARATHI
            return DetectedLanguage.HINDI

        # Check Hinglish / Latin script regional markers
        hinglish_markers = [
            "kya", "hai", "batao", "bhai", "yaar", "karo", "mera", "meri", "aaj", "kal",
            "kitna", "hota", "hoga", "bolo", "padho", "dekh", "sun", "mat", "nahi"
        ]
        words = set(re.findall(r"\b\w+\b", msg_lower))
        if len(words.intersection(hinglish_markers)) >= 1:
            return DetectedLanguage.HINGLISH

        return DetectedLanguage.ENGLISH

    def _detect_formality(self, msg_lower: str) -> FormalityStyle:
        casual_markers = ["bro", "bhai", "yaar", "dude", "hey", "sup", "what's up", "check kar", "bata"]
        formal_markers = ["please", "kindly", "could you", "would you", "sir", "regards", "request", "assist"]

        if any(m in msg_lower for m in casual_markers):
            return FormalityStyle.CASUAL
        if any(m in msg_lower for m in formal_markers):
            return FormalityStyle.FORMAL
        return FormalityStyle.BALANCED

    def build_system_prompt(self, user_message: str, requested_language: Optional[str] = None) -> str:
        """Constructs tone-aligned system prompt for LLM requests."""
        tone = self.analyze_tone(user_message)
        prompt = self.SYSTEM_PROMPT_CORE

        if requested_language == "mr":
            target_lang = DetectedLanguage.MARATHI
        elif requested_language == "hi":
            target_lang = DetectedLanguage.HINDI
        elif requested_language == "en":
            target_lang = DetectedLanguage.ENGLISH
        else:
            target_lang = tone["language"]

        if tone["formality"] == FormalityStyle.CASUAL:
            prompt += " Match the user's casual and direct style naturally without excessive slang."
        elif tone["formality"] == FormalityStyle.FORMAL:
            prompt += " Match the user's polite and professional style."

        if target_lang == DetectedLanguage.HINDI:
            prompt += " Respond naturally in Hindi (Devanagari script) in 1-2 short sentences."
        elif target_lang == DetectedLanguage.MARATHI:
            prompt += " Respond naturally in Marathi (Devanagari script) in 1-2 short sentences. Do not reply in Hindi."
        elif target_lang == DetectedLanguage.HINGLISH:
            prompt += " Respond in natural Hinglish (conversational Hindi written in Roman script) in 1-2 short sentences."

        return prompt

    def style_offline_response(self, text: str, user_message: str) -> str:
        """Adapts deterministic responses subtly to user style while keeping core facts accurate."""
        tone = self.analyze_tone(user_message)
        # Keep clean, concise voice phrasing
        clean_text = text.strip()
        return clean_text

personality_engine = PersonalityEngine()
