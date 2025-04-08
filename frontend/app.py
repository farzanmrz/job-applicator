import streamlit as st
from classes.CredentialManager import CredentialManager
from classes.JobSearchPreferences import JobSearchPreferences
from utils.frontendutil import (
    setupBasic_prefs,
    setupCreds_tab,
    setupExport_tab,
    setupPage,
    setupSave_button,
    setupSkills_tab,
    setupTabs,
)


def init_session_state():
    """Initialize session state variables."""
    if "editing_credential_set" not in st.session_state:
        st.session_state.editing_credential_set = None

    if "adding_credential_set" not in st.session_state:
        st.session_state.adding_credential_set = False


def main():
    """Main Streamlit application."""
    setupPage()

    # Initialize session state
    init_session_state()

    # Initialize managers
    cred_manager = CredentialManager()
    pref_manager = JobSearchPreferences()
    preferences = pref_manager.get_prefs()

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

    # Save button (always visible)
    setupSave_button(pref_manager, preferences)


if __name__ == "__main__":
    main()
