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

# Import LinkedInUIAgent from its own file
import classes.linkedin_ui_agent
importlib.reload(classes.linkedin_ui_agent)
from classes.linkedin_ui_agent import LinkedInUIAgent

# Import PrefModel
import classes.PrefModel
importlib.reload(classes.PrefModel)
from classes.PrefModel import PrefModel

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
    
    # Test mode arguments (mutually exclusive)
    test_mode = parser.add_mutually_exclusive_group()
    test_mode.add_argument(
        "--login-only",
        action="store_true",
        help="Only test the login functionality without navigation",
    )
    
    # Add updatepref flag (defaults to True)
    parser.add_argument(
        "--updatepref",
        dest="update_preferences",
        action="store_true",
        default=True,
        help="Navigate to job preferences onboarding page (default: True)",
    )
    parser.add_argument(
        "--no-updatepref",
        dest="update_preferences",
        action="store_false",
        help="Don't navigate to job preferences page after login",
    )
    
    # LLM arguments
    parser.add_argument(
        "--use-browser-llm",
        action="store_true",
        default=True,
        help="Use browser-use with local Ollama (default)",
    )
    
    # Test applying preferences
    parser.add_argument(
        "--apply-prefs",
        action="store_true",
        default=False,
        help="Test applying preferences using AI agent",
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
            
            # Step 1: Testing complete if login-only mode
            if args.login_only:
                print("\nLogin test completed successfully!")
                
            
            # Navigate to preferences page if updatepref is True (default)
            elif args.update_preferences:
                print("\nNavigating to job preferences onboarding page...")
                job_pref_result = agent.navigate_to_job_preferences()
                logger.info(f"Job preferences navigation result: {job_pref_result}")
                
                if job_pref_result:
                    print("\nSuccessfully navigated to job preferences onboarding page!")
                    
                    # Test applying preferences if requested
                    if args.apply_prefs:
                        print("\nTesting preference application with AI agent...")
                        
                        # Initialize preference model
                        pref_model = PrefModel()
                        
                        # Initialize UI agent
                        ui_agent = LinkedInUIAgent(agent)
                        
                        print("Using browser-use with local Ollama (llama3:8b)")
                        
                        # Apply some test preferences
                        test_prefs = {
                            "job_type": ["Full-time", "Part-time", "Internship"],
                            "modality": ["Remote"]
                        }
                        
                        print(f"Applying test preferences: {test_prefs}")
                        result = ui_agent.apply_preferences(test_prefs)
                        print(f"Preference application result:\n{result}")
                        
                        print("\nPreference test completed.")
                else:
                    print("\nFailed to navigate to job preferences onboarding page.")
            
            # If no-updatepref is specified, just stay at the current page after login
            else:
                print("\nStaying on current page after login as requested.")
            
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