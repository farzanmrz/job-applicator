import uuid
from enum import Enum
from typing import Any, Dict


# Agent type enumeration
class EnumAgtType(str, Enum):
    """Constants for different agent types in the system hierarchy."""

    COORD = "coord"  # Coordinator - top-level orchestrator
    MGR = "mgr"  # Manager - manages a specific domain/category
    WRKR = "wrkr"  # Worker - performs specific tasks


class AgtBase:
    """Base class for all agents in the system."""

    def __init__(self, agt_type: EnumAgtType, agt_pid: str):
        """
        Initialize a new agent instance directly.

        Args:
            agt_type: The type of agent (EnumAgtType).
            agt_pid: Parent ID of above this agent instance.
            agt_name: Name of the agent class.
            agt_id: Unique identifier for this agent instance
            active_tasks: Dictionary to hold active tasks for this agent.
        """
        # --- Direct assignment of attributes ---
        self.agt_type = agt_type
        self.agt_pid = agt_pid
        self.agt_name = self.__class__.__name__
        self.agt_id = f"{self.agt_type.value}.{uuid.uuid4().hex[:6]}"
        self.active_tasks = {}
