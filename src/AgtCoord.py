# AgtCoord.py (Base Coordinator Agent)
from typing import Any, Dict, List, Literal, Optional

from langgraph.graph import END, StateGraph

from src.graphs.SrchMgr import SrchMgr  # Import the SrchMgr subgraph
from src.state import JobState

# --- Action Nodes (Using attribute access) ---


def job_profile_entry(state: JobState) -> Dict[str, Any]:
    """Placeholder for Job Profile Management logic."""
    print("--- Entered Job Profile Node (Stub) ---")
    # Use attribute access: state.msgs
    messages = state.msgs + ["Visited Job Profile"]
    return {
        "msgs": messages,
        "current_action": "idle",
    }


def job_search_entry(state: JobState) -> Dict[str, Any]:
    """Placeholder for Job Search logic."""
    print("--- Entered Job Search Node (Stub) ---")
    # Use attribute access: state.msgs
    messages = state.msgs

    # Check if plats_srch is empty
    if not state.plats_srch:
        # Error: no platforms approved
        messages = messages + ["Error: no platforms approved for search."]
        return {
            "msgs": messages,
            "current_action": "idle",
        }

    # Normal course: platforms available for search
    messages = messages + ["Visited Job Search"]

    # Call the SrchMgr subgraph
    srch_mgr = SrchMgr()
    srch_result = srch_mgr(state)

    # Return the result
    return srch_result


def job_apply_entry(state: JobState) -> Dict[str, Any]:
    """Placeholder for Job Apply logic."""
    print("--- Entered Job Apply Node (Stub) ---")
    # Use attribute access: state.msgs
    messages = state.msgs + ["Visited Job Apply"]
    return {
        "msgs": messages,
        "current_action": "idle",
    }


# --- Routing Function (Using attribute access) ---


def route_action(
    state: JobState,
) -> Literal["ProfMgr", "SrchMgr", "ApplyMgr", "__end__"]:
    """
    Reads state.current_action and returns the *name* of the next node
    or '__end__'. Use attribute access for Pydantic models.
    """
    # Use attribute access: state.current_action
    action = state.current_action

    if action == "job_prof":
        return "ProfMgr"
    elif action == "job_srch":
        return "SrchMgr"
    elif action == "job_apply":
        return "ApplyMgr"
    elif action == "idle" or action is None:
        return "__end__"
    else:
        print(f"Warning: Unknown action '{action}' in route_action. Ending.")
        return "__end__"


# --- Graph Definition (Using Conditional Entry/Edges) ---
# Define the workflow using the JobState Pydantic model
workflow = StateGraph(JobState)

# Add only the action nodes
workflow.add_node("ProfMgr", job_profile_entry)
workflow.add_node("SrchMgr", job_search_entry)
workflow.add_node("ApplyMgr", job_apply_entry)

# Define the path map for routing decisions
path_map = {
    "ProfMgr": "ProfMgr",
    "SrchMgr": "SrchMgr",
    "ApplyMgr": "ApplyMgr",
    "__end__": END,
}

# Set the CONDITIONAL entry point
workflow.set_conditional_entry_point(route_action, path_map)

# Add CONDITIONAL edges from each action node back to the routing logic
workflow.add_conditional_edges("ProfMgr", route_action, path_map)
workflow.add_conditional_edges("SrchMgr", route_action, path_map)
workflow.add_conditional_edges("ApplyMgr", route_action, path_map)


# Compile the graph
app = workflow.compile()


# --- Main execution block ---
if __name__ == "__main__":
    print("--- Running Graph ---")

    # 1. Define the initial state as a dictionary, triggering 'job_srch'
    # LangGraph automatically converts this dict to a JobState instance internally
    initial_inputs = {
        "current_action": "job_srch",
        "msgs": [],
        "plats_srch": ["linkedin"],
    }

    print(f"Initial State (dict): {initial_inputs}")
    print("-" * 25)

    # 2. Execute the graph using app.stream()
    step = 0
    # The state object within the stream will be the JobState instance
    for state_snapshot in app.stream(initial_inputs, {"recursion_limit": 10}):
        step += 1
        print(f"\n--- Output after Step {step} ---")
        # state_snapshot often contains the output of the last node run
        print(f"{state_snapshot}")
        print("-" * 25)

    print("--- Graph Finished ---")
