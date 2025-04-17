#!/usr/bin/env python3
"""
LinkedIn Authentication Tool

This tool handles authentication to LinkedIn using stored credentials.
It provides functionality for both headless and visible browser sessions.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from utils.credmanager import CredentialManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("LinkedInAuth")

class LinkedInAuthenticator:
    """
    Handles authentication to LinkedIn using Playwright.
    
    Attributes:
        headless: Whether to run the browser in headless mode.
        storage_state_path: Path to store browser session state.
        browser: The Playwright browser instance.
        context: The browser context with the session.
        page: The main page with the authenticated session.
    """
    
    # LinkedIn URLs
    BASE_URL = "https://www.linkedin.com"
    LOGIN_URL = "https://www.linkedin.com/login"
    FEED_URL = "https://www.linkedin.com/feed/"
    
    def __init__(self, headless: bool = False):
        """Initialize the LinkedIn authenticator.
        
        Args:
            headless: Whether to run in headless mode (default: False)
        """
        self.headless = headless
        
        # Set storage state directory and path
        project_root = Path(__file__).parent.parent.parent
        storage_dir = project_root / "data" / "browser_state" / "linkedin"
        os.makedirs(storage_dir, exist_ok=True)
        
        self.storage_state_path = str(storage_dir / "storage_state.json")
        
        # Initialize other attributes
        self.browser = None
        self.context = None
        self.page = None
        self.credential_manager = CredentialManager()
    
    def login(self, platform: str = "linkedin") -> bool:
        """Log into LinkedIn using stored credentials.
        
        Args:
            platform: The credential platform name to use
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            with sync_playwright() as p:
                # Launch browser with appropriate settings to avoid detection
                self.browser = p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    ]
                )
                
                # Try to use stored session state if available
                if os.path.exists(self.storage_state_path):
                    logger.info("Using stored session state")
                    self.context = self.browser.new_context(storage_state=self.storage_state_path)
                    self.page = self.context.new_page()
                    self.page.goto(self.FEED_URL)
                    
                    # Check if we're still logged in
                    if self._is_logged_in():
                        logger.info("Successfully restored LinkedIn session")
                        return True
                    else:
                        logger.info("Stored session expired, logging in again")
                
                # Create new browser context if no stored session or session expired
                if not self.context:
                    self.context = self.browser.new_context()
                    self.page = self.context.new_page()
                    
                # Get credentials
                credentials = self.credential_manager.get_credentials(platform)
                if not credentials:
                    logger.error(f"No credentials found for {platform}")
                    return False
                
                # Go to login page
                self.page.goto(self.LOGIN_URL)
                
                # Fill in credentials
                self.page.fill("#username", credentials["username"])
                self.page.fill("#password", credentials["password"])
                
                # Click sign-in button
                self.page.click('button[type="submit"]')
                
                # Wait for navigation
                self.page.wait_for_load_state("networkidle")
                
                # Check for successful login
                if self._is_logged_in():
                    logger.info("Successfully logged into LinkedIn")
                    
                    # Save session state for future use
                    self.context.storage_state(path=self.storage_state_path)
                    logger.info(f"Saved session state to {self.storage_state_path}")
                    
                    return True
                else:
                    logger.error("Failed to log into LinkedIn")
                    return False
                
        except Exception as e:
            logger.error(f"Error during LinkedIn login: {e}")
            return False
        finally:
            self.close()
            
    def _is_logged_in(self) -> bool:
        """Check if currently logged into LinkedIn.
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            # Wait a bit for page to fully load
            self.page.wait_for_load_state("networkidle")
            
            # Check for elements only present when logged in
            # Gives more time for the page to load completely
            nav_present = self.page.is_visible('nav[aria-label="Primary navigation"]', timeout=3000)
            feed_present = self.page.is_visible('div[data-test-id="feed-container"]', timeout=3000)
            profile_present = self.page.is_visible('div[data-test-id="nav-settings"]', timeout=3000)
            
            # Also check for login form - it should NOT be present
            login_form = self.page.is_visible('form.login__form', timeout=1000)
            
            return (nav_present or feed_present or profile_present) and not login_form
        
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
            
    def close(self):
        """Close browser and clean up resources."""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
        except Exception as e:
            logger.error(f"Error closing browser: {e}")


def test_linkedin_auth(headless: bool = False) -> bool:
    """Test the LinkedIn authentication.
    
    Args:
        headless: Whether to run in headless mode
        
    Returns:
        bool: True if authentication successful
    """
    logger.info(f"Testing LinkedIn authentication (headless={headless})")
    authenticator = LinkedInAuthenticator(headless=headless)
    result = authenticator.login()
    
    if result:
        logger.info("LinkedIn authentication successful!")
    else:
        logger.error("LinkedIn authentication failed.")
        
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test LinkedIn authentication")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()
    
    success = test_linkedin_auth(headless=args.headless)
    sys.exit(0 if success else 1)