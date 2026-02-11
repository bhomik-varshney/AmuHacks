def reevaluate(history):
    last = history[-1]

    return {
        "problem_resolved": last.get("resolved", False),
        "can_user_take_next_action": last.get("actionable", True)
    }
