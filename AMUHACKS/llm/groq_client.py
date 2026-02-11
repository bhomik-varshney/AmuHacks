import os
import json
from groq import Groq
from config.settings import MODEL_NAME
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)

with open("llm/system_instruction.txt", encoding="utf-8") as f:
    SYSTEM = f.read()

with open("llm/few_shot_examples.json", encoding="utf-8") as f:
    FEW_SHOTS = json.load(f)


def call_llm(user_text, mood, intent, shock, step):

    messages = [
        {"role": "system", "content": SYSTEM}
    ]

    # Few shot examples
    for ex in FEW_SHOTS:
        messages.append({
            "role": "user",
            "content": ex["user"]
        })

        messages.append({
            "role": "assistant",
            "content": json.dumps(ex["assistant"])
        })

    prompt = f"""
User situation: {user_text}

Mood: {mood}
Financial intent: {intent}
Shock category: {shock}
Current step: {step}

Return ONLY valid JSON.
Do not explain.
Follow the schema strictly.
"""

    messages.append({
        "role": "user",
        "content": prompt
    })

    try:

        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        content = res.choices[0].message.content

        return json.loads(content)

    except json.JSONDecodeError:

        # 🔥 LLM returned garbage
        return {
            "step": step,
            "instruction": "Take a slow breath. We will handle this together.",
            "timer_seconds": 30,
            "actionable": True,
            "resolved": False,
            "_internal_status": "llm_json_error"
        }

    except Exception as e:

        # 🔥 API failure fallback (VERY IMPORTANT FOR DEMO)

        return {
            "step": step,
            "instruction": "Our system is experiencing a delay. Please pause and avoid financial decisions for a moment.",
            "timer_seconds": 30,
            "actionable": False,
            "resolved": False,
            "_internal_status": str(e)
        }
