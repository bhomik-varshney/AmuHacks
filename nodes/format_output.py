"""
Structured Output Node
Assembles and validates final JSON response
"""

import json
from schema import CrisisResponse, Escalation


def format_output(state: dict) -> dict:
    """
    Assemble final response in strict JSON schema format
    """
    if state.get("error"):
        # Return error response in valid JSON format
        error_response = {
            "user_prompt": state.get("user_input", ""),
            "crisis_type": "Error",
            "severity_level": "low",
            "assessment": state.get("error", "An error occurred"),
            "immediate_actions": [
                {
                    "step_id": 1,
                    "title": "Rephrase input",
                    "instruction": "Please provide a clear description of the medical emergency or health situation.",
                    "duration_seconds": None,
                    "user_confirmation_required": True,
                    "critical": False,
                    "repeatable": False
                }
            ],
            "do_not_do": ["Do not provide non-medical queries"],
            "escalation": {
                "required": False,
                "who_to_contact": [],
                "reason": "Not applicable"
            },
            "reassurance_message": "Please provide information about a medical situation for assistance."
        }
        state["final_output"] = error_response
        return state
    
    try:
        # Build escalation object
        escalation = Escalation(
            required=state["escalation_required"],
            who_to_contact=state["who_to_contact"],
            reason=state["escalation_reason"]
        )
        
        # Build complete response
        response = CrisisResponse(
            user_prompt=state["user_input"],
            crisis_type=state["crisis_type"],
            severity_level=state["severity_level"],
            assessment=state["assessment"],
            immediate_actions=state["immediate_actions"],
            do_not_do=state["do_not_do"],
            escalation=escalation,
            reassurance_message=state["reassurance_message"]
        )
        
        # Convert to dict and store in state
        state["final_output"] = response.model_dump()
        
    except Exception as e:
        # Fallback to manual construction
        state["final_output"] = {
            "user_prompt": state.get("user_input", ""),
            "crisis_type": state.get("crisis_type", "Unknown"),
            "severity_level": state.get("severity_level", "moderate"),
            "assessment": state.get("assessment", "Medical situation requiring assessment"),
            "immediate_actions": state.get("immediate_actions", [
                {
                    "step_id": 1,
                    "title": "Seek medical help",
                    "instruction": "Contact emergency services or go to the nearest hospital.",
                    "duration_seconds": None,
                    "user_confirmation_required": False,
                    "critical": True,
                    "repeatable": False
                }
            ]),
            "do_not_do": state.get("do_not_do", ["Do not delay seeking help"]),
            "escalation": {
                "required": state.get("escalation_required", True),
                "who_to_contact": state.get("who_to_contact", ["ambulance"]),
                "reason": state.get("escalation_reason", "Safety precaution")
            },
            "reassurance_message": state.get("reassurance_message", "Please seek medical attention."),
            "symptom_recheck": state.get("symptom_recheck")
        }
    
    return state


def should_continue(state: dict) -> str:
    """
    Decide if graph should continue or end
    """
    if state.get("error"):
        return "end"
    return "continue"
