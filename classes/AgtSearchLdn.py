import importlib
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from playwright.sync_api import sync_playwright

# Add project root to sys.path (ensures classes/ is importable)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import and reload classes to ensure latest version
from classes import AppCreds

importlib.reload(AppCreds)

from classes.AppCreds import AppCreds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("linkedin_agent")

# Job preferences URL constant
JOB_PREFS_URL = "https://www.linkedin.com/jobs/opportunities/job-opportunities/onboarding/?jobOpportunitiesOrigin=SEEKER_NEXT_BEST_ACTION"


class AgtSearchLdn:
    """Agent responsible for LinkedIn job search operations."""

    def __init__(self, headless=False):
        """
        Initialize the LinkedIn search agent.

        Args:
            headless (bool): Whether to run the browser in headless mode
        """
        self.cred_manager = AppCreds()
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None
        self.logged_in = False
        self.browser_args = ["--disable-dev-shm-usage"] if self.headless else []

    def get_credentials(self):
        """Retrieve LinkedIn credentials from the credential manager."""
        creds = self.cred_manager.get_creds("linkedin")
        if not creds:
            logger.error(
                "LinkedIn credentials not found. Please set up your credentials first."
            )
            return None
        return creds

    def login(self, use_cookies=True):
        """
        Log into LinkedIn using stored credentials.

        Args:
            use_cookies (bool): Whether to attempt to use stored cookies for authentication

        Returns:
            bool or str: True if login successful, False if failed, "verification_needed" if manual verification required
        """
        if self.logged_in and self.page:
            logger.info("Already logged in to LinkedIn")
            return True

        creds = self.get_credentials()
        if not creds:
            return False

        # Launch browser outside the sync_playwright context to avoid context issues
        # when manual intervention is needed
        self.playwright = sync_playwright().start()

        # Create storage state dir if needed
        cookies_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "browser_state"
        )
        os.makedirs(cookies_dir, exist_ok=True)
        cookies_file = os.path.join(cookies_dir, "linkedin_cookies.json")

        try:
            # Launch browser
            logger.info("Launching browser...")
            self.browser = self.playwright.chromium.launch(
                headless=self.headless, args=self.browser_args
            )

            # Configure viewport for consistent behavior
            viewport_size = {"width": 1280, "height": 720}

            # Try to use saved cookies if available and requested
            context_options = {
                "viewport": viewport_size,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            }

            if use_cookies and os.path.exists(cookies_file):
                logger.info("Using saved cookies for authentication")
                context_options["storage_state"] = cookies_file

            context = self.browser.new_context(**context_options)
            self.page = context.new_page()

            # Navigate to LinkedIn login page
            logger.info("Navigating to LinkedIn login page...")
            try:
                self.page.goto("https://www.linkedin.com/login", timeout=30000)
            except Exception as e:
                logger.warning(f"Initial navigation timeout: {e}")
                self.page.goto("https://www.linkedin.com/", timeout=30000)

            # Check if we're already logged in (cookies worked)
            if "feed" in self.page.url:
                logger.info("Already logged in via cookies!")
                self.logged_in = True
                return True

            # Fill in credentials if login form is present
            if self.page.locator("#username").count() > 0:
                logger.info("Filling in credentials...")
                self.page.fill("#username", creds["username"])
                self.page.fill("#password", creds["password"])

                # Click login button
                logger.info("Clicking login button...")
                self.page.click('button[type="submit"]')

                # Wait for navigation with timeout
                logger.info("Waiting for navigation...")
                try:
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                except Exception as e:
                    logger.warning(f"Navigation timeout after login: {e}")
                    # Try to continue anyway
            else:
                logger.info(
                    "Login form not found - we might already be logged in or on a different page"
                )
                logger.info(f"Current URL: {self.page.url}")

            # Check if login was successful by looking for typical elements
            if self.page.url.startswith("https://www.linkedin.com/feed/"):
                logger.info("Login successful!")
                self.logged_in = True

                # Save cookies for future use if we successfully logged in without them
                if use_cookies and not os.path.exists(cookies_file):
                    logger.info("Saving cookies for future use")
                    try:
                        self.page.context.storage_state(path=cookies_file)
                    except Exception as e:
                        logger.error(f"Failed to save cookies: {e}")

                return True
            else:
                # Check for security verification or other barriers
                if "checkpoint" in self.page.url or "challenge" in self.page.url:
                    logger.warning(
                        "Security verification or challenge required. Manual intervention needed."
                    )
                    logger.warning(
                        "Please complete the verification in the browser window."
                    )

                    # Handle verification checkpoint
                    if not self.headless:
                        print(
                            "\n==========================================================="
                        )
                        print("ATTENTION: LinkedIn security verification required!")
                        print("Please complete the verification in the browser window.")
                        print("After completing verification, press Enter to continue.")
                        print(
                            "===========================================================\n"
                        )

                        try:
                            input("Press Enter after completing verification...")

                            # Check if we're logged in after manual intervention
                            if self.page.url.startswith(
                                "https://www.linkedin.com/feed/"
                            ):
                                logger.info("Verification completed successfully!")
                                self.logged_in = True
                                return True
                            else:
                                logger.warning(
                                    f"Still not logged in after verification. Current URL: {self.page.url}"
                                )
                                return "verification_needed"
                        except EOFError:
                            logger.error(
                                "Input operation failed, possibly running in a non-interactive environment"
                            )
                            return "verification_needed"
                    else:
                        # In headless mode, LinkedIn security verification is usually impossible
                        # Consider advanced strategies like using cookies or session restoration
                        logger.error(
                            "Security verification required but running in headless mode."
                        )
                        logger.error(
                            "LinkedIn security measures prevent fully automated login."
                        )
                        logger.error(
                            "Consider using cookie-based authentication or session restoration for headless operation."
                        )
                        return "verification_needed"
                else:
                    logger.error(f"Login failed. Current URL: {self.page.url}")
                    return False
        except Exception as e:
            logger.error(f"An error occurred during login: {str(e)}")
            return False

    def navigate_to_job_preferences(self):
        """
        Navigate to the LinkedIn job preferences page.
        This page shows personalized job opportunities and preferences.

        Returns:
            bool: True if navigation was successful, False otherwise
        """
        if not self.logged_in:
            login_result = self.login()
            if not login_result or login_result == "verification_needed":
                return False

        try:
            logger.info(f"Navigating to job preferences page: {JOB_PREFS_URL}")

            # Add some safety checks
            if not self.page or not self.browser:
                logger.error("Browser or page is not initialized")
                return False

            # Navigate directly to the job preferences page
            try:
                logger.info("Going to LinkedIn job preferences page...")
                self.page.goto(JOB_PREFS_URL, timeout=30000)
                
                # Wait for page to be fully loaded
                logger.info("Waiting for page to load (domcontentloaded)...")
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                
                # Also wait for network to be idle to ensure everything is loaded
                try:
                    logger.info("Waiting for network idle (up to 30 seconds)...")
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                except Exception as e:
                    logger.warning(f"Network idle timeout: {e} - continuing anyway")
                    
                # Give the page some time to render and JavaScript to initialize
                logger.info("Waiting 3 seconds for page to stabilize...")
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"Timeout during navigation to job preferences, but continuing: {e}")
                # Continue anyway, the page might still be usable

            # Check if we reached the right page
            current_url = self.page.url
            logger.info(f"Current URL after navigation: {current_url}")

            # More permissive URL checking
            if "/jobs/" in current_url:
                logger.info("Successfully navigated to a LinkedIn jobs page")
                return True
            else:
                logger.warning(
                    f"Navigation may have been redirected. Current URL: {current_url}"
                )
                # Take a screenshot to see where we ended up
                self.take_screenshot("navigation_result.png")
                return False

        except Exception as e:
            logger.error(
                f"An error occurred while navigating to job preferences: {str(e)}"
            )
            # Try to take a screenshot of where we ended up
            try:
                self.take_screenshot("navigation_error.png")
            except:
                pass
            return False

    def take_screenshot(self, filename="screenshot.png"):
        """
        Take a screenshot of the current page for debugging.

        Args:
            filename: Name of the screenshot file

        Returns:
            str: Path to the screenshot file or None if failed
        """
        try:
            # Create screenshots directory if it doesn't exist
            screenshots_dir = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)

            # Generate full path
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_path = os.path.join(screenshots_dir, f"{timestamp}_{filename}")

            # Take the screenshot
            self.page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return None

    def close(self):
        """Close the browser and PlayWright if they're open."""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None

            if hasattr(self, "playwright") and self.playwright:
                self.playwright.stop()

            self.page = None
            self.logged_in = False
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")


