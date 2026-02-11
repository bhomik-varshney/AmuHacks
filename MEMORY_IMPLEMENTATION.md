# Memory & State Management Implementation

## Overview

This document describes the deterministic, state-based memory system implemented for the medical crisis decision assistant using LangGraph's checkpointing capabilities.

## Architecture

### 1. GraphState (Single Source of Truth)

Located in `agent_graph.py`, the `GraphState` TypedDict defines all state fields:

```python
class GraphState(TypedDict):
    # Core fields
    user_input: str
    normalized_input: str
    crisis_type: str
    severity_level: str
    assessment: str
    immediate_actions: List[dict]
    do_not_do: List[str]
    escalation_required: bool
    who_to_contact: List[str]
    escalation_reason: str
    reassurance_message: str
    error: str
    final_output: dict
    symptom_recheck: dict

    # Memory fields
    completed_steps: List[str]          # Track which action steps are done
    previous_severity: Optional[str]    # Track severity changes
    escalation_history: List[dict]      # Immutable escalation record
```

### 2. State Validation (`validate_state` function)

Enforces safety rules and data integrity:

**Safety Rules:**

- ✅ **Severity cannot decrease** - Once assessed as high/critical, cannot downgrade to moderate/low
- ✅ **Escalation immutability** - Once escalation is required, it stays required
- ✅ **Completed steps validation** - Only valid step IDs are tracked

**Code Location:** `agent_graph.py:16-43`

```python
def validate_state(state: dict) -> dict:
    # Initialize memory fields if missing
    # Validate completed_steps reference real actions
    # Prevent severity downgrade
    # Prevent escalation removal
    return state
```

### 3. LangGraph Checkpointing

Uses `MemorySaver` for in-memory checkpointing:

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

**Benefits:**

- State persists across workflow runs
- Session-based tracking with `thread_id`
- Automatic state snapshots at each node
- Enables time-travel debugging

### 4. Validation Wrappers

All nodes are wrapped with validation:

```python
def validated_node(node_func):
    def wrapper(state):
        state = validate_state(state)  # Validate before
        result = node_func(state)
        return validate_state(result)   # Validate after
    return wrapper
```

This ensures **every node** respects memory rules.

### 5. Memory Integration in Nodes

#### assess_risk.py

Tracks escalation history:

```python
if state.get('escalation_required'):
    state['escalation_history'].append({
        'timestamp': 'current',
        'required': True,
        'reason': state.get('escalation_reason', '')
    })
```

#### format_output.py

Includes memory fields in final output:

```python
state["final_output"]["completed_steps"] = state.get("completed_steps", [])
state["final_output"]["previous_severity"] = state.get("previous_severity")
state["final_output"]["escalation_history"] = state.get("escalation_history", [])
```

#### worsening_check.py

Preserves and updates memory during recheck:

```python
def run_worsening_recheck(original_result: dict, user_response: str) -> dict:
    # Extract memory from original result
    completed_steps = original_result.get('completed_steps', [])
    previous_severity = original_result.get('severity_level')

    # Preserve in recheck state
    state['completed_steps'] = completed_steps
    state['previous_severity'] = previous_severity
```

### 6. UI Integration (app.py)

**Session State Tracking:**

```python
if 'completed_steps' not in st.session_state:
    st.session_state.completed_steps = []
```

**Step Completion:**

```python
if st.button(f"✓ Mark Step {step_id} as Completed"):
    st.session_state.completed_steps.append(step_id)
    result['completed_steps'] = st.session_state.completed_steps
    st.rerun()
```

**Visual Feedback:**

- ✅ Green badge for completed steps
- ⚠️ Red badge for critical steps
- 🔄 Blue badge for repeatable steps

**Memory State Viewer:**

```python
with st.expander("🧠 Memory State (Debug)", expanded=False):
    st.json({
        "completed_steps": result.get('completed_steps', []),
        "previous_severity": result.get('previous_severity'),
        "escalation_history": result.get('escalation_history', [])
    })
```

## Testing

### Test Suite: test_memory.py

6 comprehensive tests validate memory behavior:

