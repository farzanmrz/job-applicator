# General Imports
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Playwright imports
from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright
from pydantic import Field

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Agent setup imports
from agents.AgtBase import AgtBase, EnumAgtType
from tools.auth.TlAuthLkdn import TlAuthLkdn

# Utility/tool imports
from utils.commonutil import set_logger

# Set up logger with custom format and name of current module
logger = set_logger("SrchWrkrLkdn")


# Class starts here
class SrchWrkrLkdn(AgtBase):
    """Worker agent responsible for LinkedIn-specific job search operations and authentication"""

    def __init__(self, headless: bool = True):
        """Initialize the LinkedIn Search Worker Agent"""

        # 1a. Initialize the base class with the inherited constructor
        super().__init__(agt_type=EnumAgtType.WRKR, agt_pid="defaultpid.000000")
        logger.info(f"Search Worker LinkedIn initialized with ID {self.agt_id}")

        # 1b. Initialize base URLs
        self.BASE_URL = "https://www.linkedin.com"
        self.LOGIN_URL = "https://www.linkedin.com/login"
        self.CAPTCHA_URL = "https://www.linkedin.com/checkpoint/challenge/"
        self.ERROR_URL = "https://www.linkedin.com/checkpoint/lg/login-submit"
        self.FEED_URL = "https://www.linkedin.com/feed/"

        # 1c. Initialize instance variables
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=headless)

        # 1d. Get browser context using TlAuthLkdn
        self.auth_tool = TlAuthLkdn()
        self.context = self.auth_tool.get_valid_context(self.browser)
        if not self.context:
            logger.critical("Failed to obtain valid browser context.")


# For testing
if __name__ == "__main__":
    # Minimal test block
    agent = SrchWrkrLkdn(headless=False)
    if agent.context:
        logger.info("Context created successfully.")
    else:
        logger.error("Failed to create context.")
