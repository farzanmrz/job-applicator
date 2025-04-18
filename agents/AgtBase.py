#!/usr/bin/env python3
"""
Base Agent Class - Foundation for all agents in the system

This module defines the base agent class and agent type enumeration
that all specialized agents in the system will inherit from.
"""

import uuid
from enum import Enum
from typing import Dict, Any

from pydantic import BaseModel, Field

# Agent type enumeration
class EnumAgtType(str, Enum):
    """Constants for different agent types in the system hierarchy."""

    COORD = "coord"  # Coordinator - top-level orchestrator
    MGR = "mgr"      # Manager - manages a specific domain/category
    WRKR = "wrkr"    # Worker - performs specific tasks

class AgtBase(BaseModel):
    """
    Base class for all agents in the system.
    
    This class provides common attributes and functionality that all agents share,
    regardless of their specific role or type.
    
    Attributes:
        agt_type: The type of agent (coordinator, manager, worker)
        agt_pid: Process ID or other identifier for the agent instance
        agt_name: Name of the agent class
        agt_id: Unique identifier for this agent instance
    """

    agt_type: EnumAgtType
    agt_pid: str
    agt_name: str
    agt_id: str
    
    # Dictionary to track active tasks
    active_tasks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    def __init__(self, **data):
        """
        Initialize a new agent instance.
        
        Sets up the agent name based on class name and generates a unique
        agent ID combining the agent type and a random identifier.
        
        Args:
            **data: Keyword arguments for initializing the agent
        """
        # Set agent name to the class name
        data["agt_name"] = self.__class__.__name__
        
        # Generate a unique ID that includes the agent type prefix
        data["agt_id"] = f"{data['agt_type'].value}.{uuid.uuid4().hex[:6]}"
        
        # Initialize the base class
        super().__init__(**data)