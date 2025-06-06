import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from playwright.sync_api import Browser, BrowserContext, Page

from utils.commonutil import set_logger
from utils.credmanager import CredentialManager

logger = set_logger("TlAuthLkdn")


class TlAuthLkdn:
    # LinkedIn URLs
    BASE_URL = "https://www.linkedin.com"
    LOGIN_URL = "https://www.linkedin.com/login"
    CAPTCHA_URL = "https://www.linkedin.com/checkpoint/challenge/"
    ERROR_URL = "https://www.linkedin.com/checkpoint/lg/login-submit"
    FEED_URL = "https://www.linkedin.com/feed/"

    def __init__(self, state_path: str = "data/browser_lkdn.json"):
        self.state_path = state_path
        self.cred_mgr = CredentialManager()

    def is_logged_in(self, page: Page) -> bool:
        """Check if the given page is on the LinkedIn feed (i.e., logged in)."""
        try:
            return page.url.startswith(self.FEED_URL)
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    def login_flow(self, context: BrowserContext) -> Page | None:
        """Perform the login steps. Returns the page if successful, else None."""
        try:
            creds = self.cred_mgr.get_credentials("linkedin")
            if not creds:
                logger.critical("No LinkedIn credentials found.")
                return None

            page = context.new_page()
            page.goto(self.LOGIN_URL)
            page.locator("#username").fill(creds["username"])
            page.locator("#password").fill(creds["password"])
            page.locator("button[type='submit']").click()
            page.wait_for_load_state("domcontentloaded")

            # Handle different post-login scenarios
            if page.url.startswith(self.FEED_URL):
                logger.info("Login successful.")
                return page
            elif page.url.startswith(self.CAPTCHA_URL):
                logger.warning("Verification captcha encountered.")
                # Wait for manual captcha solving
                page.wait_for_timeout(20000)
                if page.url.startswith(self.FEED_URL):
                    return page
            elif page.url == self.ERROR_URL:
                logger.error("Login failed - Landed on Error URL.")
            else:
                logger.warning(f"Landed on unexpected URL: {page.url}")

            page.close()
            return None
        except Exception as e:
            logger.error(f"Error in login flow: {e}")
            return None

    def create_and_save_context(self, browser: Browser) -> BrowserContext | None:
        """Create a new context, perform login, and save state if successful."""
        try:
            context = browser.new_context(base_url=self.BASE_URL, no_viewport=True)
            page = self.login_flow(context)
            if page:
                context.storage_state(path=self.state_path)
                page.close()
                return context
            if context:
                context.close()
            return None
        except Exception as e:
            logger.error(f"Error creating context: {e}")
            return None

    def get_valid_context(self, browser: Browser) -> BrowserContext | None:
        """Try to load context from file, validate, or create new if needed."""
        if not os.path.exists(self.state_path):
            logger.critical(f"State file {self.state_path} not found.")
            return None

        try:
            # Try loading from saved state
            context = browser.new_context(
                base_url=self.BASE_URL, no_viewport=True, storage_state=self.state_path
            )

            # Verify loaded context
            page = context.new_page()
            page.goto(self.FEED_URL)
            page.wait_for_load_state("domcontentloaded")

            if self.is_logged_in(page):
                logger.info("Successfully loaded context from saved state.")
                page.close()
                return context

            logger.warning("Loaded context is not valid (not logged in).")
            page.close()
            context.close()

            # Try creating new context
            logger.info("Creating new context with login...")
            context = self.create_and_save_context(browser)
            if not context:
                logger.critical("Failed to create new context.")
                return None

            # Verify new context
            page = context.new_page()
            page.goto(self.FEED_URL)
            page.wait_for_load_state("domcontentloaded")

            if self.is_logged_in(page):
                logger.info("Created and verified new context.")
                page.close()
                return context

            logger.critical("New context creation succeeded but verification failed.")
            page.close()
            context.close()
            return None

        except Exception as e:
            logger.error(f"Error in get_valid_context: {e}")
            return None
