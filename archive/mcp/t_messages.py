#!/usr/bin/env python3
"""
MCP Message Structure Module - Foundation for agent communication protocol
"""

import uuid
import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator


class MessageType(str, Enum):
    TASK = "task"
    STATUS = "status"
    ERROR = "error"
    QUERY = "query"
    RESPONSE = "response"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Message(BaseModel):
    """Base MCP message class with common fields for all message types"""
    
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    sender: str
    recipient: str
    message_type: MessageType
    status: Optional[TaskStatus] = None
    
    class Config:
        extra = "forbid"  # Prevent extra fields not defined in the model
    
    @validator('timestamp', pre=True)
    def ensure_datetime(cls, v):
        """Ensure timestamp is a datetime object"""
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v)
        return v


class TaskMessage(Message):
    """Message for defining and assigning tasks to agents"""
    
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = Field(default_factory=list)  # List of task_ids this task depends on
    parameters: Dict[str, Any] = Field(default_factory=dict)  # Task-specific parameters
    deadline: Optional[datetime.datetime] = None
    
    @validator('message_type')
    def validate_message_type(cls, v):
        """Ensure the message_type is TASK for this message class"""
        if v != MessageType.TASK:
            raise ValueError(f"message_type must be {MessageType.TASK} for TaskMessage")
        return v
    
    @validator('deadline', pre=True)
    def ensure_deadline_datetime(cls, v):
        """Ensure deadline is a datetime object if provided"""
        if v is not None and isinstance(v, str):
            return datetime.datetime.fromisoformat(v)
        return v


class StatusMessage(Message):
    """Message for reporting task status updates"""
    
    task_id: str
    status: TaskStatus
    progress: Optional[float] = None  # Progress indicator between 0.0 and 1.0
    details: Optional[str] = None  # Detailed information about current status
    estimated_completion: Optional[datetime.datetime] = None
    
    @validator('message_type')
    def validate_message_type(cls, v):
        """Ensure the message_type is STATUS for this message class"""
        if v != MessageType.STATUS:
            raise ValueError(f"message_type must be {MessageType.STATUS} for StatusMessage")
        return v
    
    @validator('progress')
    def validate_progress(cls, v):
        """Ensure progress is between 0.0 and 1.0 if provided"""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("progress must be between 0.0 and 1.0")
        return v
    
    @validator('estimated_completion', pre=True)
    def ensure_completion_datetime(cls, v):
        """Ensure estimated_completion is a datetime object if provided"""
        if v is not None and isinstance(v, str):
            return datetime.datetime.fromisoformat(v)
        return v


class ErrorMessage(Message):
    """Message for reporting errors during task execution"""
    
    task_id: Optional[str] = None
    error_code: str
    error_message: str
    severity: ErrorSeverity
    trace: Optional[str] = None
    recovery_suggestion: Optional[str] = None
    
    @validator('message_type')
    def validate_message_type(cls, v):
        """Ensure the message_type is ERROR for this message class"""
        if v != MessageType.ERROR:
            raise ValueError(f"message_type must be {MessageType.ERROR} for ErrorMessage")
        return v


class QueryMessage(Message):
    """Message for requesting information from another agent"""
    
    query_type: str  # Type of query (e.g., "job_status", "user_preferences")
    query_parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[float] = None  # Timeout in seconds
    
    @validator('message_type')
    def validate_message_type(cls, v):
        """Ensure the message_type is QUERY for this message class"""
        if v != MessageType.QUERY:
            raise ValueError(f"message_type must be {MessageType.QUERY} for QueryMessage")
        return v


class ResponseMessage(Message):
    """Message responding to a QueryMessage"""
    
    query_id: str  # message_id of the original QueryMessage
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None  # Error message if the query could not be processed
    
    @validator('message_type')
    def validate_message_type(cls, v):
        """Ensure the message_type is RESPONSE for this message class"""
        if v != MessageType.RESPONSE:
            raise ValueError(f"message_type must be {MessageType.RESPONSE} for ResponseMessage")
        return v


# Utility functions for message handling

def generate_message_id() -> str:
    """Generate a unique message ID"""
    return str(uuid.uuid4())


def generate_task_id() -> str:
    """Generate a unique task ID"""
    return str(uuid.uuid4())


def create_task_message(
    sender: str,
    recipient: str,
    description: str,
    priority: Union[TaskPriority, str] = TaskPriority.MEDIUM,
    dependencies: List[str] = None,
    parameters: Dict[str, Any] = None,
    deadline: Optional[datetime.datetime] = None
) -> TaskMessage:
    """Create a new task message"""
    # Convert string priority to enum if needed
    if isinstance(priority, str):
        priority = TaskPriority(priority)
    
    return TaskMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.TASK,
        description=description,
        priority=priority,
        dependencies=dependencies or [],
        parameters=parameters or {},
        deadline=deadline
    )


def create_status_message(
    sender: str,
    recipient: str,
    task_id: str,
    status: Union[TaskStatus, str],
    progress: Optional[float] = None,
    details: Optional[str] = None,
    estimated_completion: Optional[datetime.datetime] = None
) -> StatusMessage:
    """Create a new status message"""
    # Convert string status to enum if needed
    if isinstance(status, str):
        status = TaskStatus(status)
    
    return StatusMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.STATUS,
        task_id=task_id,
        status=status,
        progress=progress,
        details=details,
        estimated_completion=estimated_completion
    )


def create_error_message(
    sender: str,
    recipient: str,
    error_code: str,
    error_message: str,
    severity: Union[ErrorSeverity, str] = ErrorSeverity.ERROR,
    task_id: Optional[str] = None,
    trace: Optional[str] = None,
    recovery_suggestion: Optional[str] = None
) -> ErrorMessage:
    """Create a new error message"""
    # Convert string severity to enum if needed
    if isinstance(severity, str):
        severity = ErrorSeverity(severity)
    
    return ErrorMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.ERROR,
        error_code=error_code,
        error_message=error_message,
        severity=severity,
        task_id=task_id,
        trace=trace,
        recovery_suggestion=recovery_suggestion
    )


def create_query_message(
    sender: str,
    recipient: str,
    query_type: str,
    query_parameters: Dict[str, Any] = None,
    timeout: Optional[float] = None
) -> QueryMessage:
    """Create a new query message"""
    return QueryMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.QUERY,
        query_type=query_type,
        query_parameters=query_parameters or {},
        timeout=timeout
    )


def create_response_message(
    sender: str,
    recipient: str,
    query_id: str,
    data: Dict[str, Any] = None,
    error: Optional[str] = None
) -> ResponseMessage:
    """Create a new response message"""
    return ResponseMessage(
        sender=sender,
        recipient=recipient,
        message_type=MessageType.RESPONSE,
        query_id=query_id,
        data=data or {},
        error=error
    )


def serialize_message(message: Message) -> Dict[str, Any]:
    """Serialize a message to a dictionary"""
    return message.dict()


def deserialize_message(message_data: Dict[str, Any]) -> Message:
    """Deserialize a message from a dictionary to the appropriate message class"""
    message_type = message_data.get("message_type")
    
    # Map message_type to the appropriate class
    message_classes = {
        MessageType.TASK: TaskMessage,
        MessageType.STATUS: StatusMessage,
        MessageType.ERROR: ErrorMessage,
        MessageType.QUERY: QueryMessage,
        MessageType.RESPONSE: ResponseMessage
    }
    
    # Get the appropriate class or default to base Message
    message_class = message_classes.get(message_type, Message)
    
    # Parse the message data into the class
    return message_class.parse_obj(message_data)