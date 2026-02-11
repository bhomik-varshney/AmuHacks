"""
Symptom Worsening Evaluation Node
Re-evaluates crisis after initial steps based on user feedback
"""

import json
from config import get_groq_client, APP_CONFIG


def evaluate_worsening(state: dict, user_response: str) -> dict:
    """
    Evaluate symptom worsening and adapt response
    
    Args:
        state: Current graph state with initial assessment
        user_response: "yes" | "no" | "unsure"
    """
    client = get_groq_client()
    
    original_prompt = state["user_input"]
    previous_severity = state["severity_level"]
    previous_actions = state["immediate_actions"]
    crisis_type = state["crisis_type"]
    
    # Determine new severity and action
    if user_response == "yes":
        action_taken = "escalated"
        # Escalate severity
        severity_map = {"low": "moderate", "moderate": "high", "high": "critical", "critical": "critical"}
        new_severity = severity_map.get(previous_severity, "high")
        force_escalation = True
        max_steps = 5
        
    elif user_response == "unsure":
        action_taken = "reassessed"
        new_severity = previous_severity
        force_escalation = False
        max_steps = 5
        
    else:  # "no"
        action_taken = "continued"
        new_severity = previous_severity
        force_escalation = False
        max_steps = 3
    
    # Generate updated assessment and actions
    prompt = f"""Medical situation: "{original_prompt}"
Previous severity: {previous_severity}
New severity assessment: {new_severity}
Crisis type: {crisis_type}
User reports: Condition has {"WORSENED" if user_response == "yes" else "NOT worsened or unsure"}

Task: Generate updated assessment and immediate actions based on symptom change.

Provide response in this EXACT JSON format:
{{
  "assessment": "<updated calm explanation>",
  "immediate_actions": [
    {{
      "step_id": 1,
      "title": "<action title>",
      "instruction": "<clear instruction>",
      "duration_seconds": <integer OR null>,
      "user_confirmation_required": true/false,
      "critical": true/false,
      "repeatable": true/false
    }}
  ],
  "escalation_required": true/false,
  "who_to_contact": ["contact1", "contact2"],
  "escalation_reason": "<reason>",
  "reassurance_message": "<supportive message>"
}}

REQUIREMENTS:
- Generate BETWEEN 3 AND {max_steps} steps maximum
- If condition worsened: prioritize emergency-safe actions, at least 2 critical steps
- If unsure: focus on monitoring and safety checks
- If stable/better: focus on continued monitoring and follow-up guidance
- {"FORCE escalation.required = true" if force_escalation else ""}
- All actions must follow the structured format
- No diagnosis or medication advice

Severity-specific guidance:
{"- CRITICAL severity: Immediate emergency response required" if new_severity == "critical" else ""}
{"- HIGH severity: Urgent medical attention needed" if new_severity == "high" else ""}
{"- MODERATE severity: Medical attention recommended soon" if new_severity == "moderate" else ""}
{"- LOW severity: Monitor and follow-up as needed" if new_severity == "low" else ""}
"""

    try:
        response = client.chat.completions.create(
            model=APP_CONFIG["model"],
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical crisis re-evaluation assistant. Adapt guidance based on symptom changes."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=APP_CONFIG["temperature"],
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Update state
        state["severity_level"] = new_severity
        state["assessment"] = result.get("assessment", state["assessment"])
        
        # Validate and set immediate actions
        actions = result.get("immediate_actions", [])
        if len(actions) < 3 or len(actions) > max_steps:
            # Use fallback
            actions = generate_fallback_actions(new_severity, user_response)
        else:
            # Validate structure
            validated_actions = []
            for i, action in enumerate(actions, 1):
                validated_actions.append({
                    "step_id": action.get("step_id", i),
                    "title": action.get("title", f"Action {i}"),
                    "instruction": action.get("instruction", "Follow medical guidance"),
                    "duration_seconds": action.get("duration_seconds"),
                    "user_confirmation_required": action.get("user_confirmation_required", True),
                    "critical": action.get("critical", False),
                    "repeatable": action.get("repeatable", False)
                })
            actions = validated_actions
        
        state["immediate_actions"] = actions
        
        # Update escalation
        if force_escalation or result.get("escalation_required", False):
            state["escalation_required"] = True
            who = result.get("who_to_contact", ["ambulance"] if new_severity == "critical" else ["nearby hospital"])
            state["who_to_contact"] = who
            state["escalation_reason"] = result.get("escalation_reason", "Condition has worsened - immediate medical attention required")
        else:
            state["escalation_required"] = result.get("escalation_required", state["escalation_required"])
            state["who_to_contact"] = result.get("who_to_contact", state["who_to_contact"])
            state["escalation_reason"] = result.get("escalation_reason", state["escalation_reason"])
        
        state["reassurance_message"] = result.get("reassurance_message", 
            "Continue monitoring the situation carefully." if user_response == "no" 
            else "Medical attention is now more urgently needed.")
        
        # Add recheck info
        state["symptom_recheck"] = {
            "asked": True,
            "user_response": user_response,
            "severity_before": previous_severity,
            "severity_after": new_severity,
            "action_taken": action_taken
        }
        
    except Exception as e:
        # Fallback on error
        state["error"] = f"Error in worsening evaluation: {str(e)}"
        state["immediate_actions"] = generate_fallback_actions(new_severity, user_response)
        state["severity_level"] = new_severity
        state["escalation_required"] = force_escalation
        state["symptom_recheck"] = {
            "asked": True,
            "user_response": user_response,
            "severity_before": previous_severity,
            "severity_after": new_severity,
            "action_taken": action_taken
        }
    
    return state


def generate_fallback_actions(severity: str, user_response: str) -> list:
    """Generate fallback actions based on severity"""
    if user_response == "yes":  # Worsened
        return [
            {
                "step_id": 1,
                "title": "Call emergency services",
                "instruction": "Call emergency services immediately. The condition has worsened and requires urgent medical evaluation.",
                "duration_seconds": None,
                "user_confirmation_required": False,
                "critical": True,
                "repeatable": False
            },
            {
                "step_id": 2,
                "title": "Monitor vital signs",
                "instruction": "Continue monitoring breathing, consciousness, and any changes in symptoms until help arrives.",
                "duration_seconds": 60,
                "user_confirmation_required": True,
                "critical": True,
                "repeatable": True
            },
            {
                "step_id": 3,
                "title": "Stay with patient",
                "instruction": "Do not leave the patient alone. Be prepared to provide information to emergency responders.",
                "duration_seconds": None,
                "user_confirmation_required": True,
                "critical": True,
                "repeatable": False
            }
        ]
    elif user_response == "unsure":
        return [
            {
                "step_id": 1,
                "title": "Check vital signs",
                "instruction": "Check breathing rate, pulse, and level of consciousness carefully.",
                "duration_seconds": 30,
                "user_confirmation_required": True,
                "critical": False,
                "repeatable": True
            },
            {
                "step_id": 2,
                "title": "Contact medical advice",
                "instruction": "Call a medical helpline or your doctor for professional guidance on next steps.",
                "duration_seconds": None,
                "user_confirmation_required": True,
                "critical": False,
                "repeatable": False
            },
            {
                "step_id": 3,
                "title": "Continue monitoring",
                "instruction": "Keep watching for any changes and be ready to call emergency services if condition worsens.",
                "duration_seconds": 120,
                "user_confirmation_required": True,
                "critical": False,
                "repeatable": True
            }
        ]
    else:  # No worsening
        return [
            {
                "step_id": 1,
                "title": "Continue monitoring",
                "instruction": "Keep monitoring the situation for any changes over the next few hours.",
                "duration_seconds": None,
                "user_confirmation_required": True,
                "critical": False,
                "repeatable": True
            },
            {
                "step_id": 2,
                "title": "Follow medical advice",
                "instruction": "Follow up with healthcare provider as recommended for proper evaluation.",
                "duration_seconds": None,
                "user_confirmation_required": True,
                "critical": False,
                "repeatable": False
            },
            {
                "step_id": 3,
                "title": "Watch for warning signs",
                "instruction": "Be alert for any new symptoms or worsening, and seek help immediately if needed.",
                "duration_seconds": None,
                "user_confirmation_required": True,
                "critical": False,
                "repeatable": True
            }
        ]
