"""
Test script for the updated immediate actions format
Validates that all fields are present and properly structured
"""

import json
from agent_graph import run_crisis_assessment

def validate_action_structure(action, step_num):
    """Validate a single action has all required fields"""
    required_fields = [
        'step_id', 'title', 'instruction', 'duration_seconds',
        'user_confirmation_required', 'critical', 'repeatable'
    ]
    
    errors = []
    
    # Check all required fields exist
    for field in required_fields:
        if field not in action:
            errors.append(f"Step {step_num}: Missing field '{field}'")
    
    # Validate field types
    if 'step_id' in action and not isinstance(action['step_id'], int):
        errors.append(f"Step {step_num}: step_id must be integer")
    
    if 'title' in action and not isinstance(action['title'], str):
        errors.append(f"Step {step_num}: title must be string")
    
    if 'instruction' in action and not isinstance(action['instruction'], str):
        errors.append(f"Step {step_num}: instruction must be string")
    
    if 'duration_seconds' in action:
        if action['duration_seconds'] is not None:
            if not isinstance(action['duration_seconds'], int):
                errors.append(f"Step {step_num}: duration_seconds must be integer or null")
            elif not (5 <= action['duration_seconds'] <= 120):
                errors.append(f"Step {step_num}: duration_seconds should be between 5-120")
    
    if 'user_confirmation_required' in action and not isinstance(action['user_confirmation_required'], bool):
        errors.append(f"Step {step_num}: user_confirmation_required must be boolean")
    
    if 'critical' in action and not isinstance(action['critical'], bool):
        errors.append(f"Step {step_num}: critical must be boolean")
    
    if 'repeatable' in action and not isinstance(action['repeatable'], bool):
        errors.append(f"Step {step_num}: repeatable must be boolean")
    
    return errors


def test_crisis_scenario(description, expected_severity=None):
    """Test a crisis scenario"""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"{'='*70}")
    
    try:
        result = run_crisis_assessment(description)
        
        # Print summary
        print(f"\n✓ Crisis Type: {result['crisis_type']}")
        print(f"✓ Severity: {result['severity_level']}")
        print(f"✓ Escalation Required: {result['escalation']['required']}")
        
        # Validate immediate actions
        actions = result.get('immediate_actions', [])
        print(f"\n✓ Number of Actions: {len(actions)}")
        
        # Check action count
        if len(actions) < 3 or len(actions) > 7:
            print(f"❌ ERROR: Must have 3-7 actions, got {len(actions)}")
            return False
        
        # Validate each action
        all_valid = True
        has_critical = False
        
        print("\nAction Details:")
        for i, action in enumerate(actions, 1):
            errors = validate_action_structure(action, i)
            
            if errors:
                all_valid = False
                print(f"\n❌ Step {i} Validation Errors:")
                for error in errors:
                    print(f"   - {error}")
            else:
                print(f"\n✓ Step {i}: {action['title']}")
                print(f"  - Instruction: {action['instruction'][:60]}...")
                print(f"  - Duration: {action['duration_seconds']}s" if action['duration_seconds'] else "  - Duration: Manual confirmation")
                print(f"  - Critical: {'YES' if action['critical'] else 'No'}")
                print(f"  - Repeatable: {'YES' if action['repeatable'] else 'No'}")
                
                if action['critical']:
                    has_critical = True
        
        # Check for at least one critical step in high/critical severity
        if result['severity_level'] in ['high', 'critical'] and not has_critical:
            print(f"\n⚠️  WARNING: Severity is {result['severity_level']} but no critical steps found")
        
        if all_valid:
            print(f"\n✅ All validation checks passed!")
            return True
        else:
            print(f"\n❌ Validation failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run comprehensive tests"""
    print("="*70)
    print("IMMEDIATE ACTIONS STRUCTURE VALIDATION TEST")
    print("="*70)
    
    test_scenarios = [
        ("My father is having chest pain and sweating heavily", "critical"),
        ("Child fell and has a deep cut that won't stop bleeding", "high"),
        ("Difficulty breathing after eating peanuts", "critical"),
        ("High fever of 104°F for 2 days", "moderate"),
        ("Minor cut on finger, bleeding slightly", "low"),
    ]
    
    results = []
    for scenario, expected_severity in test_scenarios:
        passed = test_crisis_scenario(scenario, expected_severity)
        results.append((scenario, passed))
    
    # Summary
    print(f"\n\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for scenario, passed_test in results:
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{status}: {scenario[:60]}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The immediate actions structure is valid.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")


if __name__ == "__main__":
    main()
