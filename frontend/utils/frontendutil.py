import json
import os
import time

import streamlit as st
from utils.style_utils import (
    get_css_path,
    get_html_path,
    load_css,
    load_html_template,
    render_template,
)


def decrypt_all_credentials(credManager):
    """Get all decrypted credentials including their platforms."""
    credential_sets = credManager.get_all_credential_sets()

    result = []
    for set_id, creds in credential_sets.items():
        result.append(
            {
                "set_id": set_id,
                "name": creds["name"],
                "username": creds["username"],
                "password": creds["password"],
                "saved_at": creds.get("saved_at", 0),
                "platforms": creds.get("platforms", []),
            }
        )

    return result


# This function is now deprecated in favor of setupCreds_tab
def addAuth_sidebar(auth):
    """DEPRECATED: Add LinkedIn authentication UI to the sidebar."""
    pass


def setupPage():
    """Configure page settings."""
    st.set_page_config(
        page_title="Job Search Preferences", page_icon="🔍", layout="wide"
    )

    st.title("Welcome to Job Applicator")


def setupTabs():
    """Create tabs for different sections."""
    return st.tabs(["Preferences", "Keywords", "Credentials", "Export"])


def setupBasic_prefs(preferences):
    """Setup basic preferences tab content."""
    
    # First row - 4 fields (Education, Industries, Modality, Job Type)
    col1, col2, col3, col4 = st.columns(4)
    
    # Education Level (single-select dropdown)
    with col1:
        education_options = ["None", "High School", "Bachelor's", "Master's", "PhD"]
        preferences["education"] = st.selectbox(
            "Education",
            options=education_options,
            index=(
                education_options.index(preferences["education"])
                if preferences["education"] in education_options
                else 0
            )
        )

    # Industries (multi-select dropdown)
    with col2:
        industry_options = [
            "Technology",
            "Healthcare",
            "Finance",
            "Education",
            "Manufacturing",
            "Retail",
            "Media",
            "Government",
            "Non-profit",
            "Other",
        ]
        preferences["industries"] = st.multiselect(
            "Industries",
            options=industry_options,
            default=[ind for ind in preferences.get("industries", []) if ind in industry_options]
        )
    
    # Modality (new field - multi-select dropdown)
    with col3:
        modality_options = [
            "On-site", 
            "Remote", 
            "Hybrid"
        ]
        # Make sure we only use valid options as defaults
        valid_modalities = [mod for mod in preferences.get("modality", []) if mod in modality_options]
        preferences["modality"] = st.multiselect(
            "Modality",
            options=modality_options,
            default=valid_modalities
        )

    # Job Type (multi-select dropdown)
    with col4:
        job_type_options = [
            "Full-time",
            "Part-time",
            "Contract",
            "Internship",
            "Temporary"
        ]
        # Make sure we only use valid options as defaults and remove "Remote" if present
        if "job_type" in preferences:
            # Filter out "Remote" and any other invalid options
            valid_job_types = [jt for jt in preferences["job_type"] if jt in job_type_options]
        else:
            valid_job_types = []
            
        preferences["job_type"] = st.multiselect(
            "Job Type",
            options=job_type_options,
            default=valid_job_types
        )

    # Second row - 3 fields (Locations, Job Experience, Availability)
    col1, col2, col3 = st.columns(3)
    
    # Locations (renamed from Countries - multi-select dropdown)
    with col1:
        location_options = [
            "United States",
            "Canada",
            "United Kingdom",
            "Germany",
            "France",
            "Australia",
            "India",
            "Singapore",
            "Japan",
            "Remote/Any",
        ]
        # Use locations if available, otherwise fall back to countries for compatibility
        location_defaults = preferences.get("locations", preferences.get("countries", []))
        valid_locations = [loc for loc in location_defaults if loc in location_options]
        preferences["locations"] = st.multiselect(
            "Locations",
            options=location_options,
            default=valid_locations
        )

    # Job Experience (multi-select dropdown)
    with col2:
        job_exp_options = [
            "Entry-Level",
            "1-2 years",
            "2-4 years",
            "4+ years",
            "Senior/Executive",
        ]
        valid_job_exp = [exp for exp in preferences.get("job_experience", []) if exp in job_exp_options]
        preferences["job_experience"] = st.multiselect(
            "Job Experience",
            options=job_exp_options,
            default=valid_job_exp
        )
    
    # Availability (new field - single-select dropdown with only two options)
    with col3:
        availability_options = ["Immediately", "Flexible"]
        default_availability = preferences.get("availability", "Flexible")
        # Make sure default is in options
        if default_availability not in availability_options:
            default_availability = "Flexible"
        
        preferences["availability"] = st.selectbox(
            "Availability",
            options=availability_options,
            index=availability_options.index(default_availability)
        )
    
    # Third row - Job Titles as a simple multiselect dropdown
    job_title_options = [
        "Software Engineer",
        "Data Scientist",
        "Product Manager",
        "UX Designer",
        "DevOps Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Machine Learning Engineer",
        "AI Research Scientist",
        "Project Manager"
    ]
    
    # Make sure job_titles exists
    if "job_titles" not in preferences:
        preferences["job_titles"] = []
    
    # Use a multiselect for job titles
    preferences["job_titles"] = st.multiselect(
        "Job Titles",
        options=job_title_options,
        default=[title for title in preferences["job_titles"] if title in job_title_options]
    )


