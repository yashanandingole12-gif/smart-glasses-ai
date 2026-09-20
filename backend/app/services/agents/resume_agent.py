"""
User Profile & Resume Agent for EVA
Maintains structured user profile context: education, technical skills,
robotics experience, projects, internships, preferred locations, and career objectives.
Acts as input to OpportunityMatcher.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("eva.agents.resume")

class UserProfile(BaseModel):
    user_id: str = "default_user"
    full_name: str = "Wearable User"
    email: Optional[str] = "user@example.com"
    education: str = "B.Tech in Computer Science / Robotics Engineering"
    degree: str = "Bachelor of Technology"
    graduation_year: int = 2025
    skills: List[str] = Field(default_factory=lambda: [
        "Python", "C++", "ROS2", "Robotics", "Embedded Systems", "ESP32",
        "Computer Vision", "FastAPI", "Kotlin", "Android", "Machine Learning"
    ])
    programming_languages: List[str] = Field(default_factory=lambda: [
        "Python", "C++", "C", "Kotlin", "SQL", "Rust"
    ])
    robotics_experience: List[str] = Field(default_factory=lambda: [
        "Autonomous SLAM Navigation with ROS2",
        "Kinematics & Motion Control for Robotic Manipulators",
        "Sensor Fusion with IMU, LiDAR, and Stereo Depth Cameras"
    ])
    projects: List[Dict[str, Any]] = Field(default_factory=lambda: [
        {
            "name": "EVA Smart Glasses",
            "tech_stack": ["ESP32-S3", "I2S Audio", "Android Kotlin", "FastAPI", "Gemini AI"],
            "description": "Low-latency multimodal wearable companion with on-device deterministic routing and BLE/Wi-Fi streaming."
        },
        {
            "name": "Autonomous Mobile Robot (AMR)",
            "tech_stack": ["ROS2 Humble", "Nav2", "C++", "LiDAR", "Micro-ROS"],
            "description": "Indoor mapping and path planning with dynamic obstacle avoidance."
        }
    ])
    internships: List[Dict[str, Any]] = Field(default_factory=lambda: [
        {
            "role": "Robotics Engineering Intern",
            "organization": "RoboTech Labs",
            "duration": "May 2024 - July 2024",
            "highlights": "Designed embedded firmware for brushless motor drivers and integrated camera vision pipeline."
        }
    ])
    experience_years: float = 1.5
    preferred_locations: List[str] = Field(default_factory=lambda: ["Bengaluru", "Pune", "Hyderabad", "Nagpur", "Remote"])
    preferred_roles: List[str] = Field(default_factory=lambda: [
        "Robotics Engineer Intern",
        "Embedded Software Engineer",
        "AI/ML Wearable Engineer",
        "Firmware Developer"
    ])
    salary_preferences: Optional[str] = "Competitive / Industry Standard"
    career_objectives: str = "Seeking high-impact robotics and embedded AI roles to build intelligent physical systems."

class ResumeAgent:
    def __init__(self):
        self._profile = UserProfile()
        logger.info("ResumeAgent initialized with default UserProfile.")

    def get_profile(self) -> UserProfile:
        return self._profile

    def update_profile(self, updates: Dict[str, Any]) -> UserProfile:
        """
        Incrementally update specific fields in UserProfile without hallucination.
        """
        current_data = self._profile.model_dump()
        for k, v in updates.items():
            if k in current_data:
                current_data[k] = v
        self._profile = UserProfile(**current_data)
        logger.info(f"UserProfile updated: fields {list(updates.keys())}")
        return self._profile

    def extract_matching_keywords(self) -> Dict[str, Any]:
        """
        Summarized keywords for matching against job listings and internships.
        """
        return {
            "skills": self._profile.skills,
            "roles": self._profile.preferred_roles,
            "locations": self._profile.preferred_locations,
            "experience_years": self._profile.experience_years,
            "education": self._profile.education
        }

resume_agent = ResumeAgent()
