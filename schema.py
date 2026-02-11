"""
JSON Output Schema for Medical Crisis Decision Assistant
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ImmediateAction(BaseModel):
    """Structured immediate action step"""
    step_id: int = Field(description="Step number starting from 1")
    title: str = Field(description="Short, action-oriented title")
    instruction: str = Field(description="Clear, calm instruction suitable for civilians")
    duration_seconds: Optional[int] = Field(
        description="Duration in seconds (5-120) or null if no timing needed"
    )
    user_confirmation_required: bool = Field(
        description="Whether user should confirm before proceeding"
    )
    critical: bool = Field(description="Whether this is a critical step")
    repeatable: bool = Field(
        description="Whether this action should be repeated (e.g., CPR, monitoring)"
    )


class Escalation(BaseModel):
    """Escalation information"""
    required: bool = Field(description="Whether escalation is needed")
    who_to_contact: List[str] = Field(
        description="List of contacts: relative, friend, ambulance, nearby hospital"
    )
    reason: str = Field(description="Reason for escalation")





class CrisisResponse(BaseModel):
    """Complete crisis assessment response"""
    user_prompt: str = Field(description="Original user input")
    crisis_type: str = Field(description="Identified medical issue")
    severity_level: Literal["low", "moderate", "high", "critical"] = Field(
        description="Severity assessment"
    )
    assessment: str = Field(
        description="Short calm explanation of what may be happening"
    )
    immediate_actions: List[ImmediateAction] = Field(
        description="Step-by-step immediate actions to take"
    )
    do_not_do: List[str] = Field(
        description="Actions to avoid"
    )
    escalation: Escalation = Field(
        description="Escalation information"
    )
    reassurance_message: str = Field(
        description="Calm, supportive message"
    )


# Validation constants
SEVERITY_LEVELS = ["low", "moderate", "high", "critical"]
CONTACT_TYPES = ["relative", "friend", "ambulance", "nearby hospital"]

# Medical crisis keywords for classification
MEDICAL_CRISIS_KEYWORDS = {
    "cardiac": ["chest pain", "heart", "cardiac", "palpitation", "angina"],
    "respiratory": ["breathing", "breathe", "shortness of breath", "asthma", "choking"],
    "neurological": ["headache", "stroke", "seizure", "fainting", "faint", "dizzy", "unconscious"],
    "trauma": ["injury", "bleeding", "blood", "wound", "fracture", "broken", "cut"],
    "allergic": ["allergy", "allergic", "rash", "swelling", "anaphylaxis"],
    "fever": ["fever", "temperature", "hot", "chills"],
    "poisoning": ["poison", "overdose", "toxic", "ingested"],
    "pain": ["severe pain", "excruciating", "unbearable pain"]
}

# Red flag symptoms requiring immediate escalation
RED_FLAG_SYMPTOMS = [
    "chest pain",
    "difficulty breathing",
    "unconscious",
    "severe bleeding",
    "stroke symptoms",
    "severe allergic reaction",
    "choking",
    "seizure",
    "suspected poisoning",
    "severe head injury"
]