def handleSkillList(preferences, skillType, title):
    """Handle display and adding of skills list."""
    st.subheader(title)

    # Display existing skills
    if preferences[skillType]:
        for i, skill in enumerate(preferences[skillType]):
            col1, col2 = st.columns([4, 1])
            col1.write(f"• {skill}")
            if col2.button("Remove", key=f"remove_{skillType}_{i}"):
                preferences[skillType].remove(skill)
                st.rerun()

    # Add new skill
    new_skill = st.text_input(f"Add a {title.lower()[:-1]}:")
    if (
        st.button(f"Add {title[:-1]}", key=f"add_{skillType}")
        and new_skill
        and new_skill not in preferences[skillType]
    ):
        preferences[skillType].append(new_skill)
        st.success(f"Added: {new_skill}")
        st.rerun()


def setupSkills_tab(preferences):
    """Setup skills and keywords tab content."""
    st.header("Skills & Keywords")

    # Technical Skills
    handleSkillList(preferences, "technical_skills", "Technical Skills")

    # Soft Skills
    handleSkillList(preferences, "soft_skills", "Soft Skills")
    
    # Note: Job Titles moved to Basic Preferences tab


def display_credential_set(credManager, set_id, creds, is_expanded=False):
    """Display a credential set with platforms and actions."""
    # No need to load CSS here as it's loaded globally

    with st.expander(creds["name"], expanded=is_expanded):
        # Get current credentials
        username = creds["username"]
        password = creds["password"]

        # Create state key for this credential set to track reveal state
        reveal_key = f"reveal_{set_id}"
        if reveal_key not in st.session_state:
            st.session_state[reveal_key] = False

        # Horizontal layout for form fields
        col1, col2 = st.columns(2)

        # Username field (masked by default unless revealed)
        with col1:
            if st.session_state[reveal_key]:
                displayed_username = username
            else:
                displayed_username = (
                    username[:3] + "*" * (len(username) - 3) if username else ""
                )

            st.text_input(
                "Username/Email",
                value=displayed_username,
                key=f"username_{set_id}",
                disabled=True,
            )

        # Password field (masked by default unless revealed)
        with col2:
            if st.session_state[reveal_key]:
                displayed_password = password
                # Can't use "text" type, so don't specify type at all for revealed password
                st.text_input(
                    "Password",
                    value=displayed_password,
                    key=f"password_{set_id}",
                    disabled=True,
                )
            else:
                displayed_password = "*" * len(password) if password else ""
                st.text_input(
                    "Password",
                    value=displayed_password,
                    type="password",
                    key=f"password_{set_id}",
                    disabled=True,
                )

        # If no platforms are mapped to this set
        if not creds["platforms"]:
            st.info("No platforms assigned to this credential set")
        else:
            # Show platforms in a multiselect dropdown (non-interactive)
            st.multiselect(
                "Platforms",
                options=sorted(credManager.get_all_platforms()),
                default=creds["platforms"],
                disabled=True,
                key=f"platforms_{set_id}",
            )

        # Action buttons in a horizontal layout with equal spacing (no divider)
        button_cols = st.columns([1, 1, 1])

        # Show/Hide button
        with button_cols[0]:
            button_label = "Hide" if st.session_state[reveal_key] else "Show"
            if st.button(button_label, key=f"show_{set_id}"):
                st.session_state[reveal_key] = not st.session_state[reveal_key]
                st.rerun()

        # Edit button
        with button_cols[1]:
            if st.button("Edit", key=f"edit_{set_id}"):
                st.session_state.editing_credential_set = set_id
                st.rerun()

        # Delete button
        with button_cols[2]:
            if st.button("Delete", key=f"delete_{set_id}"):
                # Directly delete without confirmation for now
                if credManager.remove_credential_set(set_id):
                    st.success("Credential set deleted!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to delete credential set")


