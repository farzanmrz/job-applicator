#!/usr/bin/env python3
"""
General section functionality for the Job Applicator frontend.

This module contains functions for displaying and handling the General section
of the application, which includes user preferences, credentials, and profile settings.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
from utils.credmanager import CredentialManager

# Constants
USR_PREFS_FILEPATH = os.path.join(
    Path(__file__).parent.parent.parent, "data", "usr_prefs.json"
)


def load_usr_prefs() -> Dict[str, Any]:
    """
    Load user preferences from JSON file for the job form.

    Returns:
        Dict[str, Any]: Dictionary of preference values with keys matching form fields
    """
    # Create an empty default dictionary
    job_prefs = {}

    # Load from file if it exists
    if os.path.exists(USR_PREFS_FILEPATH):
        with open(USR_PREFS_FILEPATH, "r") as f:
            prefs = json.load(f)
            form_prefs = prefs.get("1_prefs", {})

            # Map to form field names
            job_prefs = {
                "modality": form_prefs.get("1a_modality"),
                "employment_type": form_prefs.get("1b_emptype"),
                "locations": form_prefs.get("1c_locs"),
                "job_titles": form_prefs.get("1d_jobtitles"),
                "experience_level": form_prefs.get("1e_explevel"),
                "salary_range": form_prefs.get("1f_salary"),
            }

    return job_prefs


def save_usr_prefs() -> bool:
    """
    Save user preferences to JSON file.

    Collects values from form fields and saves them to the preferences file.

    Returns:
        bool: True if saving was successful, False otherwise
    """
    try:
        # Collect all preference values from session state
        job_titles_list = (
            st.session_state.job_title.strip().split("\n")
            if st.session_state.job_title
            else []
        )

        preferences = {
            "1_prefs": {
                "1a_modality": st.session_state.modality,
                "1b_emptype": st.session_state.employment_type,
                "1c_locs": st.session_state.locations,
                "1d_jobtitles": job_titles_list,
                "1e_explevel": st.session_state.experience_level,
                "1f_salary": list(st.session_state.salary_range),
            },
            "2_keywords": {
                # Will be populated with keywords data later
            },
        }

        # Ensure the directory exists
        os.makedirs(os.path.dirname(USR_PREFS_FILEPATH), exist_ok=True)

        # Write to file
        with open(USR_PREFS_FILEPATH, "w") as f:
            json.dump(preferences, f, indent=2)

        return True
    except Exception as e:
        st.error(f"Error saving preferences: {e}")
        return False


def tab_prefs():
    """
    Set up the Preferences tab content with job preference form elements.

    Creates form fields for modality, employment type, locations,
    job titles, experience level, and salary range.
    Loads previously saved preferences when available.
    """
    st.subheader("Preferences")

    # Get saved preferences
    prefs = load_usr_prefs()

    # Define options for each field
    OPT_MODALITY = ["On-site", "Remote", "Hybrid"]
    OPT_EMPLOYMENT = ["Full-time", "Part-time", "Contract", "Internship", "Temporary"]
    OPT_LOCATIONS = [
        "USA",
        "Canada",
        "UK",
        "Australia",
        "Germany",
        "France",
        "India",
        "Singapore",
        "Japan",
        "Netherlands",
    ]
    OPT_EXPERIENCE = ["Entry-Level", "Associate", "Mid-Level", "Senior", "Executive"]

    # First row: Modality, Employment Type, Locations
    pref_col1, pref_col2, pref_col3 = st.columns(3)

    with pref_col1:
        modality = st.multiselect(
            "Modality",
            OPT_MODALITY,
            default=prefs.get("modality") or [],
            key="modality",
        )

    with pref_col2:
        employment_type = st.multiselect(
            "Employment Type",
            OPT_EMPLOYMENT,
            default=prefs.get("employment_type") or [],
            key="employment_type",
        )

    with pref_col3:
        locations = st.multiselect(
            "Locations",
            OPT_LOCATIONS,
            default=prefs.get("locations") or [],
            key="locations",
        )

    # Second row: Job Titles, Experience, Salary
    job_col1, job_col2, job_col3 = st.columns(3)

    # Convert job titles from list to text if needed
    job_titles = prefs.get("job_titles")
    if isinstance(job_titles, list) and job_titles:
        job_titles_text = "\n".join(job_titles)
    else:
        job_titles_text = ""

    with job_col1:
        job_title = st.text_area("Job Titles", value=job_titles_text, key="job_title")

    # Find index of saved experience level if present
    saved_exp = prefs.get("experience_level")
    exp_index = None
    if saved_exp and saved_exp in OPT_EXPERIENCE:
        exp_index = OPT_EXPERIENCE.index(saved_exp)

    with job_col2:
        experience_level = st.selectbox(
            "Experience",
            options=OPT_EXPERIENCE,
            index=exp_index if exp_index is not None else 0,
            key="experience_level",
        )

    # Handle saved salary range
    saved_salary = prefs.get("salary_range")
    default_salary = (80000, 120000)  # Default fallback
    if isinstance(saved_salary, list) and len(saved_salary) == 2:
        salary_value = tuple(saved_salary)
    else:
        salary_value = default_salary

    with job_col3:
        salary_range = st.slider(
            "Annual Salary (USD)",
            min_value=20000,
            max_value=400000,
            value=salary_value,
            step=5000,
            format="$%d",
            key="salary_range",
        )


def tab_keys():
    """Set up the Keywords tab content."""
    st.subheader("Keywords & Skills")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Technical Skills")
        tech_skills = st.multiselect(
            "Select your technical skills",
            [
                "Python",
                "JavaScript",
                "Java",
                "C++",
                "C#",
                "Ruby",
                "Go",
                "Swift",
                "React",
                "Angular",
                "Vue.js",
                "Node.js",
                "Django",
                "Flask",
                "SQL",
                "MongoDB",
                "PostgreSQL",
                "MySQL",
                "Redis",
                "Docker",
                "Kubernetes",
                "AWS",
                "Azure",
                "GCP",
                "Machine Learning",
                "Data Science",
                "TensorFlow",
                "PyTorch",
            ],
            key="tech_skills",
        )
        custom_tech_skills = st.text_area(
            "Add custom technical skills (one per line)", key="custom_tech_skills"
        )

    with col2:
        st.subheader("Soft Skills")
        soft_skills = st.multiselect(
            "Select your soft skills",
            [
                "Communication",
                "Teamwork",
                "Problem Solving",
                "Critical Thinking",
                "Time Management",
                "Leadership",
                "Creativity",
                "Adaptability",
                "Project Management",
                "Attention to Detail",
                "Analytical Skills",
            ],
            key="soft_skills",
        )
        custom_soft_skills = st.text_area(
            "Add custom soft skills (one per line)", key="custom_soft_skills"
        )

    st.subheader("Skill Proficiency")
    st.markdown("Drag to set proficiency levels for your top skills")

    # Example of skill sliders
    col1, col2, col3 = st.columns(3)

    with col1:
        st.slider(
            "Python Proficiency",
            1,
            5,
            3,
            help="1 = Beginner, 5 = Expert",
            key="python_prof",
        )

    with col2:
        st.slider(
            "JavaScript Proficiency",
            1,
            5,
            3,
            help="1 = Beginner, 5 = Expert",
            key="js_prof",
        )

    with col3:
        st.slider(
            "React Proficiency",
            1,
            5,
            3,
            help="1 = Beginner, 5 = Expert",
            key="react_prof",
        )


def tab_creds():
    """Set up the Credentials tab content."""
    st.subheader("Credentials")
    
    # Initialize the credential manager
    cred_manager = CredentialManager()
    
    # Get credential sets with their platforms
    credential_sets = cred_manager.get_credential_sets_with_platforms()
    
    # Toggle to show/hide passwords
    if st.button("Toggle Password Visibility", key="show_passwords_btn"):
        if "show_passwords" not in st.session_state:
            st.session_state.show_passwords = True
        else:
            st.session_state.show_passwords = not st.session_state.show_passwords

    # Display current status
    password_status = (
        "showing" if st.session_state.get("show_passwords", False) else "hidden"
    )
    st.info(f"Passwords are currently {password_status}")
    
    # Display saved credentials
    if credential_sets:
        for cred_set in credential_sets:
            # Format the platforms for display
            platforms_str = ", ".join([p.capitalize() for p in cred_set["platforms"]])
            
            # Create a card for each credential set using a container
            with st.container():
                st.markdown(f"### Credentials for {platforms_str}")
                st.write(f"**Username:** {cred_set['username']}")
                
                # Show password as dots or plain text based on toggle
                password_display = cred_set["password"] if st.session_state.get("show_passwords", False) else "•" * 8
                st.write(f"**Password:** {password_display}")
                
                # Platform removal
                st.write("**Platforms:**")
                for platform in cred_set["platforms"]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"- {platform.capitalize()}")
                    with col2:
                        if st.button("Remove", key=f"remove_{cred_set['id']}_{platform}"):
                            if cred_manager.delete_credentials(platform):
                                st.success(f"Removed {platform} from credential set")
                                # Use Streamlit rerun instead of experimental_rerun
                                st.rerun()
                
                # Add a separator
                st.markdown("---")
    else:
        st.info("No credentials stored yet. Add your first credential below.")
    
    # Add credential form
    st.subheader("Add New Credentials")
    
    # Check if there are any available platforms
    available_platforms = cred_manager.get_available_platforms()
    available_platforms_cap = [p.capitalize() for p in available_platforms]
    
    if not available_platforms:
        st.warning("All platforms already have credentials assigned. Remove an existing platform mapping to add new credentials.")
    else:
        with st.form(key="credential_form"):
            # Get available platforms
            platforms = st.multiselect(
                "Platforms",
                options=available_platforms_cap,
                help="Select one or more platforms to use these credentials"
            )
            
            username = st.text_input("Username/Email")
            password = st.text_input("Password", type="password")
            
            submit_button = st.form_submit_button("Save Credentials")
            
            if submit_button and platforms and username and password:
                # Convert platform names to lowercase for storage
                platforms_lower = [p.lower() for p in platforms]
                if cred_manager.store_credentials(platforms_lower, username, password):
                    platform_list = ", ".join(platforms)
                    st.success(f"Credentials saved for {platform_list}")
                    # Use Streamlit rerun instead of experimental_rerun
                    st.rerun()


def set_tabgroup():
    """
    Create the tab group for the General section.

    Creates tabs for Preferences, Keywords, and Credentials,
    and calls the appropriate function to set up each tab's content.
    """
    # Create the tab group
    preferences_tab, keywords_tab, credentials_tab = st.tabs(
        ["Preferences", "Keywords", "Credentials"]
    )

    # Set up content for each tab
    with preferences_tab:
        tab_prefs()

    with keywords_tab:
        tab_keys()

    with credentials_tab:
        tab_creds()


def set_bottom() -> None:
    """
    Set up the bottom section of the General tab with save button.

    Adds a horizontal separator line and a "Save All Preferences" button
    that persists across all tabs.

    Returns:
        None: Displays content directly in the Streamlit app
    """
    # Add horizontal line above the save button
    st.markdown("<hr>", unsafe_allow_html=True)

    # Save button
    if st.button("Save All Preferences", key="save_all"):
        # Call save_usr_prefs to collect and save preferences
        if save_usr_prefs():
            st.success("All preferences saved successfully!")
        else:
            st.error("Failed to save preferences.")


def set_secgeneral() -> None:
    """
    Set up the General section of the frontend.

    This will be called when the "General" option is selected in the sidebar.
    Adds a section header, tabbed interface, and bottom section with save button.

    Returns:
        None: Displays content directly in the Streamlit app
    """
    # Add section header
    st.subheader("General Section")

    # Create the tab group
    set_tabgroup()

    # Add bottom section with save button
    set_bottom()
