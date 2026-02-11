# Quick Start Guide: Memory-Enabled Crisis Assistant

## Running the Application

### Start the Streamlit UI

```bash
cd /Users/bhomikvarshney/Desktop/AmuHacks
streamlit run app.py
```

Access at: **http://localhost:8501**

### Run Memory Tests

```bash
python test_memory.py
```

## Using the UI

### 1. Initial Assessment

1. Enter medical situation in text area
2. Click **"Get Immediate Actions"**
3. View:
   - Severity level (color-coded)
   - Crisis type
   - Immediate action steps
   - Escalation requirements

### 2. Complete Steps

- Each step shows:
  - ⚠️ **CRITICAL** badge (if urgent)
  - 🔄 **REPEATABLE** badge (if can be repeated)
  - ✅ **COMPLETED** badge (if marked done)
  - ⏱️ Duration estimate

- Click **"✓ Mark Step X as Completed"** to track progress
- Completed steps persist through rechecks

### 3. Symptom Worsening Check

If symptoms worsen, click one of:

- **"✅ Yes, symptoms are worsening"** → Escalates severity, adds emergency actions
- **"❓ I'm not sure"** → Adds monitoring/verification steps
- **"⛔ No, symptoms are stable"** → Maintains current plan

### 4. View Memory State

Expand **"🧠 Memory State (Debug)"** to see:

- `completed_steps`: Array of finished step IDs
- `previous_severity`: Last assessed severity
- `escalation_history`: Record of escalation decisions

## Memory Features

### What's Tracked

✅ **Completed Steps** - Which actions have been done  
✅ **Severity History** - How severity has changed  
✅ **Escalation Record** - When professional help was deemed necessary

### Safety Guarantees

🛡️ **Severity cannot decrease** - No false reassurance  
🛡️ **Escalation stays required** - Professional help recommendation persists  
🛡️ **Valid steps only** - Only real action IDs tracked

## Code Usage

### Programmatic Access

```python
from agent_graph import run_crisis_assessment, run_worsening_recheck

# Initial assessment
result = run_crisis_assessment("Child has high fever of 103°F")

print(f"Severity: {result['severity_level']}")
print(f"Escalation: {result['escalation']['required']}")
print(f"Actions: {len(result['immediate_actions'])} steps")

# Mark steps completed
result['completed_steps'] = [1, 2]

# Recheck if symptoms worsen
recheck = run_worsening_recheck(result, "yes")

print(f"New severity: {recheck['severity_level']}")
print(f"Previous: {recheck['previous_severity']}")
print(f"Completed preserved: {recheck['completed_steps']}")
```

### State Validation

```python
from agent_graph import validate_state

state = {
    'severity_level': 'moderate',
    'previous_severity': 'critical',  # Invalid!
    'escalation_required': False,
    'escalation_history': [{'required': True}]  # Conflict!
}

validated = validate_state(state)

# Result:
# severity_level = 'critical'  (restored)
# escalation_required = True   (enforced)
```

## Testing Scenarios

### Test 1: Basic Memory

```python
# Initial high severity
result = run_crisis_assessment("Severe chest pain radiating to arm")
assert result['severity_level'] == 'critical'
assert result['escalation']['required'] == True

# Complete steps
result['completed_steps'] = [1, 2, 3]

# Recheck maintains memory
recheck = run_worsening_recheck(result, "no")
assert recheck['completed_steps'] == [1, 2, 3]
assert recheck['escalation']['required'] == True  # Immutable
```

### Test 2: Severity Escalation

```python
# Start moderate
result = run_crisis_assessment("Mild headache for 2 hours")
assert result['severity_level'] == 'moderate'

# Symptoms worsen
recheck = run_worsening_recheck(result, "yes")
assert recheck['severity_level'] in ['high', 'critical']
assert recheck['previous_severity'] == 'moderate'  # Tracked
```

### Test 3: Invalid Downgrade Prevention

```python
state = {
    'severity_level': 'low',
    'previous_severity': 'high',
    'completed_steps': [],
    'escalation_history': []
}

validated = validate_state(state)
assert validated['severity_level'] == 'high'  # Cannot downgrade
```

## Debugging

### View Full State

```python
import json
result = run_crisis_assessment("Medical situation")
print(json.dumps(result, indent=2))
```

### Check Validation Rules

```python
from agent_graph import validate_state

test_state = {...}  # Your state
validated = validate_state(test_state)

# Compare before/after
print("Original:", test_state)
print("Validated:", validated)
```

### Inspect Checkpointing

```python
# States are automatically checkpointed with thread_id
# View in agent_graph.py:116-119
config = {"configurable": {"thread_id": "crisis_session"}}
result = app.invoke(initial_state, config=config)
```

## Common Issues

### Issue: Completed steps reset after recheck

**Solution:** Ensure original result is passed to `run_worsening_recheck()`

### Issue: Severity downgraded

**Solution:** Check if `validate_state()` is being called. Should prevent this.

### Issue: Escalation removed

**Solution:** `escalation_history` should persist. Verify `validate_state()` wrapper.

### Issue: Memory not showing in UI

**Solution:** Check format_output.py includes memory fields in final_output

## Architecture Summary

```
User Input → LangGraph Workflow
              ↓
         [normalize] → validate_state()
              ↓
         [classify] → validate_state()
              ↓
         [assess_risk] → escalation_history tracking
              ↓
         [plan_actions] → generate steps
              ↓
         [format_output] → add memory fields
              ↓
         Final Output (with memory)
              ↓
         Streamlit UI (track completion)
              ↓
         Symptom Recheck (preserve memory)
              ↓
         Updated Output (memory maintained)
```

## Key Files

- **agent_graph.py** - Core workflow, GraphState, validation
- **nodes/** - Individual processing nodes
- **app.py** - Streamlit UI with memory tracking
- **test_memory.py** - Comprehensive memory tests
- **MEMORY_IMPLEMENTATION.md** - Detailed documentation

## Support

For issues or questions:

1. Run `python test_memory.py` to verify memory system
2. Check `MEMORY_IMPLEMENTATION.md` for architecture details
3. Inspect state with debug panel in UI

## Checklist: Is Memory Working?

Run through this checklist:

- [ ] `python test_memory.py` passes all 6 tests
- [ ] UI shows completed step badges (green ✅)
- [ ] Severity cannot be downgraded to lower level
- [ ] Escalation requirement persists across rechecks
- [ ] Previous severity tracked when symptoms worsen
- [ ] Memory state visible in debug expander
- [ ] Completed steps preserved after recheck

If all checked, memory system is working correctly! 🎉
