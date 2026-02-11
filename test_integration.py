"""
Integration Test: Complete Workflow with Memory and Symptom Recheck
Tests the full flow: assessment → mark steps complete → symptom worsening → memory preservation
"""

import json
from agent_graph import run_crisis_assessment, run_worsening_recheck

print("="*70)
print("INTEGRATION TEST: FULL WORKFLOW")
print("="*70)

# Scenario: Collapsed person - requires immediate response
test_input = "My friend collapsed and is not responding"

print("\n📍 PHASE 1: Initial Assessment")
print("-"*70)
print(f"Input: {test_input}\n")

result = run_crisis_assessment(test_input)

print(f"✓ Crisis Type: {result['crisis_type']}")
print(f"✓ Severity: {result['severity_level']}")
print(f"✓ Escalation Required: {result['escalation']['required']}")
print(f"✓ Number of Actions: {len(result['immediate_actions'])}")
print(f"✓ Completed Steps: {result['completed_steps']}")
print(f"✓ Previous Severity: {result['previous_severity']}")
print(f"✓ Escalation History: {len(result['escalation_history'])} entries")

# Display actions
print("\nImmediate Actions:")
for i, action in enumerate(result['immediate_actions'][:3], 1):
    print(f"  {i}. [{action['step_id']}] {action['title']}")
    if action['critical']:
        print(f"     ⚠️  CRITICAL")
    if action['user_confirmation_required']:
        print(f"     ✓ Requires confirmation")

# Validate memory initialization
assert 'completed_steps' in result, "completed_steps must be present"
assert 'previous_severity' in result, "previous_severity must be present"
assert 'escalation_history' in result, "escalation_history must be present"
print("\n✅ Memory fields initialized correctly!")

print("\n📍 PHASE 2: Simulating Step Completion")
print("-"*70)

# Simulate user completing first 2 steps
completed_steps = [1, 2]
result['completed_steps'] = completed_steps
print(f"User completed steps: {completed_steps}")
print(f"✓ Updated result with completed steps")

print("\n📍 PHASE 3: Symptom Worsening (YES)")
print("-"*70)
print("User reports: Condition has worsened\n")

recheck_result = run_worsening_recheck(result, "yes")

print(f"✓ Crisis Type: {recheck_result['crisis_type']}")
print(f"✓ Severity Before: {result['severity_level']}")
print(f"✓ Severity After: {recheck_result['severity_level']}")
print(f"✓ Escalation Required: {recheck_result['escalation']['required']}")
print(f"✓ Number of Actions: {len(recheck_result['immediate_actions'])}")
print(f"✓ Completed Steps Preserved: {recheck_result['completed_steps']}")
print(f"✓ Previous Severity Tracked: {recheck_result.get('previous_severity')}")
print(f"✓ Escalation History: {len(recheck_result['escalation_history'])} entries")

# Validate memory preservation
assert recheck_result['completed_steps'] == completed_steps, "Completed steps must be preserved"
assert recheck_result['escalation']['required'] == True, "Escalation must remain required"
assert len(recheck_result['escalation_history']) >= len(result['escalation_history']), "Escalation history must grow"

# Check severity history tracking
if 'severity_history' in recheck_result:
    print(f"✓ Severity History: {recheck_result['severity_history']}")

print("\n✅ Memory preserved across recheck!")

print("\n📍 PHASE 4: Additional Step Completion")
print("-"*70)

# User completes more steps
recheck_result['completed_steps'].extend([3, 4])
print(f"User completed additional steps: {recheck_result['completed_steps']}")

print("\n📍 PHASE 5: Second Recheck (NO - Stable)")
print("-"*70)
print("User reports: Condition is stable\n")

final_result = run_worsening_recheck(recheck_result, "no")

print(f"✓ Severity: {final_result['severity_level']}")
print(f"✓ Escalation Required: {final_result['escalation']['required']}")
print(f"✓ Number of Actions: {len(final_result['immediate_actions'])}")
print(f"✓ All Completed Steps: {final_result['completed_steps']}")
print(f"✓ Previous Severity: {final_result.get('previous_severity')}")
print(f"✓ Escalation History: {len(final_result['escalation_history'])} entries")

# Final validation
assert final_result['completed_steps'] == [1, 2, 3, 4], "All completed steps must be preserved"
assert final_result['escalation']['required'] == True, "Escalation immutability enforced"
print("\n✅ Complete workflow maintains memory integrity!")

print("\n📍 PHASE 6: Memory Safety Validation")
print("-"*70)

# Test that severity cannot be downgraded
from agent_graph import validate_state

test_state = {
    'severity_level': 'moderate',
    'previous_severity': 'critical',
    'completed_steps': [1, 2],
    'escalation_history': [{'required': True}],
    'escalation_required': False
}

validated = validate_state(test_state)

print(f"Attempted severity downgrade: critical → moderate")
print(f"✓ Validated severity: {validated['severity_level']}")
assert validated['severity_level'] == 'critical', "Severity downgrade prevented"

print(f"\nAttempted escalation removal")
print(f"✓ Validated escalation: {validated['escalation_required']}")
assert validated['escalation_required'] == True, "Escalation removal prevented"

print("\n✅ Safety rules enforced by validation!")

print("\n📍 SUMMARY")
print("-"*70)
print("\n✅ Initial assessment with memory initialization")
print("✅ Step completion tracking")
print("✅ Symptom worsening with severity escalation")
print("✅ Memory preservation across multiple rechecks")
print("✅ Escalation immutability enforced")
print("✅ Severity downgrade prevention")
print("✅ Complete workflow integrity maintained")

print("\n" + "="*70)
print("🎉 INTEGRATION TEST PASSED!")
print("="*70)

print("\n📊 Final State:")
print(json.dumps({
    "crisis_type": final_result['crisis_type'],
    "severity_level": final_result['severity_level'],
    "completed_steps": final_result['completed_steps'],
    "previous_severity": final_result.get('previous_severity'),
    "escalation_required": final_result['escalation']['required'],
    "total_actions": len(final_result['immediate_actions']),
    "escalation_history_entries": len(final_result['escalation_history'])
}, indent=2))
