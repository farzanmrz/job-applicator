import json
import logging
import os
import sys
import time
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("linkedin_ui_agent")

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
logger.info(f"Added parent directory to sys.path: {parent_dir}")

# Import browser-use
try:
    from langchain_community.llms import Ollama

    logger.info("Successfully imported Ollama")
except ImportError as e:
    logger.error(f"Failed to import required packages: {str(e)}")
    logger.error("Please install with: pip install langchain-community")
    raise

# Import AgtSearchLdn with explicit path handling
try:
    # Try classes module first (correct structure)
    try:
        from classes.AgtSearchLdn import AgtSearchLdn

        logger.info("Imported AgtSearchLdn from classes package")
    except ImportError:
        # Try importing from current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)

        # Dynamic import based on file existence
        if os.path.exists(os.path.join(current_dir, "AgtSearchLdn.py")):
            # Use importlib for more control
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "AgtSearchLdn", os.path.join(current_dir, "AgtSearchLdn.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            AgtSearchLdn = module.AgtSearchLdn
            logger.info(
                f"Imported AgtSearchLdn directly from file: {os.path.join(current_dir, 'AgtSearchLdn.py')}"
            )
        else:
            raise ImportError(f"Could not find AgtSearchLdn.py in {current_dir}")
except ImportError as e:
    logger.error(f"Failed to import AgtSearchLdn: {str(e)}")
    raise


class LinkedInUIAgent:
    """Agent for LinkedIn UI interaction using manual Playwright interactions."""

    def __init__(self, browser_agent, verbose=True):
        """
        Initialize the LinkedIn UI agent.

        Args:
            browser_agent: Instance of AgtSearchLdn with active Playwright session
            verbose: Whether to enable verbose logging
        """
        self.browser_agent = browser_agent
        self.page = browser_agent.page
        self.verbose = verbose
        logger.info("LinkedIn UI agent initialized successfully")

    def apply_job_preferences(self, preferences: Dict[str, Any]) -> str:
        """
        Apply job search preferences to LinkedIn UI using direct Playwright interaction.

        Args:
            preferences: Dictionary of job preferences to apply

        Returns:
            str: Result message indicating success or failure
        """
        if not self.page or not self.browser_agent:
            logger.error("Browser or page not initialized")
            return "Failed: Browser or page not initialized"

        # Verify we're on the right page
        current_url = self.page.url
        if "job-opportunities" not in current_url and "/jobs/" not in current_url:
            logger.warning(
                f"Not on LinkedIn job preferences page. Current URL: {current_url}"
            )
            return "Failed: Not on LinkedIn job preferences page"

        try:
            # Take initial screenshot
            self.browser_agent.take_screenshot("before_action.png")

            # Wait for the page to load
            logger.info("Waiting for page to fully load...")
            print("\n===================================")
            print("PLEASE WAIT: Page is loading...")
            print("DO NOT close the browser window!")
            print("You can move your mouse off the window - it won't affect the script")
            print("===================================\n")
            time.sleep(1)

            # Debug UI elements on the page
            try:
                logger.info("Analyzing page structure...")
                # Count the number of input fields
                input_count = len(self.page.locator("input").all())
                logger.info(f"Found {input_count} input fields on the page")

                # Count buttons
                button_count = len(self.page.locator("button").all())
                logger.info(f"Found {button_count} buttons on the page")

                # Check for specific text related to job preferences
                for text in [
                    "job title",
                    "location",
                    "remote",
                    "hybrid",
                    "full-time",
                    "part-time",
                ]:
                    elements = self.page.locator(f"text=/{text}/i").all()
                    if elements:
                        logger.info(
                            f"Found elements containing '{text}': {len(elements)}"
                        )

                # Try to identify interactive elements
                self.page.locator('button[aria-expanded="false"]').all()
                dropdowns = len(
                    self.page.locator('button[aria-expanded="false"]').all()
                )
                logger.info(f"Found {dropdowns} potential dropdown elements")

            except Exception as e:
                logger.warning(f"Error during page analysis: {str(e)}")

            logger.info("Starting to interact with the page...")
            result_message = ""

            # Apply job titles if present
            if "job_titles" in preferences:
                result_message += self._set_job_titles(preferences["job_titles"])

            # Apply job type if present
            if "job_type" in preferences:
                result_message += self._set_job_type(preferences["job_type"])

            # Apply modality/remote if present
            if "modality" in preferences:
                result_message += self._set_modality(preferences["modality"])

            # Apply locations if present
            if "locations" in preferences:
                result_message += self._set_locations(preferences["locations"])

            # Try to click Save button
            print("\n>>> TRYING TO SAVE PREFERENCES...")
            try:
                # Try different selectors for save/apply/submit buttons
                save_selectors = [
                    'button:has-text("Save")',
                    'button:has-text("Apply")',
                    'button:has-text("Submit")',
                    'button:has-text("Done")',
                    'button[type="submit"]',
                    'button[aria-label*="save" i]',
                    'button[aria-label*="apply" i]',
                    'button[aria-label*="submit" i]',
                    'footer button',  # Often save buttons are in footers
                    '.form-footer button', # Another common pattern
                ]

                # Take screenshot before trying to save
                before_save_screenshot = self.browser_agent.take_screenshot("before_save.png")
                
                # Get current URL before saving
                url_before_save = self.page.url
                print(f"  URL before saving: {url_before_save}")

                save_button_found = False
                save_button_clicked = False
                for selector in save_selectors:
                    print(f"  Trying to find save button with selector: {selector}")
                    save_buttons = self.page.locator(selector).all()

                    if save_buttons and len(save_buttons) > 0:
                        print(
                            f"  Found {len(save_buttons)} buttons with selector: {selector}"
                        )
                        for button in save_buttons:
                            try:
                                # Check if button is visible
                                is_visible = button.is_visible()
                                print(f"  Button visible: {is_visible}")
                                
                                # Only try to click visible buttons
                                if is_visible:
                                    try:
                                        # Get button text if possible
                                        button_text = button.text_content()
                                        print(f"  Button text: {button_text}")
                                    except:
                                        print("  Could not get button text")
                                
                                    print(f"  Clicking save button...")
                                    button.click()
                                    logger.info("Clicked Save button")
                                    
                                    # Mark that we found and clicked a button
                                    save_button_found = True
                                    save_button_clicked = True
                                    
                                    # Wait for save to complete and page to update
                                    print("  Waiting for save to complete...")
                                    self.page.wait_for_load_state("networkidle", timeout=2000)
                                    time.sleep(0.5)
                                    break
                            except Exception as e:
                                print(f"  Error clicking specific save button: {e}")

                    if save_button_clicked:
                        break

                # Verify if saving worked by checking for various success indicators
                url_after_save = self.page.url
                print(f"  URL after saving: {url_after_save}")
                
                # Check if URL changed (strong signal of successful submission)
                url_changed = url_before_save != url_after_save
                print(f"  URL changed: {url_changed}")
                
                # Look for success messages or toast notifications
                success_message = False
                try:
                    success_selectors = [
                        'div:has-text("Successfully saved")',
                        'div:has-text("Preferences updated")',
                        'div:has-text("Changes saved")',
                        '.toast-success',
                        '[role="alert"]:has-text("saved")'
                    ]
                    
                    for selector in success_selectors:
                        if self.page.locator(selector).count() > 0:
                            success_message = True
                            print(f"  Found success message with selector: {selector}")
                            break
                except Exception as e:
                    print(f"  Error checking for success messages: {e}")
                
                # Check for changes in UI state that indicate success
                ui_state_changed = False
                try:
                    # Check if any previously visible forms or dialogs disappeared
                    input_count_after = len(self.page.locator('input[type="text"]').all())
                    button_count_after = len(self.page.locator('button:has-text("Save"), button:has-text("Apply")').all())
                    
                    print(f"  UI state change assessment - visible forms/dialogs changed: {input_count_after < len(all_inputs)}")
                    print(f"  Save buttons still present: {button_count_after > 0}")
                    
                    # If inputs decreased or save buttons disappeared, UI likely changed
                    ui_state_changed = (input_count_after < len(all_inputs) or button_count_after == 0)
                except Exception as e:
                    print(f"  Error checking UI state changes: {e}")
                
                
                # Determine success status - more comprehensive check
                save_successful = url_changed or success_message or ui_state_changed
                
                if save_button_found:
                    if save_successful:
                        print("  Successfully saved preferences!")
                        result_message += "Successfully saved preferences. "
                    else:
                        print("  Clicked save button but form may not have been submitted successfully")
                        result_message += "Tried to save preferences but submission may not have completed. "
                else:
                    print("  No save button found with any selector")
                    logger.warning("Save button not found")
                    result_message += "Save button not found. "
            except Exception as e:
                logger.error(f"Error clicking Save button: {str(e)}")
                print(f">>> ERROR SAVING PREFERENCES: {str(e)}")
                result_message += "Error saving preferences. "

            # Take final screenshot (only keep before & after)
            self.browser_agent.take_screenshot("after_action.png")
            
            # Remove old screenshots
            try:
                import glob
                import os
                # Get all screenshots except the two we just created
                screenshots_dir = os.path.join(os.getcwd(), "screenshots")
                all_screenshots = glob.glob(os.path.join(screenshots_dir, "*.png"))
                recent_screenshots = [
                    os.path.join(screenshots_dir, f"*before_action.png"),
                    os.path.join(screenshots_dir, f"*after_action.png")
                ]
                # Keep only the most recent before/after pair
                for screenshot in all_screenshots:
                    if "before_action.png" in screenshot or "after_action.png" in screenshot:
                        # Keep the most recent timestamp
                        if not (screenshot.endswith(f"before_action.png") or screenshot.endswith(f"after_action.png")):
                            try:
                                os.remove(screenshot)
                                print(f"Removed old screenshot: {screenshot}")
                            except Exception as e:
                                print(f"Error removing old screenshot: {e}")
            except Exception as e:
                print(f"Error cleaning up screenshots: {e}")

            if not result_message:
                result_message = "No changes made to preferences."

            return f"Result: {result_message}"

        except Exception as e:
            logger.error(f"Error applying preferences: {str(e)}")
            return f"Failed to apply preferences: {str(e)}"

    def _set_job_titles(self, job_titles) -> str:
        """Set job titles in LinkedIn preferences."""
        try:
            print("\n>>> TRYING TO SET JOB TITLES...")

            # Different ways to find job title fields
            selectors = [
                'input[id*="title"]',
                'input[placeholder*="title" i]',
                'input[aria-label*="title" i]',
                'input[placeholder*="search" i]',
                "input:not([disabled])",  # any enabled input as fallback
            ]

            # Try each selector
            job_title_fields = []
            for selector in selectors:
                print(f"  Trying selector: {selector}")
                fields = self.page.locator(selector).all()
                if fields:
                    job_title_fields = fields
                    print(f"  Found {len(fields)} fields with selector: {selector}")
                    break

            if not job_title_fields:
                logger.warning("Job title fields not found")
                print("  No job title fields found!")
                return "Job title fields not found. "

            # Fill in the first job title field found
            titles_set = 0
            for i, title in enumerate(job_titles):
                if i < len(job_title_fields):
                    field = job_title_fields[i]

                    # Try to make sure field is visible and enabled
                    try:
                        print(f"  Clicking on field before typing...")
                        field.click()
                        # Faster interactions with minimal delays
                        # First clear any existing text
                        print(f"  Clearing existing text...")
                        field.fill("")

                        # Then fill with new title
                        print(f"  Setting job title: {title}")
                        field.fill(title)
                        print(f"  Pressing Enter to confirm")
                        field.press("Enter")

                        titles_set += 1
                        logger.info(f"Set job title: {title}")
                        time.sleep(0.5)  # Much shorter delay between interactions
                    except Exception as e:
                        print(f"  Error interacting with field: {e}")
                else:
                    break

            result = f"Set {titles_set} job titles. "
            print(f">>> COMPLETED SETTING JOB TITLES: {result}")
            return result
        except Exception as e:
            logger.error(f"Error setting job titles: {str(e)}")
            print(f">>> ERROR SETTING JOB TITLES: {str(e)}")
            return "Failed to set job titles. "

    def _set_job_type(self, job_types) -> str:
        """Set job type in LinkedIn preferences."""
        try:
            print("\n>>> TRYING TO SET JOB TYPES...")
            print(f"  Job types to set: {job_types}")
            types_set = 0

            # First try to find and click any dropdowns related to job type
            try:
                job_type_dropdowns = self.page.locator(
                    'button:has-text("Job type"), button:has-text("Employment type")'
                ).all()

                if job_type_dropdowns:
                    print(f"  Found job type dropdown, clicking to expand...")
                    job_type_dropdowns[0].click()
                    time.sleep(0.5)  # Wait for dropdown to expand
                    print("  Dropdown expanded, continuing...")
                else:
                    print("  No dropdown found, will try to find job type options directly")
            except Exception as e:
                print(f"  Could not expand job type dropdown: {e}")

            # Look for job type checkboxes or buttons
            for job_type in job_types:
                print(f"  Looking for job type: {job_type}")

                # Try different selectors to find the job type
                selectors = [
                    f'label:has-text("{job_type}")',
                    f'button:has-text("{job_type}")',
                    f'div[role="checkbox"]:has-text("{job_type}")',
                    f'div:has-text("{job_type}"):has(input[type="checkbox"])',
                    f'li:has-text("{job_type}")',
                    # Additional more specific selectors
                    f'label[for*="job-type" i]:has-text("{job_type}")',
                    f'label[for*="employment" i]:has-text("{job_type}")',
                    # Try case insensitive versions
                    f'label:has-text("{job_type.lower()}")',
                    f'label:has-text("{job_type.upper()}")',
                ]

                found = False
                for selector in selectors:
                    print(f"    Trying selector: {selector}")
                    elements = self.page.locator(selector).all()

                    if elements:
                        print(
                            f"    Found {len(elements)} elements with selector: {selector}"
                        )

                        for element in elements:
                            try:
                                # Try to check if this element is visible and clickable
                                is_visible = element.is_visible()
                                print(f"    Element visible: {is_visible}")
                                
                                # Check if it's already selected
                                aria_checked = element.get_attribute("aria-checked")
                                print(f"    Element aria-checked: {aria_checked}")
                                
                                if aria_checked == "true":
                                    print(f"    {job_type} already selected, skipping")
                                    types_set += 1
                                    found = True
                                    break
                                
                                print(f"    Clicking on element...")
                                element.click()
                                time.sleep(0.5)  # Much shorter delay between interactions
                                
                                # Verify it was selected
                                try:
                                    aria_checked_after = element.get_attribute("aria-checked")
                                    print(f"    After click, aria-checked: {aria_checked_after}")
                                    if aria_checked_after == "true":
                                        print(f"    Successfully selected {job_type}")
                                    else:
                                        print(f"    Click may not have selected {job_type}")
                                except Exception as e:
                                    print(f"    Could not verify selection: {e}")
                                
                                logger.info(f"Selected job type: {job_type}")
                                types_set += 1
                                found = True
                                break
                            except Exception as e:
                                print(f"    Error clicking element: {e}")

                        if found:
                            break

                if not found:
                    print(f"  Could not find job type: {job_type}")
                    logger.warning(f"Job type {job_type} not found")

            result = f"Set job types: {', '.join(job_types[:types_set])}. "
            print(f">>> COMPLETED SETTING JOB TYPES: {result}")
            return result
        except Exception as e:
            logger.error(f"Error setting job type: {str(e)}")
            print(f">>> ERROR SETTING JOB TYPES: {str(e)}")
            return "Failed to set job type. "

    def _set_modality(self, modalities) -> str:
        """Set work modality (remote, hybrid, etc.) in LinkedIn preferences."""
        try:
            print("\n>>> TRYING TO SET WORK MODALITY...")
            modalities_set = 0

            # First try to find and click any dropdowns related to modality
            try:
                modality_dropdowns = self.page.locator(
                    'button:has-text("Work mode"), button:has-text("Remote")'
                ).all()

                if modality_dropdowns:
                    print(f"  Found modality dropdown, clicking to expand...")
                    modality_dropdowns[0].click()
                    time.sleep(0.5)  # Wait for dropdown to expand
            except Exception as e:
                print(f"  Could not expand modality dropdown: {e}")

            # Look for modality checkboxes or buttons
            for modality in modalities:
                print(f"  Looking for modality: {modality}")

                # Try different selectors to find the modality
                selectors = [
                    f'label:has-text("{modality}")',
                    f'button:has-text("{modality}")',
                    f'div:has-text("{modality}")',
                    f'li:has-text("{modality}")',
                ]

                found = False
                for selector in selectors:
                    print(f"    Trying selector: {selector}")
                    elements = self.page.locator(selector).all()

                    if elements:
                        print(
                            f"    Found {len(elements)} elements with selector: {selector}"
                        )

                        for element in elements:
                            try:
                                print(f"    Clicking on element...")
                                element.click()
                                time.sleep(0.5)  # Much shorter delay between interactions
                                logger.info(f"Selected modality: {modality}")
                                modalities_set += 1
                                found = True
                                break
                            except Exception as e:
                                print(f"    Error clicking element: {e}")

                        if found:
                            break

                if not found:
                    print(f"  Could not find modality: {modality}")
                    logger.warning(f"Modality {modality} not found")

            result = f"Set modalities: {', '.join(modalities[:modalities_set])}. "
            print(f">>> COMPLETED SETTING MODALITIES: {result}")
            return result
        except Exception as e:
            logger.error(f"Error setting modality: {str(e)}")
            print(f">>> ERROR SETTING MODALITIES: {str(e)}")
            return "Failed to set modality. "

    def _set_locations(self, locations) -> str:
        """Set job locations in LinkedIn preferences."""
        try:
            print("\n>>> TRYING TO SET LOCATIONS...")

            # First try to find section headings for the two location sections
            location_sections = {
                "onsite": None,
                "remote": None
            }
            
            try:
                # Look for section headings
                section_selectors = [
                    'h2:has-text("On-site locations")', 
                    'h3:has-text("On-site locations")',
                    'h2:has-text("Remote locations")',
                    'h3:has-text("Remote locations")',
                    'div:has-text("On-site locations"):not(:has(input))',
                    'div:has-text("Remote locations"):not(:has(input))'
                ]
                
                for selector in section_selectors:
                    sections = self.page.locator(selector).all()
                    for section in sections:
                        try:
                            text = section.text_content().strip().lower()
                            print(f"  Found section: '{text}'")
                            if "on-site" in text or "onsite" in text:
                                location_sections["onsite"] = section
                            elif "remote" in text:
                                location_sections["remote"] = section
                        except Exception as e:
                            print(f"  Error getting section text: {e}")
            except Exception as e:
                print(f"  Error finding section headings: {e}")

            # Identify input fields more precisely
            all_inputs = self.page.locator('input[type="text"]').all()
            print(f"  Found {len(all_inputs)} total text input fields")
            
            # Find all add buttons too
            add_buttons = self.page.locator('button:has-text("Add")').all()
            print(f"  Found {len(add_buttons)} Add buttons")
            
            # Try to look for "add" buttons specifically for locations
            location_add_buttons = []
            for button in add_buttons:
                try:
                    # Get parent elements to see if they're related to locations
                    parent_element = button.locator('xpath=..').first
                    if parent_element:
                        parent_text = parent_element.text_content().lower()
                        if "location" in parent_text:
                            location_add_buttons.append(button)
                            print(f"  Found location add button with parent text: {parent_text}")
                except Exception as e:
                    print(f"  Error checking add button context: {e}")
            
            # Categorize input fields based on position, placeholder text, and nearby labels
            onsite_inputs = []
            remote_inputs = []
            
            for input_field in all_inputs:
                try:
                    placeholder = input_field.get_attribute("placeholder") or ""
                    aria_label = input_field.get_attribute("aria-label") or ""
                    
                    # Get parent elements to find context
                    parent = input_field.locator('xpath=..').first
                    parent_text = ""
                    if parent:
                        parent_text = parent.text_content().lower()
                    
                    print(f"  Input field: placeholder='{placeholder}', aria-label='{aria_label}', parent_text contains 'remote': {'remote' in parent_text}")
                    
                    # Categorize based on attributes and context
                    if ("remote" in placeholder.lower() or 
                        "remote" in aria_label.lower() or 
                        "remote" in parent_text):
                        remote_inputs.append(input_field)
                        print("    Categorized as REMOTE input")
                    else:
                        onsite_inputs.append(input_field)
                        print("    Categorized as ON-SITE input")
                except Exception as e:
                    print(f"  Error categorizing input field: {e}")
            
            print(f"  Categorized {len(onsite_inputs)} on-site inputs and {len(remote_inputs)} remote inputs")
            
            # Clear existing location pills first
            # Look for elements that might be "pills" (selected locations)
            try:
                pills = self.page.locator('[aria-label*="Remove" i], [role="button"]:has(svg)').all()
                for pill in pills:
                    try:
                        text = pill.text_content() or ""
                        aria = pill.get_attribute("aria-label") or ""
                        if "remove" in aria.lower() or "clear" in aria.lower():
                            print(f"  Found location pill: {text}, aria-label: {aria}")
                            pill.click()
                            print(f"  Cleared existing location pill")
                    except Exception as e:
                        print(f"  Error clearing pill: {e}")
            except Exception as e:
                print(f"  Error finding pills: {e}")
                
            # Process the locations
            locations_set = 0
            
            # Set on-site locations
            if onsite_inputs and locations:
                location = locations[0]  # Use first location for on-site
                try:
                    input_field = onsite_inputs[0]
                    
                    print(f"  Setting on-site location: {location}")
                    input_field.click()
                    input_field.fill("")
                    input_field.fill(location)
                    input_field.press("Enter")
                    
                    locations_set += 1
                    logger.info(f"Set on-site location: {location}")
                except Exception as e:
                    print(f"  Error setting on-site location: {e}")
                    
                    # Try using add button as fallback
                    if location_add_buttons:
                        try:
                            print(f"  Trying add button for on-site location")
                            location_add_buttons[0].click()
                            # Wait for dialog or input to appear
                            self.page.wait_for_selector('input[type="text"]', timeout=1000)
                            # Find the input in the dialog
                            dialog_input = self.page.locator('input[type="text"]').first
                            dialog_input.fill(location)
                            dialog_input.press("Enter")
                            locations_set += 1
                            print(f"  Added on-site location via add button")
                        except Exception as dialog_e:
                            print(f"  Error using add button: {dialog_e}")
            
            # Set remote locations
            if remote_inputs and len(locations) > 1:
                # Use remaining locations for remote
                location = locations[1]  # Use second location for remote
                try:
                    input_field = remote_inputs[0]
                    
                    print(f"  Setting remote location: {location}")
                    input_field.click()
                    input_field.fill("")
                    input_field.fill(location)
                    input_field.press("Enter")
                    
                    locations_set += 1
                    logger.info(f"Set remote location: {location}")
                except Exception as e:
                    print(f"  Error setting remote location: {e}")
                    
                    # Try using add button as fallback
                    print(f"  Searching thoroughly for add buttons for remote location")
                    
                    # Look for all possible ways to add a remote location
                    add_attempts = [
                        # Try using the add buttons we found earlier
                        (len(location_add_buttons) > 1, lambda: location_add_buttons[1].click()),
                        
                        # Try looking for buttons near the remote section
                        (True, lambda: self.page.locator('button:near(:text("Remote locations"))').first.click()),
                        
                        # Try clicking "+ Add" buttons
                        (True, lambda: self.page.locator('button:has-text("+ Add")').first.click()),
                        
                        # Try any "Add" button near "remote"
                        (True, lambda: self.page.locator('button:has-text("Add"):near(:text("remote"))').first.click()),
                        
                        # Last resort - try any add button
                        (True, lambda: self.page.locator('button:has-text("Add")').first.click())
                    ]
                    
                    for condition, click_action in add_attempts:
                        if not condition:
                            continue
                            
                        try:
                            print(f"  Trying another approach to add remote location...")
                            click_action()
                            
                            # Wait briefly for dialog
                            self.page.wait_for_selector('input[type="text"]', timeout=1000)
                            
                            # Find the input that appeared or was focused
                            newly_active_inputs = self.page.locator('input:focus, input[type="text"]:visible').all()
                            
                            for input_field in newly_active_inputs:
                                try:
                                    input_field.fill(location)
                                    input_field.press("Enter")
                                    print(f"  Successfully added remote location: {location}")
                                    locations_set += 1
                                    break
                                except Exception as input_e:
                                    print(f"  Error filling remote location input: {input_e}")
                            
                            # If we found and filled an input, break the loop
                            if locations_set > 0:
                                break
                                
                        except Exception as attempt_e:
                            print(f"  Error trying add approach: {attempt_e}")
                    
                    if locations_set == 0:
                        print(f"  All attempts to add remote location failed")
            
            result = f"Set {locations_set} locations. "
            print(f">>> COMPLETED SETTING LOCATIONS: {result}")
            return result
        except Exception as e:
            logger.error(f"Error setting locations: {str(e)}")
            print(f">>> ERROR SETTING LOCATIONS: {str(e)}")
            return "Failed to set locations. "


    def apply_preferences(self, preferences: Dict[str, Any]) -> str:
        """
        Alias for apply_job_preferences for backwards compatibility with test scripts.
        
        Args:
            preferences: Dictionary of job preferences to apply
            
        Returns:
            str: Result message indicating success or failure
        """
        return self.apply_job_preferences(preferences)


def main():
    """Main function to run the LinkedIn UI agent."""
    # Sample preferences
    test_preferences = {
        "job_titles": ["Software Engineer", "Data Scientist"],
        "modality": ["Remote", "Hybrid"],
        "locations": ["United States", "Canada"],
        "job_type": ["Full-time"],
    }

    linkedin_agent = None
    try:
        # Initialize LinkedIn agent
        logger.info("Initializing AgtSearchLdn...")
        linkedin_agent = AgtSearchLdn(headless=False)

        # Login to LinkedIn
        logger.info("Logging in to LinkedIn...")
        login_result = linkedin_agent.login()
        if not login_result:
            logger.error("Failed to login to LinkedIn")
            return

        # Navigate to job preferences
        logger.info("Navigating to job preferences...")
        preferences_result = linkedin_agent.navigate_to_job_preferences()
        if not preferences_result:
            logger.error("Failed to navigate to job preferences")
            return

        # Initialize UI agent and apply preferences
        logger.info("Initializing UI agent...")
        ui_agent = LinkedInUIAgent(linkedin_agent)

        # Apply preferences
        logger.info("Applying job preferences...")
        result = ui_agent.apply_job_preferences(test_preferences)
        logger.info(f"Result: {result}")

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        # Print stack trace for better debugging
        import traceback

        traceback.print_exc()
    finally:
        # Always close the browser
        if linkedin_agent:
            logger.info("Closing browser...")
            linkedin_agent.close()


if __name__ == "__main__":
    # Run the main function
    logger.info("Starting LinkedIn UI Agent...")
    main()
