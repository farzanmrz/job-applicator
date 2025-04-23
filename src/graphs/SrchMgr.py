import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import Any, Dict, Literal

from langgraph.graph import END, StateGraph

# Import Pregel for type hinting the compiled graph
from langgraph.pregel import Pregel

# Use relative import because SrchMgr is in a subpackage ('graphs') of 'src'
# and state.py is directly under 'src'
from src.state import JobState


# --- Node Function ---
def process_search_stub(state: JobState) -> Dict[str, Any]:
    """
    Minimal placeholder function for the search subgraph node.
    """
    # This message should originate from within the subgraph
    return {
        "msgs": state.msgs + ["SrchMgr subgraph executed (stub)"],
        "current_action": "idle",  # Assume subgraph sets action to idle when done
    }


# --- Create Subgraph Definition ---
def create_srch_mgr_graph() -> Pregel:  # Use Pregel for type hint
    """
    Defines and compiles the SrchMgr subgraph.
    """
    subgraph = StateGraph(JobState)
    # Add the single stub processing node
    subgraph.add_node(
        "process_srchmgr_stub", process_search_stub
    )  # Descriptive node name
    # Set it as the entry point
    subgraph.set_entry_point("process_srchmgr_stub")
    # End immediately after this node for simplicity
    subgraph.add_edge("process_srchmgr_stub", END)
    # Compile and return the subgraph
    return subgraph.compile()


# --- Pre-compile the graph for efficiency ---
compiled_srch_mgr_graph: Pregel = create_srch_mgr_graph()  # Use Pregel for type hint


# --- Callable Interface / Runner Function ---
# Renamed as requested
def init_srchmgr(state: JobState) -> Dict[str, Any]:
    """
    Runs the compiled search manager subgraph with the given state.
    This is the main entry point called from AgtCoord.
    """
    # Run the pre-compiled subgraph with the provided state dictionary
    result = compiled_srch_mgr_graph.invoke(state)
    return result
