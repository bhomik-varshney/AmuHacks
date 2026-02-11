"""
Input Normalization Node
Cleans and summarizes user input, removes irrelevant text
"""

import json
from typing import TypedDict
from config import get_groq_client, SYSTEM_PROMPTS, APP_CONFIG


class GraphState(TypedDict):
    """State object for the graph"""
    user_input: str
    normalized_input: str
    crisis_type: str
    severity_level: str
    assessment: str
    immediate_actions: list
    do_not_do: list
    escalation_required: bool
    who_to_contact: list
    escalation_reason: str
    reassurance_message: str
    error: str


def normalize_input(state: GraphState) -> GraphState:
    """
    Normalize and clean user input
    Returns updated state with normalized_input
    """
    client = get_groq_client()
    user_input = state["user_input"]
    
    prompt = f"""User input: "{user_input}"

Task: Clean and normalize this input. Extract the core medical concern.
If this is clearly NOT a medical emergency or health-related input, respond with exactly: NON_MEDICAL_INPUT

Otherwise, provide a clean, concise summary of the medical situation in 1-2 sentences.
Focus on symptoms, who is affected, and observable facts."""

    try:
        response = client.chat.completions.create(
            model=APP_CONFIG["model"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["input_normalization"]},
                {"role": "user", "content": prompt}
            ],
            temperature=APP_CONFIG["temperature"],
            max_tokens=500
        )
        
        normalized = response.choices[0].message.content.strip()
        
        # Check for non-medical input
        if "NON_MEDICAL_INPUT" in normalized:
            state["error"] = "Input is not medical-related. Please describe a medical crisis or health emergency."
            state["normalized_input"] = ""
        else:
            state["normalized_input"] = normalized
            state["error"] = ""
            
    except Exception as e:
        state["error"] = f"Error in input normalization: {str(e)}"
        state["normalized_input"] = ""
    
    return state
