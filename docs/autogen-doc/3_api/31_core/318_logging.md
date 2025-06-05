# autogen_core.logging

---

**`class` AgentConstructionExceptionEvent ( `*` , `agent_id` : `AgentId` , `exception` : `BaseException` , `**kwargs` : `Any` ) [source]**

Bases: `object`

This class defines an event that occurs when an exception is encountered during the construction of an agent. It records the `agent_id` of the agent being constructed and the `exception` that occurred, along with any additional keyword arguments.

---

**`class` DeliveryStage ( `value` , `names = None` , `*` , `module = None` , `qualname = None` , `type = None` , `start = 1` , `boundary = None` ) [source]**

Bases: `Enum`

The `DeliveryStage` enum specifies the stage of message delivery.

`DELIVER` `= 2`
Represents the stage where a message is delivered.

`SEND` `= 1`
Represents the stage where a message is sent.

---

**`class` LLMCallEvent ( `*` , `messages` : `List[Dict[str, Any]]` , `response` : `Dict[str, Any]` , `prompt_tokens` : `int` , `completion_tokens` : `int` , `**kwargs` : `Any` ) [source]**

Bases: `object`

This class represents an event logging a complete LLM (Large Language Model) call. It captures the `messages` exchanged during the call, the `response` received from the LLM, and the token counts associated with the interaction.

`property` `completion_tokens`: `int`
The number of completion tokens generated in the LLM response.

`property` `prompt_tokens`: `int`
The number of prompt tokens used in the LLM call.

---

**`class` LLMStreamEndEvent ( `*` , `response` : `Dict[str, Any]` , `prompt_tokens` : `int` , `completion_tokens` : `int` , `**kwargs` : `Any` ) [source]**

Bases: `object`

This class is used to log the end of an LLM streaming response. It includes the final `response` received, along with the total `prompt_tokens` and `completion_tokens` for the stream.

`property` `completion_tokens`: `int`
The total number of completion tokens generated during the LLM stream.

`property` `prompt_tokens`: `int`
The total number of prompt tokens used for the LLM stream.

---

**`class` LLMStreamStartEvent ( `*` , `messages` : `List[Dict[str, Any]]` , `**kwargs` : `Any` ) [source]**

Bases: `object`

This event class is intended to be used by model clients to log the initiation of an LLM streaming interaction. It captures the initial set of messages that prompt the stream.

**Parameters**:

*   **`messages`** (`List[Dict[str, Any]]`) – The messages used in the call. These messages must be json serializable for logging purposes.

**Example**

The following example demonstrates how to log the start of an LLM stream using `LLMStreamStartEvent` within the `autogen_core.logging` framework.

```python
import logging
from autogen_core import EVENT_LOGGER_NAME
from autogen_core.logging import LLMStreamStartEvent

messages = [{"role": "user", "content": "Hello, world!"}]
logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.info(LLMStreamStartEvent(messages=messages))
```

---

**`class` MessageDroppedEvent ( `*` , `payload` : `str` , `sender` : `AgentId | None` , `receiver` : `AgentId | TopicId | None` , `kind` : `MessageKind` , `**kwargs` : `Any` ) [source]**

Bases: `object`

This class logs an event where a message was dropped and not processed or delivered. It specifies the `payload` of the message, its `sender` (if known), its intended `receiver`, and the `kind` of message, along with any other pertinent keyword arguments.

---

**`class` MessageEvent ( `*` , `payload` : `str` , `sender` : `AgentId | None` , `receiver` : `AgentId | TopicId | None` , `kind` : `MessageKind` , `delivery_stage` : `DeliveryStage` , `**kwargs` : `Any` ) [source]**

Bases: `object`

The `MessageEvent` class logs a general message activity within the system. It captures the message's `payload`, its `sender` and `receiver`, the `kind` of message, and its current `delivery_stage`, providing a detailed record of message lifecycle.

---

**`class` MessageHandlerExceptionEvent ( `*` , `payload` : `str` , `handling_agent` : `AgentId` , `exception` : `BaseException` , `**kwargs` : `Any` ) [source]**

Bases: `object`

This class logs an event where an exception occurred during the handling of a message by a specific agent. It includes the message `payload`, the `handling_agent` responsible for processing it, and the `exception` that was raised during processing, along with any additional details.

---

**`class` MessageKind ( `value` , `names = None` , `*` , `module = None` , `qualname = None` , `type = None` , `start = 1` , `boundary = None` ) [source]**

Bases: `Enum`

The `MessageKind` enum categorizes the type of a message based on its intended interaction or purpose.

`DIRECT` `= 1`
Indicates a message intended for a specific, direct recipient.

`PUBLISH` `= 2`
Indicates a message intended to be published to a topic or for general consumption by interested parties.

`RESPOND` `= 3`
Indicates a message that is a response to a previous message or query.

---

**`class` ToolCallEvent ( `*` , `tool_name` : `str` , `arguments` : `Dict[str, Any]` , `result` : `str` ) [source]**

Bases: `object`

The `ToolCallEvent` class logs details about a tool call made within the system. It records the `tool_name` that was invoked, the `arguments` passed to the tool as a dictionary, and the `result` obtained from the tool's execution.

---
