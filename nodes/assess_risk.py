"""
Safety & Risk Assessment Node
Checks for red-flag symptoms and decides escalation requirements
"""

import json
from config import get_groq_client, SYSTEM_PROMPTS, APP_CONFIG


def assess_risk(state: dict) -> dict:
    """
    Assess safety risks and determine if escalation is required
    """
    if state.get("error"):
        return state
    
    client = get_groq_client()
    normalized_input = state["normalized_input"]
    severity = state["severity_level"]
    crisis_type = state["crisis_type"]
    
    prompt = f"""Medical situation: "{normalized_input}"
Crisis type: {crisis_type}
Current severity: {severity}

Task: Assess if this situation requires emergency escalation.

Red-flag symptoms requiring immediate escalation:
- Chest pain with sweating, nausea, or shortness of breath
- Difficulty breathing or choking
- Unconsciousness or unresponsiveness
- Severe bleeding that won't stop
- Stroke symptoms (facial drooping, arm weakness, speech difficulty)
- Severe allergic reactions (swelling, difficulty breathing)
- Seizures
- Suspected poisoning or overdose
- Severe head injury

Provide response in this EXACT JSON format:
{{
  "escalation_required": true/false,
  "who_to_contact": ["contact1", "contact2"],
  "reason": "<why escalation is or isn't needed>"
}}

Contact types to choose from:
- "ambulance" (for critical emergencies)
- "nearby hospital" (for high urgency)
- "relative" (for moderate support)
- "friend" (for moderate support)

Rules:
- If severity is "critical" → escalation_required: true, include "ambulance"
- If severity is "high" → escalation_required: true, include "nearby hospital"
- If severity is "moderate" → escalation_required: false or true (based on symptoms), include "relative" or "friend"
- If severity is "low" → escalation_required: false

Be conservative - prioritize safety."""

    try:
        response = client.chat.completions.create(
            model=APP_CONFIG["model"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["risk_assessment"]},
                {"role": "user", "content": prompt}
            ],
            temperature=APP_CONFIG["temperature"],
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        state["escalation_required"] = result.get("escalation_required", False)
        state["who_to_contact"] = result.get("who_to_contact", ["relative"])
        state["escalation_reason"] = result.get("reason", "Based on symptom severity")
        
        # Track escalation history for memory
        if not state.get("escalation_history"):
            state["escalation_history"] = []
        state["escalation_history"].append({
            "required": state["escalation_required"],
            "who_to_contact": state["who_to_contact"],
            "reason": state["escalation_reason"],
            "severity": severity
        })
        
        # Auto-escalate for high/critical severity if not already done
        if severity in ["critical", "high"] and not state["escalation_required"]:
            state["escalation_required"] = True
            if severity == "critical" and "ambulance" not in state["who_to_contact"]:
                state["who_to_contact"].insert(0, "ambulance")
            if severity == "high" and "nearby hospital" not in state["who_to_contact"]:
                state["who_to_contact"].insert(0, "nearby hospital")
                
    except Exception as e:
        state["error"] = f"Error in risk assessment: {str(e)}"
        # Default to safe escalation
        state["escalation_required"] = True
        state["who_to_contact"] = ["ambulance"]
        state["escalation_reason"] = "Unable to properly assess risk - recommending emergency contact"
    
    return state
