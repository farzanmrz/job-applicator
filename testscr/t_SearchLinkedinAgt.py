#!/usr/bin/env python3
"""
Test script for the LinkedIn Search Agent
"""

import sys
import os
import logging
import argparse

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from agents.search.SearchLinkedinAgt import SearchLinkedinAgt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('linkedin_test')

def main():
    parser = argparse.ArgumentParser(description='Test LinkedIn Search Agent')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--search', action='store_true', help='Perform job search after login')
    parser.add_argument('--keywords', type=str, default='software engineer', help='Job search keywords')
    parser.add_argument('--location', type=str, default='', help='Job location')
    
    args = parser.parse_args()
    
    logger.info("Initializing LinkedIn Search Agent...")
    agent = SearchLinkedinAgt(headless=args.headless)
    
    try:
        # Test login
        logger.info("Testing LinkedIn login...")
        login_result = agent.login()
        logger.info(f"Login result: {login_result}")
        
        # Test job search if requested and login was successful
        if args.search and login_result is True:
            logger.info(f"Searching for jobs with keywords: {args.keywords}")
            jobs = agent.search_jobs(args.keywords, args.location)
            
            logger.info(f"Found {len(jobs)} jobs")
            # Display the first 5 jobs
            for i, job in enumerate(jobs[:5]):
                print(f"\nJob {i+1}:")
                print(f"  Title: {job['title']}")
                print(f"  Company: {job['company']}")
                print(f"  Location: {job['location']}")
                print(f"  URL: {job['url']}")
    finally:
        # Always close the browser
        agent.close()

if __name__ == "__main__":
    main()