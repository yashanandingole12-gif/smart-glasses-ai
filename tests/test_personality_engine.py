import pytest
from backend.app.services.personality_engine import personality_engine, FormalityStyle, DetectedLanguage

def test_language_detection():
    assert personality_engine.analyze_tone("Hello, what is on my calendar?")["language"] == DetectedLanguage.ENGLISH
    assert personality_engine.analyze_tone("आज मेरा क्या शेड्यूल है?")["language"] == DetectedLanguage.HINDI
    assert personality_engine.analyze_tone("आज माझा कोणता क्लास आहे?")["language"] == DetectedLanguage.MARATHI
    assert personality_engine.analyze_tone("bhai mera latest mail check kar")["language"] == DetectedLanguage.HINGLISH

def test_formality_detection():
    assert personality_engine.analyze_tone("bro check my email")["formality"] == FormalityStyle.CASUAL
    assert personality_engine.analyze_tone("Could you please check my upcoming meetings?")["formality"] == FormalityStyle.FORMAL
    assert personality_engine.analyze_tone("What is the time?")["formality"] == FormalityStyle.BALANCED

def test_system_prompt_builder():
    prompt_casual = personality_engine.build_system_prompt("bro check my mail")
    assert "casual and direct" in prompt_casual

    prompt_hinglish = personality_engine.build_system_prompt("aaj ka schedule bata")
    assert "Hinglish" in prompt_hinglish
