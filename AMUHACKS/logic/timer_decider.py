def decide_timer(mood):
    if mood == "panic":
        return 60
    if mood == "stress":
        return 45
    return 30
