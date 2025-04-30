import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import Any, Dict

from langgraph.graph import END, StateGraph

# Import Pregel for type hinting the compiled graph
from langgraph.pregel import Pregel

# Use relative import because SrchMgr is in a subpackage ('graphs') of 'src'
# and state.py is directly under 'src'
from src.state import JobState

# Placeholder import for the tool (will be in tools/lkdn_tools.py)
try:
    from tools.lkdn_tools import lkdn_auth
except ImportError:
    print("Warning: tools.lkdn_tools import failed. Define lkdn_auth tool later.")
    lkdn_auth = lambda: {
        "success": False,
        "message": "Tool 'lkdn_auth' not implemented yet",
    }


# --- Node Functions ---
def run_search(state: JobState) -> Dict[str, Any]:
    """
    Main entry point for search management. Checks for supported platforms
    in the search results and processes them accordingly.
    """
    if "linkedin" in state.srch_res:
        return {"msgs": state.msgs + ["SrchMgr: LinkedIn processing placeholder"]}
    return {"msgs": state.msgs + ["SrchMgr: No supported platforms found"]}


def init_srchwrkrlkdn(state: JobState) -> Dict[str, Any]:
    """Node to handle LinkedIn process, starting with authentication call."""
    lkdn_auth()  # Call the tool, ignore its return value for now
    return {"msgs": ["SrchWrkrLkdn: Called lkdn_auth. Success"], "state": "idle"}


# --- Create Workflow Definition ---
def create_srchmgr() -> Pregel:  # Use Pregel for type hint
    """
    Defines and compiles the SrchMgr workflow.
    This workflow functions as a subgraph within the main agent coordinator.
    """
    workflow = StateGraph(JobState)

    # Add nodes
    workflow.add_node("run_search", run_search)
    workflow.add_node("SrchWrkrLkdn", init_srchwrkrlkdn)

    # Set up the workflow sequence
    workflow.set_entry_point("run_search")
    # Conditional edge from run_search
    workflow.add_conditional_edges(
        "run_search",
        lambda state: (
            "SrchWrkrLkdn" if "linkedin" in state.get("srch_res", {}) else END
        ),
        {"SrchWrkrLkdn": "SrchWrkrLkdn", END: END},
    )
    # Edge from the new node to END (for now)
    workflow.add_edge("SrchWrkrLkdn", END)

    # Compile and return the workflow
    return workflow.compile()


# --- Pre-compile the workflow for efficiency ---
compiled_srch_mgr_workflow: Pregel = create_srchmgr()  # Use Pregel for type hint


# --- Callable Interface / Runner Function ---
def init_srchmgr(state: JobState) -> Dict[str, Any]:
    """
    Legacy entry point. Use run_search() instead.
    """
    return run_search(state)
