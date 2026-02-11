def detect_mood(text: str) -> str:
    t = text.lower()

    panic_words = [
        "panic","can't breathe","heart racing",
        "dying","losing control","terrified"
    ]

    stress_words = [
        "worried","stressed","anxious",
        "tense","overthinking","scared"
    ]

    if any(w in t for w in panic_words):
        return "panic"

    if any(w in t for w in stress_words):
        return "stress"

    return "neutral"
