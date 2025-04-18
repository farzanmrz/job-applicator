import base64
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import openai
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from utils.commonutil import set_logger
from utils.credmanager import CredentialManager

# Get logger
logger = set_logger("TlAuthLkdn")


class TlAuthLkdn:

    # LinkedIn URLs (Consider moving to a config or constants file later)
    BASE_URL = "https://www.linkedin.com"
    LOGIN_URL = "https://www.linkedin.com/login"
    CAPTCHA_URL = "https://www.linkedin.com/checkpoint/challenge/"
    ERROR_URL = "https://www.linkedin.com/checkpoint/lg/login-submit"
    FEED_URL = "https://www.linkedin.com/feed/"

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.cred_mgr = CredentialManager()
        self.state_pth = "data/browser/state_lkdn.json"
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pg: Optional[Page] = None

    def verify_captcha(self) -> bool:
        """Use GPT-4o vision to locate and click the verify button on the CAPTCHA page."""
        try:
            # Load OpenAI API key
            load_dotenv()
            api_key = os.environ.get("KEY_OPENAI")
            if not api_key:
                logger.error("OpenAI API key not found")
                return False

            # Initialize OpenAI client
            client = openai.OpenAI(api_key=api_key)

            # Wait 5 seconds for page to fully load
            logger.info("Waiting 5 seconds for CAPTCHA page to load...")
            self.pg.wait_for_timeout(5000)

            # Take screenshot of the page
            screenshot_path = "temp/captcha_page.png"
            self.pg.screenshot(path=screenshot_path)
            logger.info("Captured CAPTCHA page screenshot")

            # Read and encode screenshot
            with open(screenshot_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")

            # Prepare prompt for GPT-4o
            prompt = """You are an expert at analyzing web page screenshots for automation.
            Given the attached screenshot, identify the main "Verify" button that a user must click to pass a CAPTCHA or verification step.
            
            Respond ONLY with a single-line JSON object with these keys:
            1. "selectors": array — List of possible CSS selectors for the "Verify" button, ordered by likelihood. Include variations like:
               - Button with exact text: 'button:has-text("Verify")'
               - Common class names: '.verify-button', '.verification-button', '.submit-button'
               - Common button patterns: 'form button[type="submit"]', 'button.primary'
            2. "coordinates": [x, y] — The pixel coordinates of the center of the "Verify" button.
            3. "confidence": float — Your confidence (0.0 to 1.0) that you have correctly identified the button.
            
            Example response:
            {"selectors": ["button:has-text(\\"Verify\\")", ".verify-button", "form button[type=\\"submit\\"]"], "coordinates": [320, 240], "confidence": 0.95}
            
            If you cannot find the button, respond with:
            {"selectors": [], "coordinates": [0, 0], "confidence": 0.0}
            
            IMPORTANT: Use double quotes for all JSON keys and values. Do not include any explanation or extra text."""

            # Call GPT-4o with vision
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=150,
            )

            def clean_json_response(text: str) -> str:
                """Clean and fix common JSON formatting issues in LLM responses."""
                # Remove markdown code block markers if present
                text = text.replace("```json", "").replace("```", "").strip()

                # Add missing commas between properties
                text = text.replace('" "', '", "')
                text = text.replace('] "', '], "')

                return text

            # Get raw response and log it
            raw_response = response.choices[0].message.content
            logger.info(f"Raw GPT-4o response: {raw_response}")

            # Clean and parse JSON response
            try:
                cleaned_response = clean_json_response(raw_response)
                logger.info(f"Cleaned response: {cleaned_response}")

                result = json.loads(cleaned_response)
                logger.info(f"Parsed GPT-4o result: {result}")

                # Validate expected keys are present
                required_keys = ["selectors", "coordinates", "confidence"]
                if not all(key in result for key in required_keys):
                    logger.error("Missing required keys in GPT-4o response")
                    return False

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT-4o response as JSON: {str(e)}")
                logger.error(f"Raw response was: {raw_response}")
                return False

            # Try to click the button
            if result["confidence"] > 0.7:  # Only proceed if confidence is high enough
                # First try all provided selectors
                if result["selectors"]:
                    for selector in result["selectors"]:
                        try:
                            logger.info(
                                f"Attempting to click button using selector: {selector}"
                            )
                            # Set a shorter timeout for each selector attempt
                            self.pg.click(selector, timeout=5000)
                            logger.info("Successfully clicked button!")
                            # Wait a moment after clicking
                            self.pg.wait_for_timeout(2000)
                            return True
                        except Exception as e:
                            logger.warning(
                                f"Failed to click using selector '{selector}': {str(e)}"
                            )

                # If all selectors fail, try coordinates
                if result["coordinates"] != [0, 0]:
                    x, y = result["coordinates"]
                    try:
                        logger.info(f"Attempting to click at coordinates: ({x}, {y})")
                        self.pg.mouse.click(x, y)
                        logger.info("Successfully clicked coordinates!")
                        # Wait a moment after clicking
                        self.pg.wait_for_timeout(2000)
                        return True
                    except Exception as e:
                        logger.error(f"Failed to click coordinates: {str(e)}")

                logger.error("All click attempts failed")
                return False
            else:
                logger.error("Low confidence in button detection")
                return False

        except Exception as e:
            logger.error(f"Error in verify_captcha: {str(e)}")
            return False
        finally:
            # Clean up screenshot
            try:
                Path(screenshot_path).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to delete screenshot: {str(e)}")

    def val_login(self) -> bool:
        """Validate LinkedIn login state based on URL."""
        if self.pg.url.startswith(self.CAPTCHA_URL):
            logger.warning("Verification captcha encountered.")
            return self.verify_captcha()

        if self.pg.url == self.FEED_URL:
            logger.info("Login Successful")
            return True

        if self.pg.url == self.ERROR_URL:
            logger.critical("Login failed: incorrect login credentials.")
            return False

        return False

    def login(self) -> bool:
        """Authenticate with LinkedIn using Playwright"""
        logger.info(f"Logging in LinkedIn with headless = {self.headless}")

        # Fetch credentials
        creds = self.cred_mgr.get_credentials("linkedin")
        if not creds:
            logger.error("LinkedIn credentials not found")
            return False

        # Initialize Playwright
        with sync_playwright() as playwright:
            self.browser = playwright.chromium.launch(headless=self.headless)

            # Create fresh context
            self.context = self.browser.new_context()
            self.pg = self.context.new_page()

            # Navigate to login page and input credentials
            self.pg.goto(self.LOGIN_URL)

            # Fill in credentials
            self.pg.fill("#username", creds["username"])
            self.pg.fill("#password", creds["password"])
            self.pg.click("button[type='submit']")

            # Wait for 2 seconds after submit
            self.pg.wait_for_timeout(2000)

            # Call the validation method
            login_successful = self.val_login()

            if not login_successful:
                logger.info("Closing browser")
                self.pg.close()
                self.context.close()
                self.browser.close()

            return login_successful


if __name__ == "__main__":
    auth = TlAuthLkdn(headless=False)
    auth.login()
