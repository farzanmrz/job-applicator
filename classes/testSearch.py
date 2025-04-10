import base64
import importlib
import json
import logging
import os
import sys
import time

from langchain_ollama import OllamaLLM
from playwright.sync_api import sync_playwright

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import classes.AppCreds
import classes.FormRecog
import classes.PrefModel

importlib.reload(classes.AppCreds)
importlib.reload(classes.PrefModel)
importlib.reload(classes.FormRecog)

from classes.AppCreds import AppCreds
from classes.PrefModel import PrefModel, PendingAction

# Logging config
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S"
)
log = lambda msg: (
    print(end="\n"),
    logging.info(msg),
)


class LinkedInAgent:
    """LinkedIn search and job application agent"""

    def __init__(self, headless=False):
        log("AGENT: Initializing Agent and Browser ")
        self.pw = sync_playwright().start()
        self.br = self.pw.chromium.launch(headless=headless)
        self.cx = self.br.new_context()
        self.pg = self.cx.new_page()
        self.job_prefs_url = (
            "https://www.linkedin.com/jobs/opportunities/job-opportunities/onboarding/"
        )
        self.feed_url = "https://www.linkedin.com/feed/"
        self.flags = json.load(open("data/flags.json"))

    def login(self):
        """Log in to LinkedIn"""
        log("LOGIN: Attempting login")
        if not (creds := AppCreds().get_creds("linkedin")):
            log("LOGIN: Login failed (missing credentials)")
            return False

        self.pg.goto("https://www.linkedin.com/login")
        self.pg.fill("#username", creds["username"])
        self.pg.fill("#password", creds["password"])
        self.pg.click('button[type="submit"]')

        if self.feed_url in self.pg.url:
            log("LOGIN: Login successful")
            return True
        else:
            log("LOGIN: Verification required")
            input("LOGIN: Return Key Confirms")
            if self.feed_url in self.pg.url:
                log("LOGIN: Login successful after verification")
                return True
            else:
                log("LOGIN: Login failed")
                return False

    def navigate(self):
        if self.flags.get("ldn_update_job_preferences"):
            log("AGENT: Navigating to job preferences")
            self.pg.goto(self.job_prefs_url)
            time.sleep(3)
        return True

    def close(self):
        log("AGENT: Closing browser session")
        self.br and self.br.close()
        self.pw and self.pw.stop()

    def recog(self):
        # Take screenshot
        log("GEMMA: Analyzing form via screenshot")
        screenshot_path = os.path.join(
            os.makedirs(os.path.join(os.getcwd(), "screenshots"), exist_ok=True)
            or "screenshots",
            f"{time.strftime('%Y%m%d-%H%M%S')}_form.png",
        )
        self.pg.screenshot(path=screenshot_path)

        # Create prompt for image analysis with improved focus detection
        prompt = """
        Analyze this screenshot step by step:
        
        Step 1: Identify if there's a dialog box, modal, or focused form area in this screenshot.
        
        Step 2: If there is a dialog box or focused area:
        a) Describe what this focused area contains
        b) Analyze ONLY the form elements inside this focused area
        
        If there is NO dialog box or focused area:
        a) Identify ALL form elements visible on the page
        
        Step 3: For all form elements you analyze, describe:
        a) The type of form fields (checkboxes, radio buttons, text inputs, etc.)
        b) The categories or sections these form elements belong to
        c) The specific values, options, placeholders or states visible for each element
        
        Step 4: Organize your analysis in a structured format with clear headings and concise descriptions.
        """

        with open(screenshot_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

        # Use the Gemma3 model which has shown good results
        model = OllamaLLM(model="gemma3:4b")

        # Use the string prompt with the image
        response = model.invoke(prompt, images=[encoded_string])

        log(f"GEMMA: Derived analysis - {response}")
        return response
        
    def recog2(self):
        """
        Extract LinkedIn job preference form data using DOM element selection.
        Uses the SubAgtJobPref class to handle the extraction, cleanup, and matching.
        """
        log("DOM: Extracting job preferences via DOM traversal")
        job_pref_agent = SubAgtJobPref(self.pg)
        
        # Step 1: Scrape raw preferences from the DOM
        scraped_prefs = job_pref_agent.scrape_prefs()
        if not scraped_prefs:
            return None
            
        # Step 2: Clean up the preferences
        cleaned_prefs = job_pref_agent.clean_prefs()
        
        # Step 3: Match with canonical values
        matched_prefs = job_pref_agent.match_prefs()
        
        return matched_prefs  # Return the matched preferences


class SubAgtJobPref:
    """LinkedIn job preferences agent for handling form extraction and interaction"""
    
    def __init__(self, page):
        """Initialize with a Playwright page object"""
        self.page = page
        self.raw_preferences = {}
        self.cleaned_preferences = {}
        self.matched_preferences = {}
        self.form_container_id = 'ember54'
        self.form_element_class = 'fb-dash-form-element'
        self.save_button_id = 'ember80'
        
    def scrape_prefs(self):
        """Extract raw job preferences from the LinkedIn form DOM"""
        # Get the root form container
        form_container = self.page.query_selector(f'#{self.form_container_id}')
        if not form_container:
            log(f"DOM: Form container #{self.form_container_id} not found")
            return None
            
        # Find all form elements
        form_elements = form_container.query_selector_all(f'.{self.form_element_class}')
        if not form_elements:
            log(f"DOM: No form elements found with class '{self.form_element_class}'")
            return None
            
        self.raw_preferences = {}
        
        for element in form_elements:
            # Find the fieldset inside the form element
            fieldset = element.query_selector('fieldset')
            if not fieldset:
                continue
                
            # Find the legend containing the category name
            legend = fieldset.query_selector('legend')
            if not legend:
                continue
                
            # Extract the category name from the span element with specific classes
            category_span = legend.query_selector('span.fb-dash-form-element__label.fb-dash-form-element__label-title--is-required')
            if not category_span:
                # Try without the required class as some fields might be optional
                category_span = legend.query_selector('span.fb-dash-form-element__label')
                if not category_span:
                    continue
            
            # Extract the category name from the text content
            # Format is expected to be: <!---->"Category Name"<!---->
            text_content = category_span.inner_text()
            if not text_content:
                continue
                
            # Clean up the category name by removing HTML comments and quotes
            category_name = text_content.replace('<!---->', '').replace('"', '')
            category_name = category_name.strip()
            
            if not category_name:
                continue
                
            # Get all sibling elements after legend in the fieldset for options/values
            options = []
            
            # Use JavaScript to gather options
            js_function = """(fieldsetEl) => {
                const children = Array.from(fieldsetEl.children);
                const legendEl = fieldsetEl.querySelector('legend');
                if (!legendEl) return [];
                
                const legendIndex = children.indexOf(legendEl);
                if (legendIndex === -1) return [];
                
                // Get elements after the legend
                const optionElements = children.slice(legendIndex + 1);
                return optionElements.map(el => {
                    // Extract relevant information based on element type
                    if (el.tagName === 'SELECT') {
                        return Array.from(el.options).map(opt => opt.value).filter(v => v);
                    } else if (el.tagName === 'INPUT') {
                        return el.value || el.placeholder || el.checked?.toString() || '';
                    } else {
                        return el.textContent.trim();
                    }
                }).filter(text => text);
            }"""
            options_elements = self.page.evaluate(js_function, fieldset)
            
            if options_elements:
                options = options_elements
            
            # Store the category and its options
            self.raw_preferences[category_name] = options
            
        log(f"DOM: Scraped {len(self.raw_preferences)} raw preference categories")
        return self.raw_preferences
    
    def clean_prefs(self):
        """Clean up extracted preferences by removing UI elements and normalizing values"""
        self.cleaned_preferences = {}
        
        # Common action buttons to filter out (not actual values)
        action_button_texts = [
            "Add title", "Add location", "Add company", "Add job type", 
            "Add industry", "Add education", "Add skill", "Add", "Edit"
        ]
        
        for category, values in self.raw_preferences.items():
            # Clean up the category name
            clean_category = category.strip()
            
            # Special case for visibility section which has verbose text
            if "Visibility" in clean_category:
                clean_category = "Visibility"
            
            # Filter out action buttons and clean option values
            clean_values = []
            for value in values:
                # Skip if value is an action button
                if any(button in value for button in action_button_texts):
                    continue
                    
                # Clean up the value text
                clean_value = value.strip()
                
                # Handle special case for Visibility options with much more aggressive cleaning
                if clean_category == "Visibility":
                    if "Recruiters" in clean_value:
                        clean_value = "Recruiters"
                    elif "All LinkedIn members" in clean_value:
                        clean_value = "All Members"
                    else:
                        continue  # Skip any other values in Visibility
                
                if clean_value and clean_value not in clean_values:
                    clean_values.append(clean_value)
            
            if clean_values:
                if clean_category in self.cleaned_preferences:
                    # Append new values if category already exists
                    self.cleaned_preferences[clean_category].extend(clean_values)
                else:
                    self.cleaned_preferences[clean_category] = clean_values
        
        log(f"DOM: Cleaned up to {len(self.cleaned_preferences)} preference categories")
        return self.cleaned_preferences
    
    def match_prefs(self):
        """
        Match extracted preferences with canonical values from PrefModel.
        Creates pending actions for new or ambiguous matches.
        """
        pref_model = PrefModel()
        log("PREF: Matching extracted preferences with canonical values")
        self.matched_preferences = {}
        self.mapping_details = {"categories": {}, "values": {}}
        
        for category, values in self.cleaned_preferences.items():
            # Try to match the category
            canonical_category, category_score = pref_model.get_canonical_category(
                category, create_pending=True)
            
            # Record the mapping details
            self.mapping_details["categories"][category] = {
                "matched_to": canonical_category,
                "confidence": category_score
            }
            
            if not canonical_category:
                # Keep original if no match found
                canonical_category = category
                
            matched_values = []
            value_mappings = {}
            
            for value in values:
                if value:  # Skip empty values
                    # Try to match the value within this category
                    canonical_value, value_score = pref_model.get_canonical_value(
                        canonical_category, value, create_pending=True)
                    
                    # Record the value mapping details
                    value_key = f"{canonical_category}.{value}"
                    value_mappings[value_key] = {
                        "matched_to": canonical_value,
                        "confidence": value_score
                    }
                    
                    if canonical_value:
                        matched_values.append(canonical_value)
                    else:
                        matched_values.append(value)  # Keep original if no match
            
            # Add to matched preferences
            self.matched_preferences[canonical_category] = matched_values
            
            # Add value mappings to the details
            self.mapping_details["values"].update(value_mappings)
        
        # Log pending actions that were created
        pending_actions = pref_model.get_pending_actions()
        if pending_actions:
            log(f"PREF: Created {len(pending_actions)} pending actions for review")
            
            # Create a summary of the pending actions
            self.mapping_details["pending_actions"] = []
            for action in pending_actions:
                action_data = {
                    "id": action.id,
                    "type": action.action_type,
                    "old_category": action.old_category,
                    "new_category": action.new_category,
                    "old_value": action.old_value,
                    "new_value": action.new_value,
                    "confidence": action.score
                }
                self.mapping_details["pending_actions"].append(action_data)
        
        # Save mapping details to a JSON file
        mapping_file = os.path.join(os.path.dirname(__file__), f"pref_mapping_{time.strftime('%Y%m%d-%H%M%S')}.json")
        with open(mapping_file, "w") as f:
            json.dump(self.mapping_details, f, indent=2)
        log(f"PREF: Saved mapping details to {mapping_file}")
        
        log(f"PREF: Matched {len(self.matched_preferences)} categories with canonical values")
        return self.matched_preferences
    
    def update_preference(self, category, values):
        """Update a preference in the form (placeholder for future implementation)"""
        # Finds the category in the form and updates its values
        pass


def main():
    agent = LinkedInAgent(headless=False)
    agent.login()
    agent.navigate()
    
    # Extract and match preferences
    matched_prefs = agent.recog2()
    
    # Print the matched preferences
    if matched_prefs:
        print("\n=== MATCHED PREFERENCES ===")
        for category, values in matched_prefs.items():
            print(f"Category: {category}")
            for value in values:
                print(f"  {value}")
            print()
            
        # Print pending actions
        pref_model = PrefModel()
        pending_actions = pref_model.get_pending_actions()
        if pending_actions:
            print("\n=== PENDING ACTIONS ===")
            for action in pending_actions:
                action_type = action.action_type
                if action.is_category_action():
                    print(f"{action_type}: {action.old_category} -> {action.new_category}")
                else:
                    print(f"{action_type}: {action.old_category}.{action.old_value} -> {action.new_category}.{action.new_value}")
            print()
    
    agent.close()


if __name__ == "__main__":
    main()
