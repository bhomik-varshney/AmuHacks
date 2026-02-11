"""
LangGraph Agent Workflow
Multi-node agent flow for medical crisis decision assistant
"""

from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from nodes.normalize_input import normalize_input
from nodes.classify import classify_crisis
from nodes.assess_risk import assess_risk
from nodes.plan_actions import plan_actions
from nodes.format_output import format_output, should_continue
from config import langfuse_client, langfuse_handler
from langfuse.decorators import observe, langfuse_context
import time
import uuid


class GraphState(TypedDict):
    """State object for the crisis assessment graph"""
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
    # Memory fields
    completed_steps: List[str]
    previous_severity: Optional[str]
    escalation_history: List[dict]


def validate_state(state: dict) -> dict:
    """Validate state integrity and enforce memory rules"""
    # Ensure required memory fields exist
    if 'completed_steps' not in state:
        state['completed_steps'] = []
    if 'escalation_history' not in state:
        state['escalation_history'] = []
    if 'previous_severity' not in state:
        state['previous_severity'] = None
    
    # Validate completed steps reference existing actions
    # Note: During recheck, new actions may have different step_ids
    # Only validate if this is an initial assessment (not a recheck with existing completed steps)
    if state.get('immediate_actions') and not state.get('completed_steps'):
        valid_step_ids = [action.get('step_id') for action in state['immediate_actions'] if isinstance(action, dict)]
        state['completed_steps'] = [s for s in state.get('completed_steps', []) if s in valid_step_ids]
    # If completed_steps already exist (from recheck), preserve them as they're from previous valid actions
    
    # Enforce: escalation cannot be downgraded once set
    if state.get('escalation_history'):
        if any(h.get('required') for h in state['escalation_history']):
            state['escalation_required'] = True
    
    # Enforce: severity cannot decrease
    severity_order = {'low': 0, 'moderate': 1, 'high': 2, 'critical': 3}
    if state.get('previous_severity') and state.get('severity_level'):
        prev_level = severity_order.get(state['previous_severity'], 0)
        curr_level = severity_order.get(state['severity_level'], 0)
        if curr_level < prev_level:
            state['severity_level'] = state['previous_severity']
    
    return state


def create_crisis_agent():
    """
    Create and compile the LangGraph workflow with checkpointing
    
    Graph Flow:
    1. Input Normalization -> cleans user input
    2. Crisis Classification -> identifies crisis type and severity
    3. Risk Assessment -> determines escalation needs
    4. Action Planning -> generates immediate actions
    5. Format Output -> assembles JSON response
    
    Memory: Uses LangGraph checkpointing for deterministic state management
    """
    from langgraph.checkpoint.memory import MemorySaver
    
    # Initialize the graph with state validation
    workflow = StateGraph(GraphState)
    
    # Add validation wrapper for all nodes
    def validated_node(node_func):
        def wrapper(state):
            state = validate_state(state)
            result = node_func(state)
            return validate_state(result)
        return wrapper
    
    # Add nodes with validation
    workflow.add_node("normalize_input", validated_node(normalize_input))
    workflow.add_node("classify_crisis", validated_node(classify_crisis))
    workflow.add_node("assess_risk", validated_node(assess_risk))
    workflow.add_node("plan_actions", validated_node(plan_actions))
    workflow.add_node("format_output", validated_node(format_output))
    
    # Define the flow
    workflow.set_entry_point("normalize_input")
    
    # Add conditional edges to handle errors
    workflow.add_conditional_edges(
        "normalize_input",
        lambda state: "end" if state.get("error") else "continue",
        {
            "continue": "classify_crisis",
            "end": "format_output"
        }
    )
    
    workflow.add_edge("classify_crisis", "assess_risk")
    workflow.add_edge("assess_risk", "plan_actions")
    workflow.add_edge("plan_actions", "format_output")
    workflow.add_edge("format_output", END)
    
    # Compile with in-memory checkpointing
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


def run_crisis_assessment(user_input: str, session_id: str = None) -> dict:
    """
    Run the complete crisis assessment workflow with memory and observability
    
    Args:
        user_input: User's description of the medical situation
        session_id: Optional session ID for tracking
        
    Returns:
        dict: Complete crisis assessment in JSON format
    """
    start_time = time.time()
    session_id = session_id or str(uuid.uuid4())
    
    # Configure Langfuse handler with session info
    if langfuse_handler:
        langfuse_handler.session_id = session_id
        langfuse_handler.trace_name = "crisis_assessment"
        langfuse_handler.tags = ["crisis", "medical", "assessment"]
        langfuse_handler.metadata = {
            "type": "medical_crisis",
            "version": "1.0",
            "user_input": user_input
        }
    
    try:
        # Create the agent
        app = create_crisis_agent()
        
        # Initialize state with memory fields
        initial_state = {
            "user_input": user_input,
            "normalized_input": "",
            "crisis_type": "",
            "severity_level": "",
            "assessment": "",
            "immediate_actions": [],
            "do_not_do": [],
            "escalation_required": False,
            "who_to_contact": [],
            "escalation_reason": "",
            "reassurance_message": "",
            "error": "",
            "final_output": {},
            # Memory fields
            "completed_steps": [],
            "previous_severity": None,
            "escalation_history": []
        }
        
        # Run the workflow with checkpointing
        # Use thread_id for session-based memory
        config = {
            "configurable": {"thread_id": session_id},
            "callbacks": [langfuse_handler] if langfuse_handler else []
        }
        
        result = app.invoke(initial_state, config=config)
        
        # Update handler metadata with final results
        if langfuse_handler:
            execution_time = time.time() - start_time
            langfuse_handler.metadata.update({
                "execution_time_seconds": execution_time,
                "severity_level": result.get("severity_level", "unknown"),
                "crisis_type": result.get("crisis_type", "unknown"),
                "escalation_required": result.get("escalation_required", False)
            })
        
        # Flush traces to ensure they're sent immediately
        if langfuse_client:
            langfuse_client.flush()
            print("✅ Trace flushed to Langfuse")
        
        return result["final_output"]
    
    except Exception as e:
        # Flush any pending traces even on error
        if langfuse_client:
            langfuse_client.flush()
        raise





def get_graph_visualization() -> str:
    """
    Get a text representation of the graph structure
    """
    return """
    Crisis Assessment Agent Graph:
    
    START
      ↓
    ┌─────────────────────┐
    │ Input Normalization │ → Cleans and validates input
    └─────────────────────┘
      ↓ (if valid medical input)
    ┌─────────────────────┐
    │ Crisis Classification│ → Identifies crisis type and severity
    └─────────────────────┘
      ↓
    ┌─────────────────────┐
    │  Risk Assessment    │ → Checks red flags, determines escalation
    └─────────────────────┘
      ↓
    ┌─────────────────────┐
    │  Action Planning    │ → Generates immediate actions
    └─────────────────────┘
      ↓
    ┌─────────────────────┐
    │  Format Output      │ → Assembles JSON response
    └─────────────────────┘
      ↓
    END
    """


if __name__ == "__main__":
    # Test the agent
    test_input = "My father is having chest pain and sweating a lot"
    print("Testing Crisis Assessment Agent...")
    print(f"Input: {test_input}\n")
    
    result = run_crisis_assessment(test_input)
    
    import json
    print("Output:")
    print(json.dumps(result, indent=2))
