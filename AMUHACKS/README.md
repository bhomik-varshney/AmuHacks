# Financial Crisis Support AI

An AI-powered crisis-support system designed to guide users through **financial distress situations** in a calm, step-by-step, and safety-first manner.
The system combines **rule-based detection**, **LLM-generated guidance**, and **strict safety enforcement** to prevent impulsive decisions during financial shocks.

---

## 🧠 Problem Statement

People facing sudden financial crises (job loss, debt, fraud, salary issues) often panic and make harmful decisions. Existing chatbots either overwhelm users or fail to detect emergency risk.

This project provides:

* Psychological safety
* Structured, time-bound guidance
* Emergency escalation when needed

---

## 🚀 Key Features

* Rule-based **mood detection** (panic, stress, neutral, calm)
* Financial **intent & shock detection**
* Risk-based **safety routing** (low / medium / high / extreme)
* Step-limited **LLM-guided instructions**
* Emergency escalation & helpline recommendations
* Strict **JSON-only output** for reliability
* Streamlit-based UI + FastAPI backend

---

## 🏗️ Project Architecture

```
User Input (Streamlit UI)
        ↓
Rule-based Detection
(mood, intent, shock, safety)
        ↓
Safety Router
(risk classification)
        ↓
LLM (Groq + LLaMA)
(generates calm step instructions)
        ↓
Rule Enforcement
(step limits, timers, emergency)
        ↓
Structured JSON Output
```

---

## 📂 Folder Structure

```
AMUHACKS/
│
├── app.py                  # FastAPI backend entry
├── requirements.txt
├── .env                    # GROQ_API_KEY
│
├── config/
│   ├── constants.py        # Mood, intent, shock configs
│   └── settings.py         # Step & model settings
│
├── detection/
│   ├── mood_detector.py
│   └── financial_intent_detector.py
│
├── emergency/
│   └── financial_emergency.py
│
├── llm/
│   ├── groq_client.py
│   ├── system_instruction.txt
│   └── few_shot_examples.json
│
├── logic/
│   ├── router.py
│   ├── step_manager.py
│   ├── escalation_manager.py
│   ├── reevaluator.py
│   └── timer_decider.py
│
├── schemas/
│   └── request_schema.py
│
├── utils/
│   ├── json_formatter.py
│   └── logger.py
│
└── ui/
    └── streamlit_app.py
```

---

## ⚙️ Tech Stack

* **Backend**: FastAPI
* **Frontend**: Streamlit
* **LLM Provider**: Groq
* **Model**: LLaMA 3.3 (70B)
* **Language**: Python
* **Environment**: Virtualenv

---

## 🔐 Environment Setup

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ How to Run

### 1️⃣ Create Virtual Environment

```
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 2️⃣ Install Dependencies

```
pip install -r requirements.txt
```

### 3️⃣ Run Backend (FastAPI)

```
uvicorn app:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

### 4️⃣ Run Frontend (Streamlit)

```
streamlit run ui/streamlit_app.py
```

---

## 🔄 Workflow Logic

1. User enters financial distress text
2. Mood & intent detected using rules
3. Safety router determines risk level
4. LLM generates **one calm instruction per step**
5. Rules enforce:

   * step limits
   * action readiness
   * emergency escalation
6. JSON response returned to UI

---

## 🚨 Safety Design

* **Extreme risk** → Immediate emergency message
* **High risk** → Reduced steps
* **LLM failure** → Safe fallback instructions
* **User overload prevention** → Timed steps only

---

## 📊 Example Use Cases

* Job loss panic
* Salary not credited
* Online fraud / scam
* Debt & EMI stress
* Trading or crypto loss

---

## 🧩 Why This Project Stands Out

* No agent graphs or heavy orchestration
* Fully explainable rule + LLM hybrid
* Demo-safe with multiple fallbacks
* Practical, real-world crisis handling

---

## 📌 Future Improvements

* Multilingual support
* Voice-based interaction
* Personalized financial recovery plans
* Analytics dashboard for counselors

---


## 🚨 Emergency Contacts 

If the system detects a **high or extreme financial or emotional crisis**, users are advised to immediately seek external help.

**Emergency & Support Helplines:**

* **Cyber Crime Helpline (India): 1930**
  For online fraud, scams, banking or UPI-related issues.

* **Local Emergency Services: 112**
  For immediate danger or safety concerns.

* **Trusted Contact**
  Reach out to a family member, friend, or mentor for immediate support.

> ⚠️ This application is designed to *recommend* emergency support, not replace it.

---

## 📜 License

This project is licensed under the **MIT License**.

You are free to:

* Use
* Copy
* Modify
* Merge
* Publish
* Distribute

Provided that the original author is credited and the license is included.

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## ⚠️ Disclaimer

This system provides **supportive and informational guidance only**. It is **not a substitute** for professional financial, legal, or medical advice.

In emergency situations, always contact official helplines or authorities.
