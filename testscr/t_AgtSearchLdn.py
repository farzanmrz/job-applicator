#!/usr/bin/env python3
"""
Test script for the LinkedIn Search Agent
"""

import argparse
import logging
import os
import sys
import time
import importlib

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Import and reload the module to ensure latest version
import classes.AgtSearchLdn
importlib.reload(classes.AgtSearchLdn)
from classes.AgtSearchLdn import AgtSearchLdn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("linkedin_test")


def main():
    parser = argparse.ArgumentParser(description="Test LinkedIn Search Agent")
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run in headless mode (default: False)",
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Run with visible browser (overrides headless)",
    )
    # Action arguments
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Wait for manual verification even in headless mode",
    )
    parser.add_argument(
        "--no-cookies",
        action="store_true",
        help="Do not use stored cookies for authentication",
    )

    args = parser.parse_args()

    # If visible flag is set, override headless setting
    if args.visible:
        args.headless = False

    logger.info("Initializing LinkedIn Search Agent...")
    logger.info(f"Headless mode: {'enabled' if args.headless else 'disabled'}")
    agent = AgtSearchLdn(headless=args.headless)

    try:
        # Test login
        logger.info("Testing LinkedIn login...")
        logger.info(f"Using cookies: {'disabled' if args.no_cookies else 'enabled'}")
        login_result = agent.login(use_cookies=not args.no_cookies)
        logger.info(f"Login result: {login_result}")

        if login_result is True:
            logger.info("Login successful!")
            
            # Navigate to job preferences by default
            logger.info("Navigating to job preferences page...")
            job_pref_result = agent.navigate_to_job_preferences()
            logger.info(f"Job preferences navigation result: {job_pref_result}")
            
            if job_pref_result:
                print("\nSuccessfully navigated to job preferences page!")
            else:
                print("\nFailed to navigate to job preferences page.")
            
            print("\nBrowser will remain open.")
            print("Press Ctrl+C to close the browser and exit.")
            try:
                # Keep the script running until user interrupts
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("User interrupted. Closing browser.")
                print("\nClosing browser...")
    finally:
        # Always close the browser when exiting
        agent.close()


if __name__ == "__main__":
    main()