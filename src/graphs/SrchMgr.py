# SrchMgr.py - Search Manager Subgraph (Stub)
from typing import Any, Dict, Literal

from langgraph.graph import END, StateGraph

from src.state import JobState


# --- Simple Node Function ---
def process_search(state: JobState) -> Dict[str, Any]:
    """
    Placeholder function for search processing.
    """
    # Simply append a message indicating the subgraph was called
    msgs = state.msgs + ["SrchMgr subgraph executed"]

    # Return state updates
    return {
        "msgs": msgs,
        "current_action": "idle",  # Set to idle when done
    }


# --- Create Subgraph ---
def create_srch_mgr_graph():
    """
    Create and return the SrchMgr subgraph.
    This is a stub implementation that will be expanded later.
    """
    # Define the subgraph using the same JobState as main graph
    subgraph = StateGraph(JobState)

    # Add a single processing node for now
    subgraph.add_node("process", process_search)

    # Set it as the entry point
    subgraph.set_entry_point("process")

    # No conditional logic yet - just end after the process node
    subgraph.add_edge("process", END)

    # Compile the subgraph
    return subgraph.compile()


# --- Callable Interface ---
def run_srch_mgr(state: JobState) -> Dict[str, Any]:
    """
    Run the search manager subgraph with the given state.
    This is the main entry point that will be called from AgtCoord.
    """
    # Create the subgraph
    subgraph = create_srch_mgr_graph()

    # Run the subgraph with the provided state
    result = subgraph.invoke(state)

    # Return the result
    return result
