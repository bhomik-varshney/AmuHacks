"""
Configuration for Groq Cloud API and application settings
"""

import os
from groq import Groq
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

# Load environment variables
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Langfuse Configuration
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

# Initialize Langfuse client
langfuse_client = None
langfuse_handler = None
if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    try:
        langfuse_client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST,
            flush_at=1,  # Flush immediately for debugging
            flush_interval=0.5  # Flush every 0.5 seconds
        )
        # Import LangChain callback handler
        from langfuse.callback import CallbackHandler
        langfuse_handler = CallbackHandler(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST
        )
        print("✅ Langfuse observability enabled")
    except Exception as e:
        print(f"⚠️ Langfuse initialization failed: {e}")
        langfuse_client = None
        langfuse_handler = None
else:
    print("⚠️ Langfuse credentials not found - running without observability")

# Initialize Groq client
def get_groq_client():
    """Initialize and return Groq client"""
    return Groq(api_key=GROQ_API_KEY)

# System prompts for different nodes
SYSTEM_PROMPTS = {
    "input_normalization": """You are a medical crisis input processor. 
Your task is to clean and normalize user input about medical situations.
Extract the core medical concern and remove irrelevant information.
Keep it brief and focused on the medical symptoms/situation described.
If the input is not medical-related, return: "NON_MEDICAL_INPUT"
""",
    
    "crisis_classification": """You are a medical crisis classifier.
Analyze the normalized input and identify:
1. The type of medical crisis (e.g., cardiac, respiratory, trauma, etc.)
2. The severity level (low, moderate, high, critical)

Severity Guidelines:
- LOW: Minor issues, no immediate danger
- MODERATE: Concerning symptoms, needs attention soon
- HIGH: Serious symptoms, needs urgent care
- CRITICAL: Life-threatening, needs immediate emergency response

Be conservative - when in doubt, escalate severity.
""",
    
    "risk_assessment": """You are a medical safety risk assessor.
Identify red-flag symptoms that require immediate escalation:
- Chest pain with sweating
- Difficulty breathing/choking
- Unconsciousness
- Severe bleeding
- Stroke symptoms (FAST: Face, Arms, Speech, Time)
- Severe allergic reactions
- Seizures
- Suspected poisoning

Return whether emergency escalation is REQUIRED or NOT_REQUIRED.
""",
    
    "action_planning": """You are a medical crisis action planner.
Create clear, step-by-step immediate actions for the situation.
Also list dangerous actions to avoid (do_not_do).

Guidelines:
- Actions must be clear and actionable
- Focus on immediate safety
- Include monitoring steps
- Include positioning/comfort measures
- NO medical diagnosis or drug dosages
- Keep calm and supportive tone
"""
}

# Application settings
APP_CONFIG = {
    "model": GROQ_MODEL,
    "temperature": 0.3,  # Low temperature for consistent outputs
    "max_tokens": 2000,
    "top_p": 0.9,
    "disclaimer": "⚠️ DISCLAIMER: This assistant does not replace medical professionals. In any emergency, call emergency services immediately."
}
