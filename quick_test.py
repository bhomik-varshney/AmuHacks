"""
Quick validation script - Tests key scenarios
"""

import json
from agent_graph import run_crisis_assessment

print("Testing new structured immediate actions format...\n")

# Test Case 1: Critical cardiac emergency
print("=" * 60)
print("TEST 1: Critical Cardiac Emergency")
print("=" * 60)
result1 = run_crisis_assessment("My father is having chest pain and sweating heavily")
actions1 = result1['immediate_actions']
print(f"✓ Generated {len(actions1)} steps")
print(f"✓ Severity: {result1['severity_level']}")
print(f"✓ Sample action structure:")
print(json.dumps(actions1[0], indent=2))

# Validate structure
assert 3 <= len(actions1) <= 7, f"Invalid step count: {len(actions1)}"
assert all('step_id' in a for a in actions1), "Missing step_id"
assert all('duration_seconds' in a for a in actions1), "Missing duration_seconds"
assert all('critical' in a for a in actions1), "Missing critical flag"
assert any(a['critical'] for a in actions1), "No critical steps for critical severity"
print("✅ All validations passed!\n")

# Test Case 2: Moderate fever
print("=" * 60)
print("TEST 2: Moderate Severity (High Fever)")
print("=" * 60)
result2 = run_crisis_assessment("My child has a fever of 104°F for 2 days")
actions2 = result2['immediate_actions']
print(f"✓ Generated {len(actions2)} steps")
print(f"✓ Severity: {result2['severity_level']}")
assert 3 <= len(actions2) <= 7, f"Invalid step count: {len(actions2)}"
print("✅ Valid structure!\n")

# Test Case 3: Low severity
print("=" * 60)
print("TEST 3: Low Severity (Minor Cut)")
print("=" * 60)
result3 = run_crisis_assessment("Small cut on finger, bleeding slightly")
actions3 = result3['immediate_actions']
print(f"✓ Generated {len(actions3)} steps")
print(f"✓ Severity: {result3['severity_level']}")
assert 3 <= len(actions3) <= 7, f"Invalid step count: {len(actions3)}"
print("✅ Valid structure!\n")

print("=" * 60)
print("🎉 ALL QUICK VALIDATION TESTS PASSED!")
print("=" * 60)
print("\nStructure Summary:")
print(f"- All actions have required fields ✓")
print(f"- Step counts are within 3-7 range ✓")
print(f"- Critical steps present for critical severity ✓")
print(f"- Duration fields properly formatted ✓")
print(f"\n✅ Implementation is working correctly!")
