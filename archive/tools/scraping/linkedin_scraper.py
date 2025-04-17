#!/usr/bin/env python3
"""
LinkedIn Job Scraper Tool - Extract job listings from LinkedIn using Playwright
"""

import os
import time
import json
import logging
import random
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import credential manager
from utils.common import get_platform_credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("linkedin_scraper.log")
    ]
)

logger = logging.getLogger("LinkedInScraper")


class JobSearchParams(BaseModel):
    """
    Parameters for LinkedIn job search
    """
    
    keywords: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None  # FULL_TIME, PART_TIME, CONTRACT, etc.
    experience_level: Optional[str] = None  # ENTRY_LEVEL, MID_SENIOR, DIRECTOR, etc.
    remote_filter: Optional[str] = None  # ON_SITE, REMOTE, HYBRID
    date_posted: Optional[str] = None  # PAST_MONTH, PAST_WEEK, PAST_24_HOURS, etc.
    salary: Optional[str] = None
    industry: Optional[str] = None
    max_results: int = 25
    
    def to_url_params(self) -> Dict[str, str]:
        """
        Convert parameters to URL query parameters
        """
        params = {}
        
        if self.keywords:
            params["keywords"] = self.keywords
        
        if self.location:
            params["location"] = self.location
        
        # Add other parameters based on LinkedIn's URL structure
        # This is a simplified version and may need to be updated
        # based on LinkedIn's current URL format
        
        return params


