"""
Decision & Action Planning Node
Generates immediate actions and things to avoid
"""

import json
from config import get_groq_client, SYSTEM_PROMPTS, APP_CONFIG


def plan_actions(state: dict) -> dict:
    """
    Generate step-by-step immediate actions and do_not_do list
    """
    if state.get("error"):
        return state
    
    client = get_groq_client()
    normalized_input = state["normalized_input"]
    crisis_type = state["crisis_type"]
    severity = state["severity_level"]
    escalation_required = state["escalation_required"]
    
    prompt = f"""Medical situation: "{normalized_input}"
Crisis type: {crisis_type}
Severity: {severity}
Escalation required: {escalation_required}

Task: Create structured immediate action steps and dangerous actions to avoid.

Provide response in this EXACT JSON format:
{{
  "immediate_actions": [
    {{
      "step_id": 1,
      "title": "<short action title>",
      "instruction": "<clear instruction>",
      "duration_seconds": <integer 5-120 OR null>,
      "user_confirmation_required": true/false,
      "critical": true/false,
      "repeatable": true/false
    }}
  ],
  "do_not_do": [
    "<dangerous action to avoid>",
    "<another dangerous action to avoid>"
  ],
  "reassurance_message": "<calm, supportive message>"
}}

IMMEDIATE ACTIONS REQUIREMENTS:
- Generate BETWEEN 3 AND 7 steps
- Each step MUST have ALL fields (step_id, title, instruction, duration_seconds, user_confirmation_required, critical, repeatable)
- step_id starts at 1 and increments
- title: 2-5 words, action-oriented
- instruction: Clear, calm, suitable for untrained civilians
- duration_seconds: Use null if no timing needed, or realistic values (5-120 seconds) for timed actions
- user_confirmation_required: false ONLY for urgent actions that can't wait (e.g., calling ambulance)
- critical: true for life-critical steps (at least one for high/critical severity)
- repeatable: true for actions like CPR, monitoring, checking breathing

Step ordering:
1. Safety first (check environment)
2. Position patient if needed
3. Call for help (if escalation required)
4. Immediate interventions (stop bleeding, clear airway, etc.)
5. Monitoring (breathing, consciousness)
6. Comfort and reassurance

Safety constraints:
- NO medical diagnosis
- NO medication advice
- NO invasive procedures
- Assume user is untrained

Guidelines for do_not_do:
- List 2-4 dangerous actions to avoid
- Focus on common mistakes people make
- Be specific

Guidelines for reassurance_message:
- Calm and supportive tone
- Acknowledge the situation
- Encourage rational action
- 1-2 sentences"""

    try:
        response = client.chat.completions.create(
            model=APP_CONFIG["model"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["action_planning"]},
                {"role": "user", "content": prompt}
            ],
            temperature=APP_CONFIG["temperature"],
            max_tokens=1200,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate and set immediate_actions
        actions = result.get("immediate_actions", [])
        
        # Ensure between 3-7 steps
        if len(actions) < 3 or len(actions) > 7:
            # Fallback actions if validation fails
            state["immediate_actions"] = [
                {
                    "step_id": 1,
                    "title": "Ensure safety",
                    "instruction": "Make sure the environment is safe for both you and the patient.",
                    "duration_seconds": None,
                    "user_confirmation_required": True,
                    "critical": False,
                    "repeatable": False
                },
                {
                    "step_id": 2,
                    "title": "Call for help",
                    "instruction": "Call emergency services immediately and describe the situation.",
                    "duration_seconds": None,
                    "user_confirmation_required": False,
                    "critical": True,
                    "repeatable": False
                },
                {
                    "step_id": 3,
                    "title": "Monitor patient",
                    "instruction": "Stay with the patient and monitor their breathing and consciousness.",
                    "duration_seconds": 60,
                    "user_confirmation_required": True,
                    "critical": True,
                    "repeatable": True
                }
            ]
        else:
            # Validate each action has required fields
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
            state["immediate_actions"] = validated_actions
        
        state["do_not_do"] = result.get("do_not_do", [
            "Do not panic or make rushed decisions",
            "Do not give any medication without medical guidance"
        ])
        state["reassurance_message"] = result.get("reassurance_message", 
            "You're taking the right steps by seeking guidance. Stay calm and follow the actions carefully.")
        
    except Exception as e:
        state["error"] = f"Error in action planning: {str(e)}"
        state["immediate_actions"] = [
            {
                "step_id": 1,
                "title": "Call emergency services",
                "instruction": "Call emergency services immediately and describe all symptoms.",
                "duration_seconds": None,
                "user_confirmation_required": False,
                "critical": True,
                "repeatable": False
            },
            {
                "step_id": 2,
                "title": "Stay with patient",
                "instruction": "Do not leave the patient alone. Monitor their condition.",
                "duration_seconds": None,
                "user_confirmation_required": True,
                "critical": True,
                "repeatable": False
            },
            {
                "step_id": 3,
                "title": "Follow dispatcher instructions",
                "instruction": "Listen carefully to emergency dispatcher and follow their guidance.",
                "duration_seconds": None,
                "user_confirmation_required": True,
                "critical": True,
                "repeatable": False
            }
        ]
        state["do_not_do"] = ["Do not delay seeking professional help"]
        state["reassurance_message"] = "Please seek immediate medical attention."
    
    return state
