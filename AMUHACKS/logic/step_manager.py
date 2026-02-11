from llm.groq_client import call_llm
from logic.timer_decider import decide_timer
from logic.reevaluator import reevaluate
from logic.escalation_manager import check_emergency
from emergency.financial_emergency import build_emergency_response
from config.settings import MAX_STEPS


def run_steps(user_text, mood, intent, shock, risk_level):

    # 🔥 SAFETY OVERRIDE — MUST BE FIRST
    if risk_level == "extreme":
        return {
            "status": "emergency",
            "steps_taken": 0,
            "message":
            "You are not alone. Please contact a trusted person, family member, or a crisis helpline immediately.",
            "steps": []
        }

    # ✅ HIGH RISK USERS → escalate faster
    MAX_LOCAL_STEPS = 3 if risk_level == "high" else MAX_STEPS

    history = []

    for step in range(1, MAX_LOCAL_STEPS + 1):

        try:
            llm_output = call_llm(user_text, mood, intent, shock, step)

            # ✅ CRASH PROTECTION (LLMs are unpredictable)
            if not isinstance(llm_output, dict):
                llm_output = {}

            llm_output.setdefault("step", step)
            llm_output.setdefault("instruction", "Pause. Take a slow breath.")
            llm_output.setdefault("actionable", True)
            llm_output.setdefault("resolved", False)

            llm_output["timer_seconds"] = decide_timer(mood)

        except Exception as e:
            # 🔥 If LLM completely fails
            return build_emergency_response(
                f"LLM failure: {str(e)}"
            )

        history.append(llm_output)

        # ✅ Reevaluator protection
        try:
            reeval = reevaluate(history)
        except Exception:
            reeval = {"problem_resolved": False}

        if reeval.get("problem_resolved"):
            return {
                "status": "resolved",
                "steps_taken": step,
                "steps": history,
                "message": llm_output["instruction"]
            }

        if check_emergency(step, reeval):
            return build_emergency_response(
                "User unable to proceed"
            )

    return {
        "status": "needs_support",
        "steps_taken": MAX_LOCAL_STEPS,
        "steps": history,
        "message": "External support recommended"
    }
