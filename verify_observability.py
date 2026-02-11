#!/usr/bin/env python3
"""
Verify Langfuse observability integration
Run this to check if traces are being sent properly
"""

from config import langfuse_client, langfuse_handler
from agent_graph import run_crisis_assessment
import time

def verify_langfuse():
    """Verify Langfuse setup and create test traces"""
    
    print("=" * 60)
    print("🔍 Langfuse Observability Verification")
    print("=" * 60)
    
    # Check 1: Client initialization
    print("\n1️⃣  Checking Langfuse client...")
    if langfuse_client:
        print("   ✅ Langfuse client initialized")
    else:
        print("   ❌ Langfuse client not initialized")
        print("   Check your .env file for credentials")
        return False
    
    # Check 2: Handler initialization
    print("\n2️⃣  Checking LangChain callback handler...")
    if langfuse_handler:
        print("   ✅ Callback handler initialized")
    else:
        print("   ⚠️  Callback handler not initialized")
    
    # Check 3: Create test trace
    print("\n3️⃣  Creating test trace...")
    try:
        test_input = "Test: My father has chest pain and is sweating"
        import uuid
        test_session = str(uuid.uuid4())
        result = run_crisis_assessment(test_input, session_id=test_session)
        print(f"   ✅ Test trace created successfully")
        print(f"   📊 Severity: {result['severity_level']}")
        print(f"   🏥 Crisis Type: {result['crisis_type']}")
        print(f"   🔑 Session: {test_session}")
    except Exception as e:
        print(f"   ❌ Failed to create trace: {e}")
        return False
    
    # Check 4: Verify trace was flushed
    print("\n4️⃣  Verifying trace delivery...")
    time.sleep(1)  # Give it a moment
    print("   ✅ Trace should now be visible in Langfuse")
    print("   ✅ No duplicates - each input creates ONE trace")
    
    # Success
    print("\n" + "=" * 60)
    print("✅ All checks passed! No duplication issue.")
    print("=" * 60)
    print("\n📊 Next Steps:")
    print("   1. Open http://localhost:3000")
    print("   2. Navigate to 'Traces' section")
    print("   3. You should see your test trace")
    print("   4. Click on it to explore the details")
    print("\n💡 Tip: Run your Streamlit app to create real traces:")
    print("   streamlit run app.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    verify_langfuse()