1. **State Validation** - Safety rules enforcement
2. **Memory Field Initialization** - All fields present in output
3. **Step Completion Tracking** - Completed steps preserved across rechecks
4. **Severity History** - Previous severity tracked when updated
5. **Escalation Immutability** - Escalation cannot be removed
6. **Checkpointing** - Session state persists with thread_id

**Run Tests:**

```bash
python test_memory.py
```

**Expected Output:**

```
✅ State validation enforces safety rules!
✅ Memory fields properly initialized!
✅ Step completion memory maintained!
✅ Severity history properly tracked!
✅ Escalation immutability enforced!
✅ Checkpointing maintains state across operations!
```

## Key Design Decisions

### Why NOT Conversational Memory?

❌ No chat history in prompts  
❌ No semantic memory search  
❌ No RAG for memory retrieval

✅ **Structured state only**  
✅ **Deterministic flow**  
✅ **Single source of truth**

### Why LangGraph Checkpointing?

- **Deterministic:** Same input → Same output (given same state)
- **Traceable:** Every state change logged
- **Debuggable:** Can inspect state at any point
- **Testable:** Memory behavior is verifiable

### Safety-First Approach

- **No severity downgrade:** Protects against false reassurance
- **Escalation immutability:** Once professional help needed, always needed
- **Completed steps validation:** Only real actions tracked

## Usage Example

### 1. Initial Assessment

```python
result = run_crisis_assessment("Child has high fever of 103°F")
# result['severity_level'] = 'high'
# result['completed_steps'] = []
# result['escalation_required'] = True
```

### 2. Complete Steps

```python
# User completes steps 1 and 2
completed_steps = [1, 2]
result['completed_steps'] = completed_steps
```

### 3. Symptom Worsening Recheck

```python
recheck_result = run_worsening_recheck(result, "yes")
# recheck_result['severity_level'] = 'critical'  # Increased
# recheck_result['previous_severity'] = 'high'    # Tracked
# recheck_result['completed_steps'] = [1, 2]      # Preserved
# recheck_result['escalation_required'] = True    # Maintained
```

### 4. Memory Validation

```python
validated_state = validate_state(recheck_result)
# Ensures:
# - severity_level >= previous_severity
# - escalation_required stays True
# - completed_steps are valid step IDs
```

## Files Modified

1. **agent_graph.py**
   - Added `GraphState` TypedDict
   - Implemented `validate_state()` function
   - Added validation wrappers
   - Integrated `MemorySaver` checkpointing

2. **nodes/assess_risk.py**
   - Added escalation history tracking

3. **nodes/format_output.py**
   - Included memory fields in final output

4. **nodes/worsening_check.py**
   - Preserved memory during rechecks

5. **app.py**
   - Added session state tracking
   - Implemented step completion buttons
   - Added memory state viewer

6. **test_memory.py**
   - Created comprehensive test suite

## Benefits

### For Users

- 🎯 **Consistency:** Decisions don't contradict previous assessments
- 🛡️ **Safety:** Critical information never forgotten
- 📊 **Progress:** Clear view of completed steps
- 🔍 **Transparency:** Memory state visible in debug panel

### For Developers

- 🧪 **Testable:** Deterministic behavior
- 🐛 **Debuggable:** State inspection at any point
- 🔒 **Safe:** Validation enforces rules
- 📈 **Scalable:** Easy to add new memory fields

## Future Enhancements

1. **Persistent Storage:** Replace `MemorySaver` with database checkpointer
2. **Multi-Session:** Track multiple patients with different `thread_id`s
3. **Temporal Queries:** "What was severity 5 minutes ago?"
4. **State Rollback:** Undo recent changes
5. **Memory Analytics:** Track common action sequences

## Conclusion

This memory implementation provides **deterministic, state-based tracking** without relying on conversational memory or LLM-based retrieval. All memory is stored in structured `GraphState`, validated by safety rules, and persisted through LangGraph checkpointing.

The system ensures that once critical information is assessed (high severity, escalation required), it cannot be accidentally downgraded, providing a **safety-first approach** to medical crisis assistance.