def credential_set_form(
    credManager, set_id=None, name="", username="", password="", platforms=None
):
    """Form for creating or editing a credential set."""

    # CSS is loaded globally

    # Default to empty list if platforms not provided
    if platforms is None:
        platforms = []

    # Get unmapped platforms (available to assign)
    available_platforms = credManager.get_unmapped_platforms()

    # If editing, add currently assigned platforms back to the available list
    if set_id:
        for platform in platforms:
            if platform not in available_platforms:
                available_platforms.append(platform)

    # Check for duplicate credentials
    def check_duplicate_credentials(username, password, current_set_id=None):
        credential_sets = credManager.get_all_credential_sets()
        for set_id, creds in credential_sets.items():
            if (
                set_id != current_set_id
                and creds["username"] == username
                and creds["password"] == password
            ):
                return creds["name"]
        return None

    with st.form(key=f"credential_set_form_{set_id or 'new'}"):
        # Form fields in horizontal layout for all fields
        col1, col2, col3 = st.columns(3)

        # Credential set name
        with col1:
            name = st.text_input("Set Name", value=name)

        # Username field
        with col2:
            username = st.text_input("Username/Email", value=username)

        # Password field
        with col3:
            password_type = (
                "text"
                if set_id and "show_password_edit" in st.session_state
                else "password"
            )
            new_password = st.text_input(
                "Password", value=password if set_id else "", type=password_type
            )

            # If editing, we'll use the new password if provided, otherwise keep the original
            if set_id and not new_password:
                # Keep original password
                password = password
            else:
                password = new_password

        # Sort platforms alphabetically
        available_platforms.sort()

        # Create formatted display names for platforms
        platform_display = {}
        for platform in available_platforms:
            if platform == "workday_common":
                platform_display[platform] = "Workday Common"
            else:
                platform_display[platform] = platform.title()

        # Use multiselect to choose platforms with formatted display names
        selected_platforms = st.multiselect(
            "Platforms",
            options=available_platforms,
            default=[p for p in platforms if p in available_platforms],
            format_func=lambda x: platform_display[x],
        )

        # Submit and cancel buttons
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("Save", use_container_width=True)

        with col2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

        # Process form submission
        if submitted:
            if not name:
                st.error("Please provide a name for this credential set")
                return False

            if not username:
                st.error("Please provide a username")
                return False

            if not password and not set_id:
                st.error("Please provide a password")
                return False

            # Check for duplicate credentials
            # Check for duplicates, but do this outside the form after submission
            duplicate_set = check_duplicate_credentials(username, password, set_id)
            if duplicate_set:
                st.error(
                    f"'{duplicate_set}' has the same credentials. Please update its mapping or delete it before creating a new set with the same combination."
                )
                return False

            # Save the credential set
            credManager.save_credential_set(
                set_id=set_id,
                name=name,
                username=username,
                password=password,
                platforms=selected_platforms,
            )

            st.success("Credential set saved successfully!")

            # Clear editing state if present
            if "editing_credential_set" in st.session_state:
                del st.session_state.editing_credential_set

            # Clear adding state if present
            if "adding_credential_set" in st.session_state:
                st.session_state.adding_credential_set = False

            time.sleep(1)
            st.rerun()

            return True

        # Handle cancel button
        if cancelled:
            # Clear editing state if present
            if "editing_credential_set" in st.session_state:
                del st.session_state.editing_credential_set

            # Clear adding state if present
            if "adding_credential_set" in st.session_state:
                st.session_state.adding_credential_set = False

            st.rerun()
            return False

    return False


