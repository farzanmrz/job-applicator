#!/usr/bin/env python3
"""
Message Control Protocol (MCP) - Foundation for agent communication

This module defines the core message structure that enables different
agents in the system to communicate with each other in a standardized way.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ========== ENUM TYPES ==========


class EnumMsgType(str, Enum):
    """Enumeration of different message types in the MCP system.

    Attributes:
        TASK: Instruct an agent to perform work.
        STATUS: Report on the progress of a task.
        ERROR: Report a problem or failure.
        QUERY: Request information from another agent.
        RESPONSE: Answer to a query.
    """

    TASK = "task"
    STATUS = "status"
    ERROR = "error"
    QUERY = "query"
    RESPONSE = "response"


class EnumTaskState(str, Enum):
    """Enumeration of possible task states.

    Attributes:
        PENDING: Task is created but not yet started.
        STARTED: Task has been picked up by an agent.
        IN_PROGRESS: Task is actively being worked on.
        COMPLETED: Task has been successfully completed.
        FAILED: Task could not be completed.
    """

    PENDING = "pending"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class EnumTaskPriority(str, Enum):
    """Enumeration of task priority levels.

    Attributes:
        LOW: Background tasks without time sensitivity.
        MEDIUM: Standard tasks with normal priority.
        HIGH: Urgent tasks that should be processed ahead of others.
        CRITICAL: Highest priority tasks requiring immediate attention.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"




# ========== MESSAGE CLASSES ==========


class Msg(BaseModel):
    """Base message class with common fields for all message types.

    Attributes:
        msg_id: Unique identifier for the message.
        time: Timestamp when the message was created.
        src: Source agent that sent the message.
        tgt: Target agent that will receive the message.
        msg_type: Type of message from EnumMsgType.
    """

    msg_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    time: datetime = Field(default_factory=datetime.now)
    src: str
    tgt: str
    msg_type: EnumMsgType


class MsgTask(Msg):
    """Task message for assigning work to agents.

    Attributes:
        task_id: Unique identifier for the task.
        task_desc: Human-readable description of the task.
        task_priority: Priority level from EnumTaskPriority.
        task_params: Dictionary of task parameters and arguments.
    """

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_desc: str
    task_priority: EnumTaskPriority = EnumTaskPriority.MEDIUM
    task_params: Dict[str, Any] = Field(default_factory=dict)


class MsgStatus(Msg):
    """Status message for reporting task progress.

    Attributes:
        status_task_id: ID of the task this status update refers to.
        status_state: Current state of the task from EnumTaskState.
        status_progress: Optional numeric progress indicator (0.0 to 1.0).
        status_detail: Optional text description of current status.
    """

    status_task_id: str
    status_state: EnumTaskState
    status_progress: Optional[float] = None
    status_detail: Optional[str] = None