class JobDetails(BaseModel):
    """
    Structure for extracted job details
    """
    
    job_id: str
    title: str
    company: str
    location: str
    url: str
    description: Optional[str] = None
    date_posted: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    job_function: Optional[str] = None
    industries: List[str] = Field(default_factory=list)
    applicant_count: Optional[int] = None
    salary_range: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)
    remote_type: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LinkedInScraper:
    """
    Tool for extracting job listings from LinkedIn using Playwright
    """
    
    def __init__(
        self, 
        headless: bool = True, 
        slow_mo: int = 100,
        timeout: int = 30000,
        browser_state_dir: Optional[str] = None
    ):
        """
        Initialize the LinkedIn Scraper
        
        Args:
            headless: Whether to run the browser in headless mode
            slow_mo: Slow down operations by this amount of milliseconds
            timeout: Timeout for operations in milliseconds
            browser_state_dir: Directory to store browser state
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.timeout = timeout
        self.credentials = self._load_credentials()
        self.browser_state_dir = browser_state_dir or os.path.join(
            Path(__file__).parent.parent.parent, "data", "browser_state")
        
        # Ensure browser state directory exists
        os.makedirs(self.browser_state_dir, exist_ok=True)
        
        # Initialize browser
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        logger.info("LinkedIn Scraper initialized")
    
    def _load_credentials(self) -> Dict[str, str]:
        """
        Load LinkedIn credentials using CredentialManager
        
        Returns:
            Dict with username and password or empty dict if not found
        """
        # Get credentials from credential manager
        credentials = get_platform_credentials("linkedin")
        
        if credentials:
            logger.info("Loaded LinkedIn credentials from credential manager")
            return credentials
        
        # Try loading from environment variables as fallback
        load_dotenv()  # Load .env file if exists
        
        if "LINKEDIN_USERNAME" in os.environ and "LINKEDIN_PASSWORD" in os.environ:
            credentials = {
                "username": os.environ["LINKEDIN_USERNAME"],
                "password": os.environ["LINKEDIN_PASSWORD"]
            }
            logger.info("Loaded LinkedIn credentials from environment variables")
            return credentials
        
        # Return empty credentials if not found
        logger.warning("LinkedIn credentials not found")
        return {"username": "", "password": ""}
    
    def start(self) -> bool:
        """
        Start the browser and initialize session
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.playwright = sync_playwright().start()
            
            # Launch browser with state directory for persistent login
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
            
            user_data_dir = os.path.join(self.browser_state_dir, "linkedin")
            self.context = self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                storage_state=os.path.join(user_data_dir, "storage_state.json") if os.path.exists(os.path.join(user_data_dir, "storage_state.json")) else None
            )
            
            # Set default timeout
            self.context.set_default_timeout(self.timeout)
            
            # Create a new page
            self.page = self.context.new_page()
            
            logger.info("Browser started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            self.stop()
            return False
    
    def stop(self) -> None:
        """
        Close browser and clean up resources
        """
        try:
            if self.context:
                # Save storage state for persistence
                user_data_dir = os.path.join(self.browser_state_dir, "linkedin")
                os.makedirs(user_data_dir, exist_ok=True)
                self.context.storage_state(path=os.path.join(user_data_dir, "storage_state.json"))
                self.context.close()
                self.context = None
            
            if self.browser:
                self.browser.close()
                self.browser = None
            
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            
            logger.info("Browser stopped and resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
    
    def login(self) -> bool:
        """
        Log in to LinkedIn
        
        Returns:
            bool: True if login successful, False otherwise
        """
        if not self.page:
            logger.error("Browser not started, cannot login")
            return False
        
        if not self.credentials.get("username") or not self.credentials.get("password"):
            logger.error("LinkedIn credentials not available, cannot login")
            return False
        
        try:
            # Navigate to login page
            self.page.goto("https://www.linkedin.com/login")
            
            # Check if we're already logged in by looking for specific elements
            if self.page.url.startswith("https://www.linkedin.com/feed"):
                logger.info("Already logged in to LinkedIn")
                return True
            
            # Fill in username and password
            self.page.fill("#username", self.credentials["username"])
            self.page.fill("#password", self.credentials["password"])
            
            # Click the login button
            self.page.click("button[type='submit']")
            
            # Wait for navigation
            self.page.wait_for_load_state("networkidle")
            
            # Check if login successful
            if "feed" in self.page.url or "checkpoint" in self.page.url:
                logger.info("Successfully logged in to LinkedIn")
                
                # Save storage state for persistence
                user_data_dir = os.path.join(self.browser_state_dir, "linkedin")
                os.makedirs(user_data_dir, exist_ok=True)
                self.context.storage_state(path=os.path.join(user_data_dir, "storage_state.json"))
                
                return True
            else:
                logger.error(f"Login failed, current URL: {self.page.url}")
                return False
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def search_jobs(
        self, 
        search_params: JobSearchParams
    ) -> List[JobDetails]:
        """
        Search for jobs on LinkedIn using the provided parameters
        
        Args:
            search_params: Search parameters
            
        Returns:
            List of job details
        """
        if not self.page:
            logger.error("Browser not started, cannot search jobs")
            return []
        
        try:
            # Construct search URL
            base_url = "https://www.linkedin.com/jobs/search/?"
            params = search_params.to_url_params()
            params_str = "&".join([f"{k}={v}" for k, v in params.items()])
            search_url = base_url + params_str
            
            logger.info(f"Searching jobs with URL: {search_url}")
            
            # Navigate to search URL
            self.page.goto(search_url)
            
            # Wait for job results to load
            self.page.wait_for_selector(".jobs-search__results-list", timeout=20000)
            
            # Extract job listings
            job_listings = []
            max_results = search_params.max_results
            
            # Function to extract currently loaded jobs
            def extract_jobs():
                # Get all job cards
                job_cards = self.page.query_selector_all(".jobs-search__results-list > li")
                
                for job_card in job_cards:
                    try:
                        # Extract basic job info
                        title_elem = job_card.query_selector("h3.base-search-card__title")
                        company_elem = job_card.query_selector("h4.base-search-card__subtitle")
                        location_elem = job_card.query_selector("span.job-search-card__location")
                        
                        if not title_elem or not company_elem:
                            continue
                        
                        title = title_elem.inner_text().strip()
                        company = company_elem.inner_text().strip()
                        location = location_elem.inner_text().strip() if location_elem else "Unknown"
                        
                        # Get job URL and ID
                        url_elem = job_card.query_selector("a.base-card__full-link")
                        if url_elem:
                            url = url_elem.get_attribute("href")
                            # Extract job ID from URL
                            job_id = url.split("?")[0].split("-")[-1]
                        else:
                            continue  # Skip if no URL
                        
                        # Check if job already in listings
                        if any(job.job_id == job_id for job in job_listings):
                            continue
                        
                        # Create job details
                        job_details = JobDetails(
                            job_id=job_id,
                            title=title,
                            company=company,
                            location=location,
                            url=url
                        )
                        
                        job_listings.append(job_details)
                        
                        # Check if we've reached max results
                        if len(job_listings) >= max_results:
                            return True  # Stop extraction
                    
                    except Exception as e:
                        logger.error(f"Error extracting job details: {e}")
                
                return False  # Continue extraction
            
            # Extract first batch of jobs
            stop_extraction = extract_jobs()
            
            # Scroll to load more jobs if needed
            scroll_attempts = 0
            max_scroll_attempts = 10
            
            while not stop_extraction and len(job_listings) < max_results and scroll_attempts < max_scroll_attempts:
                # Scroll to bottom of results
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                # Wait for potential new results to load
                time.sleep(2)
                
                # Try to extract jobs again
                stop_extraction = extract_jobs()
                scroll_attempts += 1
            
            logger.info(f"Extracted {len(job_listings)} job listings")
            
            # Enrich job details if requested
            # (The full implementation would include visiting each job page)
            
            return job_listings[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return []
    
    def get_job_details(self, job_id: str) -> Optional[JobDetails]:
        """
        Get detailed information for a specific job
        
        Args:
            job_id: LinkedIn job ID
            
        Returns:
            JobDetails or None if not found
        """
        if not self.page:
            logger.error("Browser not started, cannot get job details")
            return None
        
        try:
            # Construct job URL
            job_url = f"https://www.linkedin.com/jobs/view/{job_id}"
            
            logger.info(f"Getting details for job {job_id}")
            
            # Navigate to job page
            self.page.goto(job_url)
            
            # Wait for job details to load
            self.page.wait_for_selector(".jobs-details", timeout=20000)
            
            # Extract job details
            title_elem = self.page.query_selector("h1.jobs-unified-top-card__job-title")
            company_elem = self.page.query_selector("a.jobs-unified-top-card__company-name")
            location_elem = self.page.query_selector("span.jobs-unified-top-card__bullet")
            
            if not title_elem or not company_elem:
                logger.error(f"Could not find basic job details for {job_id}")
                return None
            
            title = title_elem.inner_text().strip()
            company = company_elem.inner_text().strip()
            location = location_elem.inner_text().strip() if location_elem else "Unknown"
            
            # Extract job description
            description_elem = self.page.query_selector(".jobs-description-content__text")
            description = description_elem.inner_text().strip() if description_elem else None
            
            # Extract other job details
            job_info = {}
            
            # Try to extract employment type, experience level, etc.
            criteria_list = self.page.query_selector_all(".jobs-unified-top-card__job-insight li")
            
            for criteria in criteria_list:
                text = criteria.inner_text().strip()
                
                if "Employment type" in text:
                    job_info["employment_type"] = text.replace("Employment type:", "").strip()
                elif "experience" in text.lower():
                    job_info["experience_level"] = text
                elif "Hybrid" in text or "Remote" in text or "On-site" in text:
                    job_info["remote_type"] = text
            
            # Create job details
            job_details = JobDetails(
                job_id=job_id,
                title=title,
                company=company,
                location=location,
                url=job_url,
                description=description,
                employment_type=job_info.get("employment_type"),
                experience_level=job_info.get("experience_level"),
                remote_type=job_info.get("remote_type")
            )
            
            return job_details
            
        except Exception as e:
            logger.error(f"Error getting job details for {job_id}: {e}")
            return None
    
    def is_logged_in(self) -> bool:
        """
        Check if currently logged in to LinkedIn
        
        Returns:
            bool: True if logged in, False otherwise
        """
        if not self.page:
            return False
        
        try:
            # Navigate to LinkedIn homepage
            self.page.goto("https://www.linkedin.com/feed/")
            
            # Check for login page or feed page
            if self.page.url.startswith("https://www.linkedin.com/feed"):
                return True
            else:
                return False
            
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False


def cli():
    """
    Command-line interface for the LinkedIn Scraper
    """
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="LinkedIn Job Scraper CLI")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--slow-mo", type=int, default=100, help="Slow down operations by milliseconds")
    parser.add_argument("--timeout", type=int, default=30000, help="Timeout for operations in milliseconds")
    parser.add_argument("--browser-state", help="Path to browser state directory")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Logging level")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Login command
    login_parser = subparsers.add_parser("login", help="Log in to LinkedIn")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for jobs")
    search_parser.add_argument("--keywords", help="Job keywords")
    search_parser.add_argument("--location", help="Job location")
    search_parser.add_argument("--job-type", help="Job type")
    search_parser.add_argument("--experience", help="Experience level")
    search_parser.add_argument("--remote", help="Remote filter")
    search_parser.add_argument("--max-results", type=int, default=25, help="Maximum number of results")
    search_parser.add_argument("--output", help="Output file path (JSON)")
    
    # Job details command
    details_parser = subparsers.add_parser("details", help="Get job details")
    details_parser.add_argument("job_id", help="LinkedIn job ID")
    details_parser.add_argument("--output", help="Output file path (JSON)")
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Initialize scraper
    scraper = LinkedInScraper(
        headless=args.headless,
        slow_mo=args.slow_mo,
        timeout=args.timeout,
        browser_state_dir=args.browser_state
    )
    
    try:
        # Start browser
        if not scraper.start():
            logger.error("Failed to start browser")
            return 1
        
        if args.command == "login":
            # Perform login
            success = scraper.login()
            if success:
                print("Successfully logged in to LinkedIn")
                return 0
            else:
                print("Failed to log in to LinkedIn")
                return 1
        
        elif args.command == "search":
            # Check if logged in
            if not scraper.is_logged_in() and not scraper.login():
                print("Not logged in to LinkedIn")
                return 1
            
            # Create search parameters
            search_params = JobSearchParams(
                keywords=args.keywords,
                location=args.location,
                job_type=args.job_type,
                experience_level=args.experience,
                remote_filter=args.remote,
                max_results=args.max_results
            )
            
            # Search for jobs
            job_listings = scraper.search_jobs(search_params)
            
            # Output results
            if args.output:
                with open(args.output, "w") as f:
                    json.dump([job.model_dump() for job in job_listings], f, indent=2, default=str)
                print(f"Saved {len(job_listings)} job listings to {args.output}")
            else:
                print(f"Found {len(job_listings)} job listings:")
                for i, job in enumerate(job_listings):
                    print(f"{i+1}. {job.title} at {job.company} ({job.location})")
                    print(f"   URL: {job.url}")
                    print()
            
            return 0
        
        elif args.command == "details":
            # Check if logged in
            if not scraper.is_logged_in() and not scraper.login():
                print("Not logged in to LinkedIn")
                return 1
            
            # Get job details
            job_details = scraper.get_job_details(args.job_id)
            
            if not job_details:
                print(f"Failed to get details for job {args.job_id}")
                return 1
            
            # Output results
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(job_details.model_dump(), f, indent=2, default=str)
                print(f"Saved job details to {args.output}")
            else:
                print(f"Job Details for {args.job_id}:")
                print(f"Title: {job_details.title}")
                print(f"Company: {job_details.company}")
                print(f"Location: {job_details.location}")
                print(f"Employment Type: {job_details.employment_type}")
                print(f"Experience Level: {job_details.experience_level}")
                print(f"Remote Type: {job_details.remote_type}")
                print(f"URL: {job_details.url}")
                print("\nDescription:")
                print(job_details.description[:500] + "..." if job_details.description and len(job_details.description) > 500 else job_details.description or "No description available")
            
            return 0
        
        else:
            parser.print_help()
            return 0
    
    finally:
        # Clean up
        scraper.stop()


if __name__ == "__main__":
    import sys
    sys.exit(cli())