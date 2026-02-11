from config.settings import MAX_STEPS, OPTIMAL_STEPS

def check_emergency(step_count, reevaluation):

    if step_count >= MAX_STEPS:
        return True

    if step_count >= OPTIMAL_STEPS and not reevaluation["can_user_take_next_action"]:
        return True

    return False
