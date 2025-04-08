import streamlit as st
import os
import time
from classes.CredentialManager import CredentialManager
from classes.JobSearchPreferences import JobSearchPreferences
from utils.frontendutil import (
    setupBasic_prefs,
    setupCreds_tab,
    setupExport_tab,
    setupPage,
    setupSkills_tab,
    setupTabs,
)
from utils.style_utils import load_css, get_css_path


def init_session_state():
    """Initialize session state variables."""
    if "editing_credential_set" not in st.session_state:
        st.session_state.editing_credential_set = None

    if "adding_credential_set" not in st.session_state:
        st.session_state.adding_credential_set = False
        
    if "delete_credential_set" not in st.session_state:
        st.session_state.delete_credential_set = None


def main():
    """Main Streamlit application."""
    setupPage()

    # Load CSS files
    load_css([
        get_css_path('styles.css'),
        get_css_path('credentials.css')
    ])
    
    
    

    # Initialize session state
    init_session_state()

    # Initialize managers
    cred_manager = CredentialManager()
    pref_manager = JobSearchPreferences()
    preferences = pref_manager.get_prefs()
    
    # Add an empty sidebar (collapsed by default)
    with st.sidebar:
        pass

    # Create tabs for different sections
    tabs = setupTabs()

    # Basic Preferences Tab
    with tabs[0]:
        setupBasic_prefs(preferences)

    # Skills & Keywords Tab
    with tabs[1]:
        setupSkills_tab(preferences)

    # Credentials Tab
    with tabs[2]:
        setupCreds_tab(cred_manager)

    # Export Tab
    with tabs[3]:
        setupExport_tab(preferences)

    # Save button (at the bottom of the page, not in sidebar) with horizontal line
    
    # Add horizontal line above the save button
    st.markdown("<hr style='margin-top: 30px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # Save button
    st.button("Save All Preferences", key="save_all", on_click=lambda: pref_manager.save_prefs(preferences))


if __name__ == "__main__":
    main()
