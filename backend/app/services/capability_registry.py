"""
EVA Capability Registry
Unified registry declaring cross-platform capability availability across
Web, Android, and Smart Glasses.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class EVACapability(BaseModel):
    id: str
    name: str
    category: str
    description: str
    available_on_web: bool
    available_on_android: bool
    available_on_glasses: bool
    requires_internet: bool
    requires_auth: bool
    requires_confirmation: bool
    output_mode: Dict[str, str]

class EVACapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, EVACapability] = {
            "research": EVACapability(
                id="research",
                name="Academic Research & Literature Search",
                category="Intelligence",
                description="Multilingual paper search across arXiv, OpenAlex, Semantic Scholar, and CrossRef",
                available_on_web=True,
                available_on_android=True,
                available_on_glasses=True,
                requires_internet=True,
                requires_auth=False,
                requires_confirmation=False,
                output_mode={"web": "DETAILED_CONSTELLATION", "android": "COMPACT_LIST", "glasses": "CONCISE_SPOKEN"}
            ),
            "documents": EVACapability(
                id="documents",
                name="Document Knowledge & Retrieval",
                category="Knowledge",
                description="Upload, indexing, and semantic search across PDF, DOCX, TXT, MD, CSV files",
                available_on_web=True,
                available_on_android=True,
                available_on_glasses=True,
                requires_internet=False,
                requires_auth=False,
                requires_confirmation=False,
                output_mode={"web": "DOCUMENT_LIBRARY", "android": "DOCUMENT_LIST", "glasses": "SPOKEN_SUMMARY"}
            ),
            "gmail": EVACapability(
                id="gmail",
                name="Gmail Communication & Search",
                category="Productivity",
                description="Search unread emails, read message threads, and draft verified replies",
                available_on_web=True,
                available_on_android=True,
                available_on_glasses=True,
                requires_internet=True,
                requires_auth=True,
                requires_confirmation=True,
                output_mode={"web": "EXPANDED_THREAD", "android": "CARD_SUMMARY", "glasses": "SPOKEN_SNIPPET"}
            ),
            "calendar": EVACapability(
                id="calendar",
                name="Google Calendar Scheduling",
                category="Productivity",
                description="View upcoming events, schedule meetings, and query daily agenda",
                available_on_web=True,
                available_on_android=True,
                available_on_glasses=True,
                requires_internet=True,
                requires_auth=True,
                requires_confirmation=True,
                output_mode={"web": "CALENDAR_AGENDA", "android": "EVENT_CARD", "glasses": "SPOKEN_TIME"}
            ),
            "activity_timeline": EVACapability(
                id="activity_timeline",
                name="Operational Activity & Session Memory",
                category="Memory",
                description="Chronological event reconstruction and active session tracking",
                available_on_web=True,
                available_on_android=True,
                available_on_glasses=False,
                requires_internet=False,
                requires_auth=False,
                requires_confirmation=False,
                output_mode={"web": "SESSION_TIMELINE", "android": "ACTIVITY_STREAM", "glasses": "NONE"}
            ),
            "device_perception": EVACapability(
                id="device_perception",
                name="Smart Glasses BLE Audio & Hardware Extension",
                category="Hardware",
                description="Continuous 16kHz audio streaming, voice wake, and battery status",
                available_on_web=True,
                available_on_android=True,
                available_on_glasses=True,
                requires_internet=False,
                requires_auth=False,
                requires_confirmation=False,
                output_mode={"web": "DEVICE_PRESENCE", "android": "PERCEPTION_RITUAL", "glasses": "HARDWARE_STREAM"}
            )
        }

    def list_capabilities(self) -> List[Dict[str, Any]]:
        return [cap.model_dump() for cap in self._capabilities.values()]

    def get_capabilities(self) -> List[EVACapability]:
        return list(self._capabilities.values())

    def get_capabilities_by_platform(self, platform: str) -> List[EVACapability]:
        plat = platform.lower()
        if plat in ["web", "browser"]:
            return [c for c in self._capabilities.values() if c.available_on_web]
        elif plat in ["android", "mobile", "companion"]:
            return [c for c in self._capabilities.values() if c.available_on_android]
        elif plat in ["glasses", "smart_glasses", "esp32", "hardware"]:
            return [c for c in self._capabilities.values() if c.available_on_glasses]
        return list(self._capabilities.values())

    def get_capability(self, cap_id: str) -> Optional[EVACapability]:
        return self._capabilities.get(cap_id)

capability_registry = EVACapabilityRegistry()
