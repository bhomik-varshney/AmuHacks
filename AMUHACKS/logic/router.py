from config.constants import SHOCK_SEVERITY


def safety_router(user_text, mood, shock):

    severity = SHOCK_SEVERITY.get(shock, 5)

    text = user_text.lower()

    # 🚨 EXTREME RISK
    if any(word in text for word in [
        "suicide",
        "kill myself",
        "want to die",
        "end my life"
    ]):
        return "extreme"

    # 🚨 HIGH RISK
    if mood == "panic" and severity >= 8:
        return "high"

    # ⚠️ MEDIUM
    if severity >= 7:
        return "medium"

    return "low"