# Example usage
if __name__ == "__main__":
    from classes.PrefModel import PrefModel
    
    # For testing UI agent integration, import from linkedin_ui_agent
    try:
        from classes.linkedin_ui_agent import LinkedInUIAgent
        logger.info("Successfully imported LinkedInUIAgent from linkedin_ui_agent")
    except ImportError as e:
        logger.error(f"Failed to import LinkedInUIAgent: {str(e)}")
        # Fallback to direct UI manipulation

    agent = AgtSearchLdn(headless=False)

    try:
        # Login test
        login_result = agent.login()
        print(f"Login result: {login_result}")

        if login_result is True:
            # Navigate to job preferences
            nav_result = agent.navigate_to_job_preferences()
            print(f"Navigation result: {nav_result}")

            if nav_result:
                try:
                    # Create UI agent and apply preferences
                    ui_agent = LinkedInUIAgent(agent)
                    
                    # Apply a simple preference
                    import asyncio
                    result = asyncio.run(ui_agent.apply_job_preferences(
                        {"job_type": ["Full-time"], "modality": ["Remote"]}
                    ))
                    
                    print(f"Applied preferences result:\n{result}")
                except Exception as e:
                    print(f"Error using UI agent: {str(e)}")
    finally:
        # Make sure we close the browser
        agent.close()