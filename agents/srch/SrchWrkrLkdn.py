# General Imports
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Playwright imports
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)
from pydantic import Field

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Agent setup imports
from agents.AgtBase import AgtBase, EnumAgtType
from tools.auth.TlAuthLkdn import TlAuthLkdn
from tools.lang.form_matcher import tlform_comparer

# Utility/tool imports
from utils.commonutil import set_logger

# Set up logger with custom format and name of current module
logger = set_logger("SrchWrkrLkdn")


class SrchWrkrLkdn(AgtBase):
    """Worker agent responsible for LinkedIn-specific job search operations and authentication"""

    def __init__(self, headless: bool = True):
        """Initialize the LinkedIn Search Worker Agent"""
        # 1a. Initialize the base class with the inherited constructor
        super().__init__(agt_type=EnumAgtType.WRKR, agt_pid="defaultpid.000000")
        logger.info(f"Search Worker LinkedIn initialized with ID {self.agt_id}")

        # 1b. Load user preferences
        with open("data/usr_prefs.json", "r") as f:
            self.usr_prefs = json.load(f)

        # 1c. Initialize instance variables
        self.headless = headless
        self.BASE_URL = "https://www.linkedin.com"
        self.LOGIN_URL = "https://www.linkedin.com/login"
        self.CAPTCHA_URL = "https://www.linkedin.com/checkpoint/challenge/"
        self.ERROR_URL = "https://www.linkedin.com/checkpoint/lg/login-submit"
        self.FEED_URL = "https://www.linkedin.com/feed/"
        self.PREF_URL = "https://www.linkedin.com/jobs/opportunities/job-opportunities/onboarding/?jobOpportunitiesOrigin=JOB_SEEKING_PREFERENCES"

        # 1c. Initialize Playwright-related attributes as None
        self.p = None
        self.browser = None
        self.auth_tool = None
        self.context = None
        self.pg = None

    def run(self, update_prefs: bool = True):
        """Main entry point for the agent's workflow"""
        try:
            # Task 1: Authentication
            self.active_tasks["authenticate"] = "started"
            self.authenticate()
            self.active_tasks["authenticate"] = "completed"

            # Task 2: Update Preferences (if flag is True)
            if update_prefs:
                self.active_tasks["update_preferences"] = "started"
                self.update_preferences()
                self.active_tasks["update_preferences"] = (
                    "incomplete"  # Mark as incomplete since not fully implemented
                )

            # Task 3: Search Jobs
            self.active_tasks["search_jobs"] = "started"
            self.search_jobs()
            self.active_tasks["search_jobs"] = (
                "incomplete"  # Mark as incomplete since not fully implemented
            )

        except Exception as e:
            logger.error(f"Error in run: {str(e)}")
            # Mark current task as failed
            for task in ["authenticate", "update_preferences", "search_jobs"]:
                if task in self.active_tasks and self.active_tasks[task] == "started":
                    self.active_tasks[task] = f"failed: {str(e)}"
            raise

    def authenticate(self):
        """Handle LinkedIn authentication and browser context setup"""
        try:
            self.p = sync_playwright().start()
            self.browser = self.p.chromium.launch(headless=self.headless)
            self.auth_tool = TlAuthLkdn()
            self.context = self.auth_tool.get_valid_context(self.browser)

            if not self.context:
                logger.critical("Failed to obtain valid browser context.")
                raise Exception(
                    "Authentication failed: Could not obtain valid browser context"
                )
            else:
                logger.info("Context created successfully.")

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise

    # New update preferences method going slowly through implementation
    def update_preferences(self):
        """Update job search preferences on LinkedIn"""
        try:
            # Navigate to the preferences URL and wait for the page to load
            logger.info(f"1. Navigating to preferences URL: {self.PREF_URL}")
            self.pg = self.context.new_page()
            self.pg.goto(self.PREF_URL, wait_until="domcontentloaded")

            # Fill form with user preferences
            logger.info("2. Filling form with user preferences")
            self.fill_prefForm()
            logger.info("2a. Pause after fill")
            time.sleep(600000)

        except Exception as e:
            logger.error(f"Error in update_preferences: {str(e)}")
            raise

    def get_currForm(self):
        """Placeholder for retrieving current form data using self.pg."""

        # Init dict to store pre-filled form values
        form_data = {}

        # # Define initial modal_locator
        # modal_locator = self.pg.locator(
        #     '[role="dialog"][aria-labelledby="po-route-modal-header-onboarding"]'
        # )

        # Try block for general functionality
        try:
            # Wait for the modal to be visible
            # modal_locator.wait_for(state="visible", timeout=5000)
            logger.info("2a) Modal found")

            # Find all potential fieldset containers and throw error if not 7
            fields = self.pg.locator(
                '[role="dialog"][aria-labelledby="po-route-modal-header-onboarding"]'
            ).locator("fieldset")
            if fields.count() != 7:
                logger.error(
                    f"Expected 7 fieldset containers, but found {fields.count()}. Aborting form extraction."
                )
                return None

            # Go through each field
            for i in range(fields.count()):

                # Get individual field
                field = fields.nth(i)

                # Set label
                label = (
                    field.locator("span.fb-dash-form-element__label")
                    .first.text_content()
                    .strip()
                )

                # Initialize form data entry
                form_data[label] = {"type": None, "opt_y": None, "opt_n": None}

                # Check for checkbox pills first
                checked_pills = field.locator(
                    'button[role="checkbox"][aria-checked="true"] span.artdeco-pill__text'
                )
                if checked_pills.count() > 0:
                    # This is a checkbox field
                    form_data[label]["type"] = "checkbox"
                    form_data[label]["opt_y"] = [
                        checked_pills.nth(j).text_content().strip()
                        for j in range(checked_pills.count())
                    ]
                    # Get unchecked options
                    unchecked_pills = field.locator(
                        'button[role="checkbox"][aria-checked="false"] span.artdeco-pill__text'
                    )
                    form_data[label]["opt_n"] = [
                        unchecked_pills.nth(j).text_content().strip()
                        for j in range(unchecked_pills.count())
                    ]
                else:
                    # Check for multiadd pills
                    selected_pills = field.locator(
                        "button.artdeco-pill--selected span.artdeco-pill__text"
                    )
                    if selected_pills.count() > 0:
                        form_data[label]["type"] = "multiadd"
                        form_data[label]["opt_y"] = [
                            selected_pills.nth(j).text_content().strip()
                            for j in range(selected_pills.count())
                        ]
                    else:
                        # Check for radio buttons
                        radio_inputs = field.locator('input[type="radio"]')
                        if radio_inputs.count() > 0:
                            form_data[label]["type"] = "radio"
                            form_data[label]["opt_y"] = []
                            form_data[label]["opt_n"] = []
                            for j in range(radio_inputs.count()):
                                radio = radio_inputs.nth(j)
                                # Get associated label using the input's ID
                                label_for = radio.get_attribute("id")
                                label_text = (
                                    field.locator(f'label[for="{label_for}"]')
                                    .text_content()
                                    .strip()
                                )
                                if radio.is_checked():
                                    form_data[label]["opt_y"].append(label_text)
                                else:
                                    form_data[label]["opt_n"].append(label_text)

            # Debug print the form_data
            print("\n=== Extracted Form Data ===")
            print(json.dumps(form_data, indent=2))
            print("===========================\n")

        # Except error raise and screenshot
        except Exception as e:
            logger.error(f"2a) Error in get_currForm {str(e)}")
            self.pg.screenshot(path="get_currForm_err.png")
            raise e

        # Pause for 10 minutes for manual inspection
        logger.info("Pausing for 10 minutes...")
        self.pg.wait_for_timeout(600_000)
        logger.info("Pause finished.")
        self.pg.close()

    def fill_prefForm(self):
        """Fill form fields with user preferences, handling dynamic field appearance."""

        # General dict and dialogbox setup
        pre_form = {}
        main_dialogBox = self.pg.locator(
            '[role="dialog"][aria-labelledby="po-route-modal-header-onboarding"]'
        )

        # CHECKBOX: Retrieval part
        f_loctype = main_dialogBox.locator(
            'fieldset:has(button[role="checkbox"][aria-checked] span.artdeco-pill__text)'
        ).first
        buttons = f_loctype.locator(
            'button[role="checkbox"][aria-checked] span.artdeco-pill__text'
        )
        print(f"Found checkbox buttons: {buttons.count()}")
        label = (
            f_loctype.locator("span.fb-dash-form-element__label")
            .first.text_content()
            .strip()
        )
        checked = f_loctype.locator(
            'button[role="checkbox"][aria-checked="true"] span.artdeco-pill__text'
        )
        unchecked = f_loctype.locator(
            'button[role="checkbox"][aria-checked="false"] span.artdeco-pill__text'
        )
        pre_form[label] = {
            "type": "checkbox",
            "opt_y": [
                checked.nth(i).text_content().strip() for i in range(checked.count())
            ],
            "opt_n": [
                unchecked.nth(i).text_content().strip()
                for i in range(unchecked.count())
            ],
        }
        print(pre_form)

        # CHECKBOX FILLING PART
        tlform_comparer(pre_form[label], self.usr_prefs)

    def search_jobs(self):
        """Search for jobs based on preferences"""
        # Stub for now - will be implemented later
        logger.info("Search jobs stub called.")


# For testing
if __name__ == "__main__":
    agent = SrchWrkrLkdn(headless=False)
    try:
        agent.run()
        print("Final task statuses:", agent.active_tasks)
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        print("Task statuses at error:", agent.active_tasks)
