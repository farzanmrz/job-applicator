import json
import os
import time

import streamlit as st
from utils.JobSearchPreferences import JobSearchPreferences


class LinkedInAuth:
    """Class to handle LinkedIn credential storage."""

    def __init__(self):
        self.credentials_file = "data/linkedin_credentials.json"
        os.makedirs("data", exist_ok=True)

    def save_credentials(self, username, password):
        """Save LinkedIn credentials to file."""
        # WARNING: In a production environment, you would want to encrypt these credentials
        credentials = {
            "username": username,
            "password": password,
            "saved_at": time.time(),
        }

        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f)

        return True

    def get_credentials(self):
        """Get LinkedIn credentials from file if they exist."""
        try:
            with open(self.credentials_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None


def add_linkedin_auth_to_sidebar():
    """Add LinkedIn authentication UI to the sidebar."""
    st.sidebar.header("LinkedIn Authentication")

    auth = LinkedInAuth()
    credentials = auth.get_credentials()

    if credentials:
        st.sidebar.success(f"✓ LinkedIn credentials saved")
        st.sidebar.info(f"Username: {credentials['username']}")

        if st.sidebar.button("Remove LinkedIn Credentials"):
            os.remove(auth.credentials_file)
            st.sidebar.info("LinkedIn credentials removed")
            st.experimental_rerun()
    else:
        with st.sidebar.form("linkedin_auth_form"):
            username = st.text_input("LinkedIn Email/Username")
            password = st.text_input("LinkedIn Password", type="password")
            submitted = st.form_submit_button("Save Credentials")

            if submitted and username and password:
                with st.sidebar:
                    with st.spinner("Saving credentials..."):
                        if auth.save_credentials(username, password):
                            st.success("LinkedIn credentials saved!")
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error("Failed to save credentials.")


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Job Search Preferences", page_icon="🔍", layout="wide"
    )

    st.title("Job Search Preferences")
    st.write("Configure your job search criteria")

    # Add LinkedIn authentication to sidebar
    add_linkedin_auth_to_sidebar()

    # Initialize preferences manager
    pref_manager = JobSearchPreferences()
    preferences = pref_manager.get_preferences()

    # Create tabs for different sections
    tabs = st.tabs(["Basic Preferences", "Skills & Keywords", "Export"])

    # Basic Preferences Tab
    with tabs[0]:
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

    # Skills & Keywords Tab
    with tabs[1]:
        st.header("Skills & Keywords")

        # Technical Skills
        st.subheader("Technical Skills")

        # Display existing skills
        if preferences["technical_skills"]:
            for i, skill in enumerate(preferences["technical_skills"]):
                col1, col2 = st.columns([4, 1])
                col1.write(f"• {skill}")
                if col2.button("Remove", key=f"remove_tech_{i}"):
                    preferences["technical_skills"].remove(skill)
                    st.experimental_rerun()

        # Add new technical skill
        new_tech_skill = st.text_input("Add a technical skill:")
        if (
            st.button("Add Technical Skill")
            and new_tech_skill
            and new_tech_skill not in preferences["technical_skills"]
        ):
            preferences["technical_skills"].append(new_tech_skill)
            st.success(f"Added: {new_tech_skill}")
            st.experimental_rerun()

        # Soft Skills
        st.subheader("Soft Skills")

        # Display existing soft skills
        if preferences["soft_skills"]:
            for i, skill in enumerate(preferences["soft_skills"]):
                col1, col2 = st.columns([4, 1])
                col1.write(f"• {skill}")
                if col2.button("Remove", key=f"remove_soft_{i}"):
                    preferences["soft_skills"].remove(skill)
                    st.experimental_rerun()

        # Add new soft skill
        new_soft_skill = st.text_input("Add a soft skill:")
        if (
            st.button("Add Soft Skill")
            and new_soft_skill
            and new_soft_skill not in preferences["soft_skills"]
        ):
            preferences["soft_skills"].append(new_soft_skill)
            st.success(f"Added: {new_soft_skill}")
            st.experimental_rerun()

        # Job Titles
        st.subheader("Target Job Titles")

        # Display existing job titles
        if preferences["job_titles"]:
            for i, title in enumerate(preferences["job_titles"]):
                col1, col2 = st.columns([4, 1])
                col1.write(f"• {title}")
                if col2.button("Remove", key=f"remove_title_{i}"):
                    preferences["job_titles"].remove(title)
                    st.experimental_rerun()

        # Add new job title
        new_job_title = st.text_input("Add a job title:")
        if (
            st.button("Add Job Title")
            and new_job_title
            and new_job_title not in preferences["job_titles"]
        ):
            preferences["job_titles"].append(new_job_title)
            st.success(f"Added: {new_job_title}")
            st.experimental_rerun()

    # Export Tab
    with tabs[2]:
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

    # Save button (always visible)
    if st.sidebar.button("Save All Preferences"):
        pref_manager.save_preferences(preferences)
        st.sidebar.success("Preferences saved successfully!")


if __name__ == "__main__":
    main()
