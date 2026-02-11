from fastapi import FastAPI
from pydantic import BaseModel

from logic.router import safety_router
from detection.mood_detector import detect_mood
from detection.financial_intent_detector import detect_financial_intent
from logic.step_manager import run_steps
from utils.json_formatter import format_json


class UserInput(BaseModel):
    user_text: str


app = FastAPI(title="Financial Crisis Support AI")



@app.post("/crisis-support")
def crisis_support(data: UserInput):

    user_text = data.user_text

    mood = detect_mood(user_text)
    intent, shock = detect_financial_intent(user_text)
    risk_level = safety_router(user_text, mood, shock)

    result = run_steps(user_text, mood, intent, shock, risk_level)

    return format_json(result)


@app.get("/")
def home():
    return {"message": "Financial Crisis Support AI is running"}
