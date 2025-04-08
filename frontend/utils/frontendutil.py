import json
import time
import streamlit as st
import os


def decrypt_all_credentials(credManager):
    """Get all decrypted credentials including their platforms."""
    credential_sets = credManager.get_all_credential_sets()
    
    result = []
    for set_id, creds in credential_sets.items():
        result.append({
            "set_id": set_id,
            "name": creds["name"],
            "username": creds["username"],
            "password": creds["password"],
            "saved_at": creds.get("saved_at", 0),
            "platforms": creds.get("platforms", [])
        })
    
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

    st.title("Job Search Preferences")
    st.write("Configure your job search criteria")


def setupTabs():
    """Create tabs for different sections."""
    return st.tabs(["Basic Preferences", "Skills & Keywords", "Credentials", "Export"])


def setupBasic_prefs(preferences):
    """Setup basic preferences tab content."""
    st.header("Basic Job Search Preferences")

    # Education Level
    st.subheader("Highest Level of Education")
    education_options = ["None", "High School", "Bachelor's", "Master's", "PhD"]
    preferences["education"] = st.radio(
        "Select your highest education level:",
        options=education_options,
        index=(
            education_options.index(preferences["education"])
            if preferences["education"] in education_options
            else 0
        ),
    )

    # Industries
    st.subheader("Industries")
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
        "Select industries you're interested in:",
        options=industry_options,
        default=preferences["industries"],
    )

    # Countries
    st.subheader("Countries")
    country_options = [
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
    preferences["countries"] = st.multiselect(
        "Select countries you're interested in:",
        options=country_options,
        default=preferences["countries"],
    )

    # Job Type
    st.subheader("Job Type")
    job_type_options = [
        "Full-time",
        "Part-time",
        "Remote",
        "Internship",
        "Contract",
        "Other",
    ]
    preferences["job_type"] = st.multiselect(
        "Select job types you're interested in:",
        options=job_type_options,
        default=preferences["job_type"],
    )

    # Job Experience
    st.subheader("Job Experience")
    job_exp_options = [
        "Entry-Level",
        "1-2 years",
        "2-4 years",
        "4+ years",
        "Senior/Executive",
    ]
    preferences["job_experience"] = st.multiselect(
        "Select experience levels:",
        options=job_exp_options,
        default=preferences["job_experience"],
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

    # Job Titles
    handleSkillList(preferences, "job_titles", "Target Job Titles")


def display_credential_set(credManager, set_id, creds, is_expanded=False):
    """Display a credential set with platforms and actions."""
    with st.expander(creds["name"], expanded=is_expanded):
        # Two-column layout for the credential set
        col1, col2 = st.columns([3, 1])
        
        # Username and password section
        with col1:
            # Get current credentials
            username = creds["username"]
            password = creds["password"]
            
            # Username field (masked by default)
            user_col, show_user = st.columns([4, 1])
            with user_col:
                masked_username = username[:3] + "*" * (len(username) - 3) if username else ""
                displayed_username = st.text_input(
                    "Username/Email", 
                    value=masked_username, 
                    key=f"username_{set_id}", 
                    disabled=True
                )
            
            # Password field (masked by default)
            pass_col, show_pass = st.columns([4, 1])
            with pass_col:
                masked_password = "*" * len(password) if password else ""
                displayed_password = st.text_input(
                    "Password", 
                    value=masked_password, 
                    type="password",
                    key=f"password_{set_id}", 
                    disabled=True
                )
            
            # Show button to reveal actual credentials
            reveal = show_user.button("Show", key=f"show_{set_id}")
            if reveal:
                user_col.text_input("Username/Email", value=username, key=f"username_reveal_{set_id}")
                pass_col.text_input("Password", value=password, key=f"password_reveal_{set_id}")
        
        # Action buttons
        with col2:
            # Delete button
            if st.button("Delete", key=f"delete_{set_id}"):
                if credManager.remove_credential_set(set_id):
                    st.success("Credential set deleted!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to delete credential set")
            
            # Edit button
            if st.button("Edit", key=f"edit_{set_id}"):
                st.session_state.editing_credential_set = set_id
                st.rerun()
        
        # Platform assignments
        st.subheader("Assigned Platforms")
        
        # If no platforms are mapped to this set
        if not creds["platforms"]:
            st.info("No platforms assigned to this credential set")
        
        # Show platforms in a horizontal layout
        platform_cols = st.columns(3)
        for i, platform in enumerate(creds["platforms"]):
            with platform_cols[i % 3]:
                st.markdown(f"✓ **{platform.title()}**")
                
                # Option to remove platform mapping
                if st.button("Unassign", key=f"unassign_{set_id}_{platform}"):
                    # Read existing data
                    with open(credManager.credentials_file, "r") as f:
                        data = json.load(f)
                    
                    # Remove mapping
                    if platform in data["platform_mappings"]:
                        del data["platform_mappings"][platform]
                        
                        # Save updated data
                        with open(credManager.credentials_file, "w") as f:
                            json.dump(data, f)
                        
                        st.success(f"Unassigned {platform}")
                        time.sleep(1)
                        st.rerun()


def credential_set_form(credManager, set_id=None, name="", username="", password="", platforms=None):
    """Form for creating or editing a credential set."""
    
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
    
    with st.form(key=f"credential_set_form_{set_id or 'new'}"):
        # Form title
        st.subheader("Credential Set Details")
        
        # Credential set name
        name = st.text_input("Set Name", value=name)
        
        # Username and password
        username = st.text_input("Username/Email", value=username)
        
        # For new sets, show a regular password field
        # For existing sets, allow viewing the current password and changing it
        if not set_id:
            password = st.text_input("Password", value="", type="password")
        else:
            col1, col2 = st.columns([4, 1])
            with col1:
                view_password = st.checkbox("Show current password", key=f"view_pass_{set_id}")
                if view_password:
                    password = st.text_input("Password", value=password)
                else:
                    masked_password = "*" * len(password) if password else ""
                    password_display = st.text_input("Current Password", value=masked_password, disabled=True)
                    password_changed = st.checkbox("Change password")
                    
                    if password_changed:
                        password = st.text_input("New Password", value="", type="password")
        
        # Platform selection
        st.subheader("Assign to Platforms")
        
        # Sort platforms alphabetically
        available_platforms.sort()
        
        # Use multiselect to choose platforms
        selected_platforms = st.multiselect(
            "Select platforms to use these credentials with:",
            options=available_platforms,
            default=[p for p in platforms if p in available_platforms]
        )
        
        # Submit button
        submitted = st.form_submit_button("Save Credential Set")
        
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
            
            # If we're editing and not changing the password, use the original
            if set_id and not password and not password_changed:
                existing_creds = credManager.get_credential_set(set_id)
                if existing_creds:
                    password = existing_creds["password"]
            
            # Save the credential set
            credManager.save_credential_set(
                set_id=set_id, 
                name=name, 
                username=username, 
                password=password, 
                platforms=selected_platforms
            )
            
            st.success("Credential set saved successfully!")
            
            # Clear editing state if present
            if "editing_credential_set" in st.session_state:
                del st.session_state.editing_credential_set
            
            time.sleep(1)
            st.rerun()
            
            return True
    
    return False


def setupCreds_tab(credManager):
    """Setup credentials tab content."""
    st.header("Platform Credentials")
    st.write("Securely store your credentials for various job application platforms")
    
    # Get all credential sets
    credential_sets = credManager.get_all_credential_sets()
    
    # Check if we're in editing mode
    editing_id = st.session_state.get("editing_credential_set")
    
    # If editing, show the form for that set
    if editing_id and editing_id in credential_sets:
        creds = credential_sets[editing_id]
        st.subheader(f"Edit Credential Set: {creds['name']}")
        
        # Cancel button
        if st.button("Cancel Editing"):
            del st.session_state.editing_credential_set
            st.rerun()
        
        # Display form with existing values
        credential_set_form(
            credManager, 
            set_id=editing_id,
            name=creds["name"],
            username=creds["username"],
            password=creds["password"],
            platforms=creds["platforms"]
        )
        
        # Separator
        st.markdown("---")
    
    # Display platform mapping information
    mapped_platforms = credManager.get_mapped_platforms()
    unmapped_platforms = credManager.get_unmapped_platforms()
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    # Show which platforms have credentials
    with col1:
        st.subheader("Mapped Platforms")
        if mapped_platforms:
            for platform in sorted(mapped_platforms):
                st.markdown(f"✓ **{platform.title()}**")
        else:
            st.info("No platforms have credentials assigned")
    
    # Show which platforms don't have credentials
    with col2:
        st.subheader("Unmapped Platforms")
        if unmapped_platforms:
            for platform in sorted(unmapped_platforms):
                st.markdown(f"❌ **{platform.title()}**")
        else:
            st.success("All platforms have credentials assigned")
    
    # Separator
    st.markdown("---")
    
    # Button to add a new credential set
    if not editing_id and st.button("Add New Credential Set"):
        st.session_state.adding_credential_set = True
    
    # Show form for new credential set if requested
    if not editing_id and st.session_state.get("adding_credential_set", False):
        st.subheader("New Credential Set")
        
        # Cancel button
        if st.button("Cancel"):
            st.session_state.adding_credential_set = False
            st.rerun()
        
        # Display empty form
        credential_set_form(credManager)
        
        # Separator
        st.markdown("---")
    
    # Display existing credential sets
    if credential_sets:
        st.subheader("Your Credential Sets")
        
        # Display each credential set in an expander
        for set_id, creds in credential_sets.items():
            # Skip the one being edited (already shown above)
            if set_id == editing_id:
                continue
            
            # Display credential set
            display_credential_set(credManager, set_id, creds)
    else:
        # No credential sets yet
        st.info("You haven't added any credentials yet. Click 'Add New Credential Set' to get started.")


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


def setupSave_button(prefManager, preferences):
    """Add save button in the sidebar."""
    if st.sidebar.button("Save All Preferences"):
        prefManager.save_prefs(preferences)
        st.sidebar.success("Preferences saved successfully!")