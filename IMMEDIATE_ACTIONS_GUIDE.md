# Immediate Actions Structure - Implementation Guide

## Overview

The medical crisis assistant now generates **structured immediate action steps** instead of simple text strings. Each action is a JSON object with specific fields for UI integration, timing, and criticality.

## Action Structure

```json
{
  "step_id": 1,
  "title": "Call emergency services",
  "instruction": "Call 911 immediately and describe all symptoms clearly.",
  "duration_seconds": null,
  "user_confirmation_required": false,
  "critical": true,
  "repeatable": false
}
```

## Field Definitions

| Field                        | Type            | Required | Description                                   |
| ---------------------------- | --------------- | -------- | --------------------------------------------- |
| `step_id`                    | integer         | ✅       | Sequential step number (1, 2, 3...)           |
| `title`                      | string          | ✅       | Short action-oriented title (2-5 words)       |
| `instruction`                | string          | ✅       | Clear instruction for untrained civilians     |
| `duration_seconds`           | integer \| null | ✅       | Time in seconds (5-120) or `null` for manual  |
| `user_confirmation_required` | boolean         | ✅       | Whether user must confirm before proceeding   |
| `critical`                   | boolean         | ✅       | Whether this is a life-critical step          |
| `repeatable`                 | boolean         | ✅       | Whether action should be repeated (e.g., CPR) |

## Rules & Constraints

### Count

- **Minimum**: 3 steps
- **Maximum**: 7 steps

### Duration Timing

- Use `null` when no specific timing is needed
- Use realistic values (5-120 seconds) when timing matters
- Examples:
  - `10` seconds for quick checks
  - `60` seconds for monitoring breathing
  - `120` seconds for extended observation
  - `null` for actions like "call ambulance" or "position patient"

### Criticality

- At least **one step must be critical** for high/critical severity
- Critical steps typically include:
  - Calling emergency services
  - Life-saving interventions (CPR, stop bleeding)
  - Ensuring breathing/consciousness

### Repeatability

- Set `true` for actions that should be done repeatedly:
  - Monitoring breathing/pulse
  - CPR cycles
  - Checking consciousness
  - Reassuring patient

### User Confirmation

- Set `false` **ONLY** for urgent actions that cannot wait:
  - Calling ambulance
  - Immediate safety actions (remove from danger)
- Set `true` for all other actions to allow user pacing

## Step Ordering Pattern

1. **Safety First**: Check environment, remove dangers
2. **Position Patient**: Get patient comfortable/safe position
3. **Call for Help**: If escalation required
4. **Immediate Interventions**: Stop bleeding, clear airway, etc.
5. **Monitoring**: Check breathing, consciousness, vital signs
6. **Comfort & Reassurance**: Stay with patient, provide support

## Safety Constraints

❌ **Never include:**

- Medical diagnosis
- Medication dosages or drug names
- Invasive medical procedures
- Actions requiring medical training

✅ **Always assume:**

- User is untrained civilian
- Basic first aid knowledge only
- Access to phone for emergency call
- Patient is conscious unless stated otherwise

## Examples by Severity

### Critical (Cardiac Emergency)

```json
{
  "step_id": 3,
  "title": "Call Ambulance",
  "instruction": "Call 911 immediately and state there is chest pain and sweating.",
  "duration_seconds": null,
  "user_confirmation_required": false,
  "critical": true,
  "repeatable": false
}
```

### High (Severe Bleeding)

```json
{
  "step_id": 4,
  "title": "Apply Direct Pressure",
  "instruction": "Use a clean cloth to apply firm, continuous pressure to the wound.",
  "duration_seconds": 60,
  "user_confirmation_required": true,
  "critical": true,
  "repeatable": false
}
```

### Moderate (High Fever)

```json
{
  "step_id": 2,
  "title": "Monitor Temperature",
  "instruction": "Check temperature every 30 minutes and note if it rises.",
  "duration_seconds": null,
  "user_confirmation_required": true,
  "critical": false,
  "repeatable": true
}
```

### Low (Minor Cut)

```json
{
  "step_id": 1,
  "title": "Clean the wound",
  "instruction": "Rinse the cut gently with clean water for 30 seconds.",
  "duration_seconds": 30,
  "user_confirmation_required": true,
  "critical": false,
  "repeatable": false
}
```

## UI Integration

The Streamlit UI displays actions with:

- **Step badges** showing step number
- **Critical indicators** (red border + badge) for critical steps
- **Repeatable indicators** (green badge) for repeatable actions
- **Timer display** when `duration_seconds` is not null
- **Manual confirmation** when `duration_seconds` is null

## Validation Checklist

Before deployment, verify:

- [ ] All actions have 7 required fields
- [ ] Step count is between 3-7
- [ ] At least one critical step for high/critical severity
- [ ] Duration values are realistic (5-120s) or null
- [ ] No medical diagnosis or drug names
- [ ] Instructions are clear for untrained users
- [ ] Step ordering makes logical sense
- [ ] Repeatable flag is used appropriately

## Testing

Run validation tests:

```bash
python test_actions.py
```

Test individual scenarios:

```bash
python agent_graph.py
```

Launch UI for manual testing:

```bash
streamlit run app.py
```

## Files Modified

1. **schema.py**: Added `ImmediateAction` Pydantic model
2. **nodes/plan_actions.py**: Updated prompt and validation logic
3. **nodes/format_output.py**: Updated fallback handling
4. **app.py**: Enhanced UI with step display, badges, timers
5. **test_actions.py**: Comprehensive validation test suite

---

**Last Updated**: February 11, 2026  
**Status**: ✅ Implemented and tested
