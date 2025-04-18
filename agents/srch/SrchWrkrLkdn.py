import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pydantic import Field

from agents.AgtBase import AgtBase, EnumAgtType
from mcp.messages import (
    EnumMsgType,
    EnumTaskPriority,
    EnumTaskState,
    Msg,
    MsgStatus,
    MsgTask,
)
from utils.commonutil import set_logger

# Get logger
logger = set_logger("SrchWrkrLkdn")


class SrchWrkrLkdn(AgtBase):
    """Worker agent responsible for LinkedIn-specific job search operations and authentication"""

    # Define auth field with default value
    auth: bool = False

    def __init__(self):
        """Initialize the LinkedIn Search Worker Agent"""
        super().__init__(agt_type=EnumAgtType.WRKR, agt_pid="defaultpid.000000")
        logger.info(f"Search Worker LinkedIn initialized with ID {self.agt_id}")


# For testing
if __name__ == "__main__":
    agent = SrchWrkrLkdn()
