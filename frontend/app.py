#!/usr/bin/env python3
"""
Streamlit Frontend for Job Applicator (v2)

A clean, modular implementation of the Job Applicator frontend.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import section components
from utils.frontend.secgeneral import set_secgeneral
from utils.frontend.secroutine import set_secroutine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [ %(name)s ] %(message)s',
    datefmt='%m/%d %H:%M'
)
logger = logging.getLogger("FrontEnd")


def setup_sidebar() -> None:
    """
    Configure the sidebar navigation and load the appropriate section content.
    
    Sets up the sidebar with navigation options and loads the corresponding
    section content based on the selection.
    
    Returns:
        None: Updates the UI directly
    """
    with st.sidebar:
        st.title("Navigation")
        selected = st.radio("Select Section", ["General", "Routines"])
    
    # Store the selection in session state
    st.session_state.sidebar_selection = selected
    
    # Load the appropriate section based on selection
    if selected == "General":
        set_secgeneral()
    elif selected == "Routines":
        set_secroutine()


def main():
    """Main function that sets up the Streamlit application."""
    # Configure basic page settings
    st.set_page_config(
        page_title="Job Applicator",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Main content area title
    st.title("Job Applicator")
    
    # Initialize session state variables
    # Interface state variables
    if "sidebar_selection" not in st.session_state:
        st.session_state.sidebar_selection = "General"
        
    # Agent communication
    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = []
    
    # Setup the sidebar navigation and load content
    setup_sidebar()


if __name__ == "__main__":
    main()