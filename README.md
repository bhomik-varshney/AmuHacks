# 🏥 Personal Crisis Decision Assistant

An agentic AI application for medical crisis assessment and decision support, built with LangGraph and Groq AI.

## 📋 Overview

This application helps individuals assess medical emergencies, reduce panic, and make informed decisions through a conversational AI assistant that provides structured JSON responses with:

- Crisis severity assessment
- Immediate action steps
- Safety warnings
- Escalation recommendations

## ⚠️ Important Disclaimer

**This assistant does not replace medical professionals. In any emergency, call emergency services immediately.**

## 🎯 Features

- **Multi-Node Agentic Architecture** using LangGraph
- **5-Stage Assessment Pipeline**:
  1. Input Normalization
  2. Crisis Classification
  3. Risk Assessment
  4. Action Planning
  5. Structured Output Generation
- **Powered by Groq AI** (llama-3.3-70b-versatile)
- **Structured JSON Output** for programmatic use
- **Interactive Streamlit UI** with color-coded severity indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**

   ```bash
   cd /Users/bhomikvarshney/Desktop/AmuHacks
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```bash
   streamlit run app.py
   ```

4. **Access the UI:**
   - The browser should open automatically
   - Or navigate to: `http://localhost:8501`

## 📁 Project Structure

```
AmuHacks/
├── app.py                 # Streamlit UI
├── agent_graph.py         # LangGraph workflow definition
├── config.py              # Groq API configuration
├── schema.py              # JSON output schema (Pydantic models)
├── requirements.txt       # Python dependencies
├── nodes/                 # Agent nodes
│   ├── __init__.py
│   ├── normalize_input.py    # Input cleaning & validation
│   ├── classify.py           # Crisis type & severity classification
│   ├── assess_risk.py        # Safety & escalation assessment
│   ├── plan_actions.py       # Action planning & recommendations
│   └── format_output.py      # JSON response assembly
└── README.md
```

## 🔄 Agent Workflow

```
START
  ↓
┌─────────────────────┐
│ Input Normalization │ → Cleans and validates input
└─────────────────────┘
  ↓
┌─────────────────────┐
│ Crisis Classification│ → Identifies crisis type and severity
└─────────────────────┘
  ↓
┌─────────────────────┐
│  Risk Assessment    │ → Checks red flags, determines escalation
└─────────────────────┘
  ↓
┌─────────────────────┐
│  Action Planning    │ → Generates immediate actions
└─────────────────────┘
  ↓
┌─────────────────────┐
│  Format Output      │ → Assembles JSON response
└─────────────────────┘
  ↓
END
```

## 📊 JSON Output Schema

```json
{
  "user_prompt": "<original user input>",
  "crisis_type": "<identified medical issue>",
  "severity_level": "low | moderate | high | critical",
  "assessment": "<calm explanation>",
  "immediate_actions": [
    "Step 1...",
    "Step 2..."
  ],
  "do_not_do": [
    "Unsafe action 1...",
    "Unsafe action 2..."
  ],
  "escalation": {
    "required": true/false,
    "who_to_contact": ["ambulance", "hospital", "relative"],
    "reason": "<escalation reason>"
  },
  "reassurance_message": "<supportive message>"
}
```

## 💡 Example Usage

### Via UI:

1. Open the Streamlit app
2. Enter a medical situation: _"My father is having chest pain and sweating heavily"_
3. Click "Assess Crisis"
4. View structured assessment with severity, actions, and escalation recommendations

### Programmatic Usage:

```python
from agent_graph import run_crisis_assessment

result = run_crisis_assessment(
    "My father is having chest pain and sweating a lot"
)

print(result)  # Returns JSON dict
```

## 🎨 UI Features

- **Color-coded severity badges**:
  - 🔴 Critical (red)
  - 🟠 High (orange)
  - 🟡 Moderate (yellow)
  - 🟢 Low (green)
- **Formatted action steps** with numbered instructions
- **Safety warnings** highlighting dangerous actions to avoid
- **JSON viewer** with download capability
- **Debug panel** showing agent graph transitions
- **Example scenarios** for quick testing

## 🔧 Configuration

API settings are in [config.py](config.py):

- Groq API key: Pre-configured
- Model: `llama-3.3-70b-versatile`
- Temperature: 0.3 (for consistent outputs)
- Max tokens: 2000

## 🛡️ Safety & Ethics

- **No Medical Diagnosis**: Only provides guidance, not diagnosis
- **Conservative Escalation**: Errs on the side of safety
- **No Drug Recommendations**: Never suggests medications or dosages
- **Clear Disclaimers**: Emphasizes the need for professional care
- **Panic Reduction**: Uses calm, supportive language

## 📝 Severity Classification

- **Low**: Minor issues, no immediate danger
- **Moderate**: Concerning symptoms, needs attention soon
- **High**: Serious symptoms, needs urgent care
- **Critical**: Life-threatening, needs immediate emergency response

## 🚨 Red Flag Symptoms (Auto-Escalate)

- Chest pain with sweating
- Difficulty breathing/choking
- Unconsciousness
- Severe bleeding
- Stroke symptoms (FAST)
- Severe allergic reactions
- Seizures
- Suspected poisoning

## 🧪 Testing

Run a quick test of the agent:

```bash
python agent_graph.py
```

This will process a sample input and display the JSON output.

## 📦 Dependencies

- **langgraph**: Agent workflow orchestration
- **langchain**: LLM framework
- **langchain-groq**: Groq AI integration
- **groq**: Groq Cloud API client
- **pydantic**: Data validation
- **streamlit**: Web UI framework

## 🤝 Contributing

This project was built for **AmuHacks** hackathon.

**Problem Statement**: PS-01: Personal Crisis Decision Assistant  
**Category**: Citizens  
**Theme**: Self-Reliance & Emergency Readiness

## 📄 License

Built for educational and emergency preparedness purposes.

## 🆘 Emergency Contacts

- **US/Canada**: 911
- **Europe**: 112
- **India**: 108 (Ambulance) / 102 (Medical Emergency)

---

**Remember**: This tool is for guidance only. Always prioritize professional medical care in emergencies.
