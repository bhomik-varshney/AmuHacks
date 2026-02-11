"""
Streamlit UI for Personal Crisis Decision Assistant
"""

import streamlit as st
import json
import time
import uuid
from agent_graph import run_crisis_assessment, get_graph_visualization
from config import APP_CONFIG

# Initialize session ID if not exists
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Page configuration
st.set_page_config(
    page_title="Medical Crisis Decision Assistant",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .severity-critical {
        background-color: #ff4444;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    .severity-high {
        background-color: #ff8800;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    .severity-moderate {
        background-color: #ffbb00;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    .severity-low {
        background-color: #44cc44;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    .json-container {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        color: #d4d4d4;
        overflow-x: auto;
    }
    .action-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-left: 4px solid #2196F3;
        margin: 10px 0;
        border-radius: 3px;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
        border-radius: 3px;
    }
    .step-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .step-critical {
        border: 3px solid #ff4444;
        background-color: #fff5f5;
    }
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .step-badge {
        background-color: #2196F3;
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        margin-right: 10px;
    }
    .critical-badge {
        background-color: #ff4444;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-left: 10px;
    }
    .repeatable-badge {
        background-color: #4CAF50;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-left: 5px;
    }
    .timer-display {
        background-color: #ff9800;
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 1.5em;
        font-weight: bold;
        text-align: center;
        margin: 15px 0;
    }
    .recheck-box {
        background-color: #e3f2fd;
        padding: 25px;
        border-radius: 10px;
        border: 3px solid #2196F3;
        margin: 25px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .recheck-updated {
        background-color: #fff3e0;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #ff9800;
        margin: 15px 0;
    }
    .severity-change {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🏥 Personal Crisis Decision Assistant")
st.markdown(f"### {APP_CONFIG['disclaimer']}")
st.markdown("---")

# Sidebar for information and debug panel
with st.sidebar:
    st.header("ℹ️ Information")
    st.markdown("""
    **Purpose:** 
    Self-guided medical crisis assessment assistant
    
    **What it does:**
    - Assesses medical emergency severity
    - Provides immediate action steps
    - Recommends escalation when needed
    - Reduces panic with calm guidance
    
    **What it does NOT do:**
    - Medical diagnosis
    - Prescribe medications
    - Replace professional medical care
    """)
    
    st.markdown("---")
    
    show_debug = st.checkbox("🔍 Show Debug Panel", value=False)
    
    if show_debug:
        st.header("Debug Info")
        st.markdown("**Agent Graph Flow:**")
        st.text(get_graph_visualization())
        
        # Show memory state if result exists
        if hasattr(st.session_state, 'last_result') and st.session_state.last_result:
            st.markdown("---")
            st.markdown("**Memory State:**")
            result = st.session_state.last_result
            st.json({
                "completed_steps": result.get("completed_steps", []),
                "severity_history": result.get("severity_history", {}),
                "escalation_count": len(result.get("escalation_history", [])),
                "recheck_performed": result.get("symptom_recheck", {}).get("asked", False)
            })

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Describe the Situation")
    
    # Example scenarios
    with st.expander("💡 Example Scenarios"):
        st.markdown("""
        - "My father is having chest pain and sweating heavily"
        - "Child fell and has a deep cut that won't stop bleeding"
        - "Difficulty breathing after eating peanuts"
        - "Grandmother suddenly can't move her left arm"
        - "High fever of 104°F for 2 days"
        - "Person fell and hit their head, now feeling dizzy"
        """)
    
    # Input text area
    user_input = st.text_area(
        "Describe the medical situation:",
        height=150,
        placeholder="Example: My father is having chest pain and sweating a lot. He's also feeling nauseous.",
        key="crisis_input"
    )
    
    # Submit button
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        submit_button = st.button("🚨 Assess Crisis", type="primary", use_container_width=True, key="assess_crisis_btn")
    with col_btn2:
        clear_button = st.button("Clear", use_container_width=True, key="clear_input_btn")
    
    if clear_button:
        if 'crisis_input' in st.session_state:
            del st.session_state.crisis_input
        st.rerun()

with col2:
    st.header("📊 Assessment Results")
    
    # Initialize recheck state
    if 'recheck_done' not in st.session_state:
        st.session_state.recheck_done = False
    if 'show_recheck' not in st.session_state:
        st.session_state.show_recheck = False
    
    if submit_button:
        if not user_input or user_input.strip() == "":
            st.error("⚠️ Please describe the medical situation first.")
        else:
            with st.spinner("🔄 Analyzing crisis situation..."):
                try:
                    # Run the agent with session tracking
                    result = run_crisis_assessment(user_input, session_id=st.session_state.session_id)
                    
                    # Store in session state
                    st.session_state.last_result = result
                    st.session_state.recheck_done = False
                    st.session_state.show_recheck = False
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.last_result = None

# Display results
if hasattr(st.session_state, 'last_result') and st.session_state.last_result:
    result = st.session_state.last_result
    
    # Initialize completed steps in session state
    if 'completed_steps' not in st.session_state:
        st.session_state.completed_steps = result.get('completed_steps', [])
    
    # Check if recheck was performed
    recheck_info = result.get("symptom_recheck")
    
    # Display recheck status if present
    if recheck_info and recheck_info.get("asked"):
        st.markdown("### 🔄 Symptom Recheck Update")
        st.markdown(f"""
        <div class="recheck-updated">
            <p><strong>Recheck Status:</strong> Completed</p>
            <p><strong>User Response:</strong> Condition has {"worsened" if recheck_info.get("user_response") == "yes" else "not worsened" if recheck_info.get("user_response") == "no" else "uncertain status"}</p>
            <p><strong>Severity:</strong> 
                <span class="severity-change">{recheck_info.get("severity_before", "").upper()}</span>
                →
                <span class="severity-change">{recheck_info.get("severity_after", "").upper()}</span>
            </p>
            <p><strong>Action Taken:</strong> {recheck_info.get("action_taken", "").title()}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        clear_button = st.button("Clear", use_container_width=True, key="clear_history_btn")
    
    if clear_button:
        if 'crisis_input' in st.session_state:
            del st.session_state.crisis_input
        st.rerun()

with col2:
    st.header("📊 Assessment Results")
    
    if submit_button:
        if not user_input or user_input.strip() == "":
            st.error("⚠️ Please describe the medical situation first.")
        else:
            with st.spinner("🔄 Analyzing crisis situation..."):
                try:
                    # Run the agent with session tracking
                    result = run_crisis_assessment(user_input, session_id=st.session_state.session_id)
                    
                    # Store in session state
                    st.session_state.last_result = result
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.last_result = None

# Display results
if hasattr(st.session_state, 'last_result') and st.session_state.last_result:
    result = st.session_state.last_result
    
    # Severity badge
    severity = result.get("severity_level", "moderate").upper()
    severity_class = f"severity-{result.get('severity_level', 'moderate').lower()}"
    
    st.markdown(f"""
    <div class="{severity_class}">
        SEVERITY: {severity}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Crisis Type
    st.subheader(f"🔍 Crisis Type: {result.get('crisis_type', 'Unknown')}")
    
    # Assessment
    st.markdown("### 📋 Assessment")
    st.info(result.get('assessment', 'No assessment available'))
    
    # Escalation Status
    escalation = result.get('escalation', {})
    if escalation.get('required', False):
        st.markdown("### 🚨 ESCALATION REQUIRED")
        st.error(f"**Reason:** {escalation.get('reason', 'Safety concern')}")
        st.warning(f"**Contact:** {', '.join(escalation.get('who_to_contact', []))}")
    else:
        st.markdown("### ✅ No Immediate Escalation Required")
        st.success("Situation can be managed with immediate actions below")
    
    # Immediate Actions
    st.markdown("### ✅ Immediate Actions")
    
    # Initialize step tracking in session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'step_history' not in st.session_state:
        st.session_state.step_history = []
    
    actions = result.get('immediate_actions', [])
    
    if actions:
        # Show all steps with enhanced UI
        for action in actions:
            step_id = action.get('step_id', 0)
            title = action.get('title', 'Action')
            instruction = action.get('instruction', '')
            duration = action.get('duration_seconds')
            critical = action.get('critical', False)
            repeatable = action.get('repeatable', False)
            user_confirm = action.get('user_confirmation_required', False)
            
            # Check if step is completed
            is_completed = step_id in st.session_state.completed_steps
            
            # Determine step container class
            container_class = "step-container"
            if critical:
                container_class = "step-container step-critical"
            
            # Build badges
            badges_html = ""
            if critical:
                badges_html += '<span class="critical-badge">⚠️ CRITICAL</span>'
            if repeatable:
                badges_html += '<span class="repeatable-badge">🔄 REPEATABLE</span>'
            if is_completed:
                badges_html += '<span class="repeatable-badge" style="background-color: #4CAF50;">✅ COMPLETED</span>'
            
            # Display step
            st.markdown(f"""
            <div class="{container_class}" style="{'opacity: 0.7;' if is_completed else ''}">
                <div class="step-header">
                    <span class="step-badge">Step {step_id}</span>
                    <strong style="font-size: 1.1em;">{title}</strong>
                    {badges_html}
                </div>
                <p style="margin: 10px 0; font-size: 1.05em;">{instruction}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add step completion button
            if not is_completed and user_confirm:
                if st.button(f"✓ Mark Step {step_id} as Completed", key=f"complete_{step_id}"):
                    if step_id not in st.session_state.completed_steps:
                        st.session_state.completed_steps.append(step_id)
                        # Update result with completed steps
                        result['completed_steps'] = st.session_state.completed_steps
                        st.session_state.last_result = result
                        st.rerun()
            
            # Show timing information
            if duration is not None:
                st.info(f"⏱️ Recommended duration: {duration} seconds")
            
            # Add spacing
            st.markdown("<br>", unsafe_allow_html=True)
    
    # Do Not Do
    st.markdown("### ⚠️ DO NOT DO")
    for action in result.get('do_not_do', []):
        st.markdown(f"""
        <div class="warning-box">
            ❌ {action}
        </div>
        """, unsafe_allow_html=True)
    
    # Reassurance Message
    st.markdown("### 💙 Reassurance")
    st.success(result.get('reassurance_message', 'Stay calm and follow the steps.'))
    
    # JSON Output Section
    st.markdown("---")
    st.markdown("### 📄 Complete JSON Response")
    
    # Format JSON
    json_str = json.dumps(result, indent=2)
    
    # Display in code block
    st.code(json_str, language="json")
    
    # Download button
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name="crisis_assessment.json",
        mime="application/json",
        key="download_initial_json"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Emergency Numbers:</strong></p>
    <p>🚨 Emergency: 911 (US) | 112 (EU) | 108/102 (India)</p>
    <p><small>This tool is for guidance only. Always prioritize professional medical care in emergencies.</small></p>
</div>
""", unsafe_allow_html=True)