def setupCreds_tab(credManager):
    """Setup credentials tab content."""

    # Get all credential sets
    credential_sets = credManager.get_all_credential_sets()

    # Initialize password visibility state
    if "show_all_passwords" not in st.session_state:
        st.session_state.show_all_passwords = False

    # CSS is loaded globally

    # Create a two-column layout with the header on the left and buttons on the right
    col1, col2 = st.columns([3, 2])

    with col1:
        # Add the header at the correct size
        st.header("Saved Credentials")

    with col2:
        # Create a 2-column subgrid for the buttons inside the right column
        button_col1, button_col2 = st.columns(2)

        # Add button
        with button_col1:
            if st.button("➕ Add", key="add_creds_btn", use_container_width=True):
                st.session_state.adding_credential_set = True
                st.rerun()

        # Show/Hide button
        with button_col2:
            btn_text = "👁️ Hide" if st.session_state.show_all_passwords else "👁️ Show"
            if st.button(btn_text, key="show_passwords_btn", use_container_width=True):
                st.session_state.show_all_passwords = (
                    not st.session_state.show_all_passwords
                )
                st.rerun()

    # Display credentials as cards
    if credential_sets:
        # Load credential card template
        card_template = load_html_template(get_html_path("credential_card.html"))

        # Create rows with 3 columns per row
        sets_list = list(credential_sets.items())
        for i in range(0, len(sets_list), 3):
            row_sets = sets_list[i : i + 3]
            cols = st.columns(3)  # Always create 3 columns

            for idx, (set_id, creds) in enumerate(row_sets):
                if idx < len(row_sets):  # Only process actual credential sets
                    with cols[idx]:
                        # Get credential values
                        username = creds["username"]
                        password = creds["password"]

                        # Use global password visibility setting
                        if st.session_state.show_all_passwords:
                            display_password = password
                        else:
                            display_password = "*" * len(password) if password else ""

                        # Generate platform text as comma-separated list with proper formatting
                        formatted_platforms = []
                        for platform in creds["platforms"]:
                            if platform == "workday_common":
                                formatted_platforms.append("Workday Common")
                            else:
                                formatted_platforms.append(platform.title())
                        platforms_text = ", ".join(formatted_platforms)

                        # Render the card template
                        card_html = render_template(
                            card_template,
                            set_id=set_id,
                            name=creds["name"],
                            username=username,
                            password=display_password,
                            platforms=platforms_text,
                        )

                        # Display the card
                        st.markdown(card_html, unsafe_allow_html=True)

                        # Add Edit and Delete buttons below the card with no horizontal gap
                        st.markdown(
                            '<div style="display: flex; gap: 0px; margin-top: 5px;">',
                            unsafe_allow_html=True,
                        )

                        # Edit button (50% width)
                        if st.button(
                            "Edit", key=f"edit_{set_id}", use_container_width=True
                        ):
                            st.session_state.editing_credential_set = set_id
                            st.rerun()

                        # Delete button (50% width)
                        if st.button(
                            "Delete", key=f"delete_{set_id}", use_container_width=True
                        ):
                            if credManager.remove_credential_set(set_id):
                                st.success(f"Deleted credential set: {creds['name']}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to delete credential set")

                        st.markdown("</div>", unsafe_allow_html=True)

    # Check if we're in editing mode
    editing_id = st.session_state.get("editing_credential_set")

    # If editing, show the form for that set with a header and horizontal line
    if editing_id and editing_id in credential_sets:
        st.markdown(
            "<hr style='margin-top: 30px; margin-bottom: 20px;'>",
            unsafe_allow_html=True,
        )
        st.header("Edit Credential")

        creds = credential_sets[editing_id]
        credential_set_form(
            credManager,
            set_id=editing_id,
            name=creds["name"],
            username=creds["username"],
            password=creds["password"],
            platforms=creds["platforms"],
        )

    # If there are no credentials at all, show an info message
    if not credential_sets and not editing_id:
        st.info(
            "You haven't added any credentials yet. Click 'Add Credentials' to get started."
        )

    # Show form for new credential set if requested with header and horizontal line
    if not editing_id and st.session_state.get("adding_credential_set", False):
        st.markdown(
            "<hr style='margin-top: 30px; margin-bottom: 20px;'>",
            unsafe_allow_html=True,
        )
        st.header("Add Credential")
        credential_set_form(credManager)


def setupExport_tab(preferences):
    """Setup export tab content."""
    st.header("Export Preferences")
    st.write("Export your job search preferences as a JSON file.")

    if st.button("Export as JSON"):
        export_json = json.dumps(preferences, indent=2)
        st.download_button(
            label="Download JSON",
            data=export_json,
            file_name="job_search_preferences.json",
            mime="application/json",
        )


# Function removed - Save button is now directly in the main app.py file
