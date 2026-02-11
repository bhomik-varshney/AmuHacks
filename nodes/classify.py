"""
Crisis Classification Node
Identifies medical crisis type and severity level
"""

import json
from typing import TypedDict
from config import get_groq_client, SYSTEM_PROMPTS, APP_CONFIG


def classify_crisis(state: dict) -> dict:
    """
    Classify the crisis type and determine severity level
    """
    if state.get("error"):
        return state
    
    client = get_groq_client()
    normalized_input = state["normalized_input"]
    
    prompt = f"""Medical situation: "{normalized_input}"

Task: Classify this medical crisis.

Provide your response in this EXACT JSON format:
{{
  "crisis_type": "<type of medical issue>",
  "severity_level": "<low|moderate|high|critical>",
  "assessment": "<brief calm explanation of what may be happening>"
}}

Severity Guidelines:
- LOW: Minor issues, no immediate danger (small cuts, mild headache, minor fever)
- MODERATE: Concerning symptoms needing attention soon (persistent fever, moderate pain)
- HIGH: Serious symptoms needing urgent care (severe pain, high fever, persistent vomiting)
- CRITICAL: Life-threatening, needs immediate emergency (chest pain, difficulty breathing, unconsciousness, severe bleeding)

Be conservative - when in doubt, increase severity level.
The assessment should be calm, non-alarming, and helpful."""

    try:
        response = client.chat.completions.create(
            model=APP_CONFIG["model"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["crisis_classification"]},
                {"role": "user", "content": prompt}
            ],
            temperature=APP_CONFIG["temperature"],
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        state["crisis_type"] = result.get("crisis_type", "Unknown medical issue")
        state["severity_level"] = result.get("severity_level", "moderate").lower()
        state["assessment"] = result.get("assessment", "Medical situation requiring assessment")
        
        # Validate severity level
        if state["severity_level"] not in ["low", "moderate", "high", "critical"]:
            state["severity_level"] = "moderate"
            
    except Exception as e:
        state["error"] = f"Error in crisis classification: {str(e)}"
        state["crisis_type"] = "Unknown"
        state["severity_level"] = "moderate"
        state["assessment"] = "Unable to assess the situation properly."
    
    return state
