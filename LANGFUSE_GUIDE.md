# Langfuse Observability Guide

## 🎯 Overview

Your Medical Crisis Decision Assistant now has full observability with Langfuse, allowing you to track, analyze, and debug every assessment.

## 📊 Accessing Langfuse Dashboard

1. **Open Langfuse**: Navigate to http://localhost:3000
2. **Login**: Use your credentials (if first time, you'll need to create an account)
3. **View Traces**: Click on "Traces" in the left sidebar

## 🔍 What You Can See

### Traces

Each crisis assessment creates a trace containing:

- **Input**: User's description of the medical situation
- **Output**: Complete assessment with actions and severity
- **Metadata**:
  - Execution time
  - Severity level (low, moderate, high, critical)
  - Crisis type (cardiac, respiratory, trauma, etc.)
  - Escalation status
- **Tags**: `crisis`, `medical`, `assessment`

### Sessions

All assessments from the same Streamlit session are grouped together, allowing you to:

- Track user journeys
- See how assessments change over time
- Identify patterns in crisis types

### Spans

Each trace contains a `langgraph_execution` span that shows:

- Individual node executions
- State transitions
- LLM calls via the LangChain callback handler

## 📈 Key Metrics to Monitor

1. **Severity Distribution**
   - How many critical vs low severity cases
   - Helps identify if the system is over/under-escalating

2. **Execution Time**
   - Average time per assessment
   - Identify slow queries or bottlenecks

3. **Crisis Types**
   - Most common medical situations
   - Helps improve system training

4. **Escalation Rate**
   - How often emergency services are recommended
   - Critical safety metric

## 🛠️ Troubleshooting

### No Traces Appearing?

1. **Check Connection**:

   ```bash
   python -c "from config import langfuse_client; print('Connected' if langfuse_client else 'Not connected')"
   ```

2. **Verify Credentials**: Check your `.env` file has:
   - LANGFUSE_PUBLIC_KEY
   - LANGFUSE_SECRET_KEY
   - LANGFUSE_HOST=http://localhost:3000

3. **Test Trace**:
   ```bash
   python -c "from agent_graph import run_crisis_assessment; run_crisis_assessment('test')"
   ```

### Traces Are Delayed?

- Traces are flushed immediately (flush_at=1)
- Refresh the Langfuse dashboard (F5)
- Check the console for "✅ Trace flushed" messages

## 🎨 Advanced Features

### Custom Metadata

The system automatically tracks:

- Session IDs for multi-turn conversations
- Crisis severity levels
- Escalation decisions
- Execution timestamps

### LangChain Integration

The `CallbackHandler` automatically tracks:

- All LLM calls to Groq
- Token usage
- Model responses
- Chain executions

## 🚀 Production Tips

1. **Set Sampling**: In production, you may want to sample traces:

   ```python
   langfuse_client = Langfuse(
       public_key=LANGFUSE_PUBLIC_KEY,
       secret_key=LANGFUSE_SECRET_KEY,
       host=LANGFUSE_HOST,
       sample_rate=0.1  # Sample 10% of traces
   )
   ```

2. **Monitor Costs**: Track token usage in Langfuse to optimize costs

3. **Set Alerts**: Use Langfuse's webhook feature to get notified of critical issues

4. **Export Data**: Export traces for compliance or further analysis

## 📝 Example Queries

Navigate to the Traces page and filter by:

- **Critical Cases**: `metadata.severity_level = "critical"`
- **Slow Assessments**: `metadata.execution_time_seconds > 5`
- **Cardiac Issues**: `metadata.crisis_type = "cardiac"`
- **Today's Traces**: Use the date picker

## 🔗 Resources

- Langfuse Docs: https://langfuse.com/docs
- LangChain Integration: https://langfuse.com/docs/integrations/langchain
- API Reference: https://langfuse.com/docs/api

---

**Need Help?** The traces contain the complete execution flow, making debugging much easier!
