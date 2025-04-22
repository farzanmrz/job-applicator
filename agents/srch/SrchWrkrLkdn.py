# General Imports
import json
import os
import sys
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

        # 1b. Initialize instance variables
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

    def _get_formLabels(self, page: Page) -> List[str]:
        """Extract form field labels from the preferences modal.

        Args:
            page: The Playwright page object containing the modal.

        Returns:
            List of strings containing the cleaned form field labels.

        Raises:
            Exception: If modal is not found or timeout occurs.
        """
        logger.info("Looking for modal dialog...")
        modal_locator = page.locator(
            '[role="dialog"][aria-labelledby="po-route-modal-header-onboarding"]'
        )

        try:
            # Wait for the element to be visible
            modal_locator.wait_for(state="visible", timeout=5000)  # 5 second timeout
            logger.info("Modal found, extracting form field labels...")

            # Locate all relevant span elements within the modal
            label_spans = modal_locator.locator("span.fb-dash-form-element__label")
            logger.info(f"Found {label_spans.count()} potential label spans.")

            # Extract and clean label texts
            form_field_labels = []
            for i in range(label_spans.count()):
                span_text = label_spans.nth(i).text_content()
                if span_text:  # Ensure text is not empty
                    cleaned_label = " ".join(span_text.split())  # Clean whitespace
                    if cleaned_label:  # Ensure not just whitespace after cleaning
                        form_field_labels.append(cleaned_label)
                        logger.info(f"  - Extracted field: {cleaned_label}")

            return form_field_labels

        except Exception as timeout_error:
            if "Timeout" in str(timeout_error):
                logger.error(
                    f"Modal did not become visible within timeout: {timeout_error}"
                )
                page.screenshot(path="debug_screenshot_modal_not_visible.png")
            raise timeout_error

    def _extract_form_data(self, page: Page) -> Dict[str, Dict[str, Any]]:
        """Extracts form field labels and specifically identifies multi-select pill data."""
        logger.info("Looking for modal dialog...")
        modal_locator = page.locator(
            '[role="dialog"][aria-labelledby="po-route-modal-header-onboarding"]'
        )
        form_data = {}

        try:
            modal_locator.wait_for(state="visible", timeout=5000)
            logger.info("Modal found. Locating form field containers (fieldsets)...")

            # Locate all potential fieldset containers
            containers = modal_locator.locator("fieldset")
            container_count = containers.count()
            logger.info(f"Found {container_count} potential fieldset containers.")

            for i in range(container_count):
                container = containers.nth(i)
                label = ""
                field_info = {
                    "type": "N/A",
                    "available_options": [],
                    "selected_options": [],
                }

                # Extract Label from within container
                label_span = container.locator("span.fb-dash-form-element__label").first
                if label_span:
                    label_text = label_span.text_content()
                    if label_text:
                        label = " ".join(label_text.split())

                if not label:
                    logger.warning(f"Could not find label for container {i}. Skipping.")
                    continue

                logger.info(f"Processing field: {label}")

                # Check for Pill Buttons first
                all_pills = container.locator(
                    "button.artdeco-pill span.artdeco-pill__text"
                )
                if all_pills.count() > 0:
                    field_info["type"] = "multi-select-pill"
                    # Get all available options
                    avail_options = all_pills.all_text_contents()
                    field_info["available_options"] = [
                        opt.strip() for opt in avail_options if opt
                    ]
                    # Get selected options
                    selected_pills = container.locator(
                        "button.artdeco-pill--selected span.artdeco-pill__text"
                    )
                    sel_options = selected_pills.all_text_contents()
                    field_info["selected_options"] = [
                        opt.strip() for opt in sel_options if opt
                    ]
                    logger.info(
                        f"  Type: Pill Buttons\n    Available: {field_info['available_options']}\n    Selected: {field_info['selected_options']}"
                    )
                else:
                    # Check for Radio Buttons
                    all_radio_labels = container.locator(
                        "label[data-test-text-selectable-option__label]"
                    )
                    if all_radio_labels.count() > 0:
                        field_info["type"] = "radio"
                        # Get all available options
                        avail_options = all_radio_labels.all_text_contents()
                        field_info["available_options"] = [
                            opt.strip() for opt in avail_options if opt
                        ]

                        # Get selected option
                        checked_radio = container.locator('input[type="radio"]:checked')
                        if checked_radio.count() == 1:
                            # Find the label associated with the checked input
                            parent_div = checked_radio.locator(
                                "xpath=./ancestor::div[contains(@class, 'display-flex')]"
                            )
                            if parent_div.count() == 1:
                                selected_label = parent_div.locator(
                                    "label[data-test-text-selectable-option__label]"
                                )
                                if selected_label.count() == 1:
                                    sel_label_text = selected_label.text_content()
                                    if sel_label_text:
                                        field_info["selected_options"] = [
                                            " ".join(sel_label_text.split())
                                        ]
                                    else:
                                        logger.warning(
                                            f"  Label for checked radio in '{label}' is empty."
                                        )
                                else:
                                    logger.warning(
                                        f"  Could not find specific label for checked radio in '{label}'."
                                    )
                            else:
                                logger.warning(
                                    f"  Could not find parent div for checked radio in '{label}'."
                                )
                        elif checked_radio.count() == 0:
                            logger.info(f"  No radio button selected for '{label}'.")
                        else:  # More than 1 checked? Should not happen for radios.
                            logger.warning(
                                f"  Found multiple checked radios for '{label}'."
                            )

                        logger.info(
                            f"  Type: Radio\n    Available: {field_info['available_options']}\n    Selected: {field_info['selected_options']}"
                        )

                    # If neither pills nor radio buttons were identified, type remains "N/A"
                    if field_info["type"] == "N/A":
                        logger.info(f"  Type: Not Pill or Radio (N/A)")

                form_data[label] = field_info

            return form_data

        except Exception as error:
            if "Timeout" in str(error):
                logger.error(f"Modal or container finding timed out: {error}")
                page.screenshot(path="debug_screenshot_modal_error.png")
            raise error

    def update_preferences(self):
        """Update job search preferences on LinkedIn"""
        try:
            logger.info(f"Navigating to preferences URL: {self.PREF_URL}")
            page = self.context.new_page()
            page.goto(self.PREF_URL, wait_until="domcontentloaded")

            # Get structured form data (focused on pills)
            form_data = self._extract_form_data(page)

            # Print the resulting dictionary
            print("\n=== Extracted Form Data (Available & Selected Options) ===")
            print(json.dumps(form_data, indent=2))
            print("====================================================\n")

            # Add wait for manual inspection
            logger.info("Pausing for 30 minutes to allow form field inspection...")
            page.wait_for_timeout(1800_000)  # Wait for 30 minutes (in ms)
            logger.info("Inspection pause finished.")

        except Exception as e:
            logger.error(f"Error in update_preferences: {str(e)}")
            raise

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
