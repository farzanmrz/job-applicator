import os
import sys
from playwright.sync_api import sync_playwright
import time
import logging

# Add project root to path to import CredentialManager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from frontend.classes.CredentialManager import CredentialManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('linkedin_agent')

class SearchLinkedinAgt:
    """Agent responsible for LinkedIn job search operations."""
    
    def __init__(self, headless=False):
        """
        Initialize the LinkedIn search agent.
        
        Args:
            headless (bool): Whether to run the browser in headless mode
        """
        self.cred_manager = CredentialManager()
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None
        self.logged_in = False
    
    def get_credentials(self):
        """Retrieve LinkedIn credentials from the credential manager."""
        creds = self.cred_manager.get_platform_credential_set("linkedin")
        if not creds:
            logger.error("LinkedIn credentials not found. Please set up your credentials first.")
            return None
        return creds
    
    def login(self):
        """Log into LinkedIn using stored credentials."""
        if self.logged_in and self.page:
            logger.info("Already logged in to LinkedIn")
            return True
            
        creds = self.get_credentials()
        if not creds:
            return False
        
        # Launch browser outside the sync_playwright context to avoid context issues
        # when manual intervention is needed
        self.playwright = sync_playwright().start()
        
        try:
            # Launch browser
            logger.info("Launching browser...")
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.page = self.browser.new_page()
            
            # Navigate to LinkedIn login page
            logger.info("Navigating to LinkedIn login page...")
            self.page.goto('https://www.linkedin.com/login')
            
            # Fill in credentials
            logger.info("Filling in credentials...")
            self.page.fill('#username', creds['username'])
            self.page.fill('#password', creds['password'])
            
            # Click login button
            logger.info("Clicking login button...")
            self.page.click('button[type="submit"]')
            
            # Wait for navigation
            logger.info("Waiting for navigation...")
            self.page.wait_for_load_state('networkidle')
            
            # Check if login was successful by looking for typical elements
            if self.page.url.startswith('https://www.linkedin.com/feed/'):
                logger.info("Login successful!")
                self.logged_in = True
                return True
            else:
                # Check for security verification or other barriers
                if "checkpoint" in self.page.url or "challenge" in self.page.url:
                    logger.warning("Security verification or challenge required. Manual intervention needed.")
                    logger.warning("Please complete the verification in the browser window.")
                    
                    # Only prompt for input if we're not in headless mode
                    if not self.headless:
                        print("\n===========================================================")
                        print("ATTENTION: LinkedIn security verification required!")
                        print("Please complete the verification in the browser window.")
                        print("After completing verification, press Enter to continue.")
                        print("===========================================================\n")
                        
                        try:
                            input("Press Enter after completing verification...")
                            
                            # Check if we're logged in after manual intervention
                            if self.page.url.startswith('https://www.linkedin.com/feed/'):
                                logger.info("Verification completed successfully!")
                                self.logged_in = True
                                return True
                            else:
                                logger.warning(f"Still not logged in after verification. Current URL: {self.page.url}")
                                return "verification_needed"
                        except EOFError:
                            logger.error("Input operation failed, possibly running in a non-interactive environment")
                            return "verification_needed"
                    else:
                        return "verification_needed"
                else:
                    logger.error(f"Login failed. Current URL: {self.page.url}")
                    return False
        except Exception as e:
            logger.error(f"An error occurred during login: {str(e)}")
            return False
    
    def search_jobs(self, keywords, location=None, filters=None):
        """
        Search for jobs on LinkedIn with given keywords and filters.
        
        Args:
            keywords (str): Job search keywords
            location (str, optional): Job location
            filters (dict, optional): Additional search filters
            
        Returns:
            list: List of job postings found
        """
        # Ensure we're logged in first
        if not self.logged_in:
            login_result = self.login()
            if not login_result or login_result == "verification_needed":
                return []
        
        try:
            logger.info(f"Searching for jobs with keywords: {keywords}")
            
            # Navigate to LinkedIn Jobs page
            self.page.goto('https://www.linkedin.com/jobs/')
            self.page.wait_for_load_state('networkidle')
            
            # Fill in the search fields
            self.page.fill("input[aria-label='Search by title, skill, or company']", keywords)
            
            if location:
                # Clear the location field first
                self.page.click("input[aria-label='City, state, or zip code']")
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Delete")
                self.page.fill("input[aria-label='City, state, or zip code']", location)
            
            # Click search button
            self.page.click("button[data-tracking-control-name='public_jobs_jobs-search-bar_base-search-button']")
            self.page.wait_for_load_state('networkidle')
            
            # TODO: Apply additional filters if provided
            
            # Extract job listings
            job_cards = self.page.query_selector_all(".job-search-card")
            jobs = []
            
            for card in job_cards:
                try:
                    title_elem = card.query_selector(".job-search-card__title")
                    company_elem = card.query_selector(".job-search-card__company-name")
                    location_elem = card.query_selector(".job-search-card__location")
                    link_elem = card.query_selector("a.job-search-card__title")
                    
                    job = {
                        "title": title_elem.inner_text() if title_elem else "Unknown Title",
                        "company": company_elem.inner_text() if company_elem else "Unknown Company",
                        "location": location_elem.inner_text() if location_elem else "Unknown Location",
                        "url": link_elem.get_attribute("href") if link_elem else None,
                    }
                    
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Error extracting job data: {str(e)}")
            
            logger.info(f"Found {len(jobs)} job listings")
            return jobs
            
        except Exception as e:
            logger.error(f"An error occurred during job search: {str(e)}")
            return []
    
    def close(self):
        """Close the browser and PlayWright if they're open."""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
                
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
                
            self.page = None
            self.logged_in = False
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")

# Example usage
if __name__ == "__main__":
    agent = SearchLinkedinAgt(headless=False)
    
    try:
        # Login test
        login_result = agent.login()
        print(f"Login result: {login_result}")
        
        if login_result is True:
            # Search jobs test
            jobs = agent.search_jobs("python developer", "San Francisco, CA")
            for i, job in enumerate(jobs[:5]):  # Print first 5 jobs
                print(f"Job {i+1}:")
                print(f"  Title: {job['title']}")
                print(f"  Company: {job['company']}")
                print(f"  Location: {job['location']}")
                print(f"  URL: {job['url']}")
                print()
    finally:
        # Make sure we close the browser
        agent.close()