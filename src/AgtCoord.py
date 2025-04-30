import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import Any, Dict, List, Literal, Optional

from langgraph.graph import END, StateGraph

# Import Pregel for type hinting the compiled graph
from langgraph.pregel import Pregel

# Import the RUNNABLE function from SrchMgr
from graphs.SrchMgr import (
    init_srchmgr,  # Assuming this is the correct runner function name
)
from src.state import JobState

# --- Action Node Functions ---


def job_profile_entry(state: JobState) -> Dict[str, Any]:
    """Node for Job Profile Management logic."""
    return {
        "msgs": state.msgs + ["Visited Job Profile"],
        "current_action": "idle",
    }


def job_search_entry(state: JobState) -> Dict[str, Any]:
    """Node that triggers the Job Search Manager workflow."""
    # Initialize search results dictionary if not present
    if not state.srch_res:
        return {
            "msgs": state.msgs
            + ["AgtCoord: Error - no platforms configured for search."],
            "current_action": "idle",
        }
    # Call the workflow runner function and return its result directly
    srch_result: Dict[str, Any] = init_srchmgr(state)
    srch_result["current_action"] = "idle"
    return srch_result


def job_apply_entry(state: JobState) -> Dict[str, Any]:
    """Node for Job Apply logic."""
    return {
        "msgs": state.msgs + ["Visited Job Apply"],
        "current_action": "idle",
    }


# --- Routing Function ---
def route_action(
    state: JobState,
) -> Literal["ProfMgr", "SrchMgr", "ApplyMgr", "__end__"]:  # Use original names
    """Reads state and returns the name of the next node."""
    action = state.current_action
    if action == "job_prof":
        return "ProfMgr"  # Original name
    elif action == "job_srch":
        return "SrchMgr"  # Original name
    elif action == "job_apply":
        return "ApplyMgr"  # Original name
    elif action == "idle" or action is None:
        return "__end__"
    else:
        print(f"Warning: Unknown action '{action}' in route_action. Ending.")
        return "__end__"


# --- Graph Definition Function ---
def init_agtcoord() -> Pregel:  # Use Pregel for type hint
    """
    Defines and compiles the main AgtCoord graph.
    """
    workflow = StateGraph(JobState)

    # Add nodes using the original, simpler names
    workflow.add_node("ProfMgr", job_profile_entry)
    workflow.add_node("SrchMgr", job_search_entry)
    workflow.add_node("ApplyMgr", job_apply_entry)

    # Define the path map using the original names
    path_map = {
        "ProfMgr": "ProfMgr",
        "SrchMgr": "SrchMgr",
        "ApplyMgr": "ApplyMgr",
        "__end__": END,
    }

    # Set the conditional entry point, routing to one of the original node names
    workflow.set_conditional_entry_point(route_action, path_map)

    # Add conditional edges from each node back to the routing logic
    # The source names must match the names given in add_node
    workflow.add_conditional_edges("ProfMgr", route_action, path_map)
    workflow.add_conditional_edges("SrchMgr", route_action, path_map)
    workflow.add_conditional_edges("ApplyMgr", route_action, path_map)

    # Compile and return the graph
    return workflow.compile()


# --- Main execution block ---
if __name__ == "__main__":
    # Create and compile the graph by calling the init function
    app: Pregel = init_agtcoord()  # Use Pregel for type hint

    # Define the initial state
    initial_inputs = {
        "current_action": "job_srch",
        "msgs": ["AgtCoord: Coordinator started"],
        "srch_res": {"linkedin": None},  # Initialize with LinkedIn platform
    }

    # Invoke the compiled graph
    print("\n--- Running AgtCoord Graph ---")
    final_state = app.invoke(initial_inputs, {"recursion_limit": 10})

    # Print the final state messages for tracing
    print("\n--- Final State ---")
    import json

    print(json.dumps(final_state, indent=2))
    print("-" * 25)
    print("--- AgtCoord Graph Finished ---")
