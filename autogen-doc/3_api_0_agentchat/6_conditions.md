# `autogen_agentchat.conditions`

This module provides various termination conditions for controlling the behavior of multi-agent teams.

## `class ExternalTermination`

Bases: `TerminationCondition`, `Component[ExternalTerminationConfig]`

A termination condition that is externally controlled by calling the `set()` method.

**Example**:
```python
from   autogen_agentchat.conditions   import   ExternalTermination
termination   =   ExternalTermination ()
# Run the team in an asyncio task.
...
# Set the termination condition externally
termination . set ()
```


### `classmethod _from_config(*config: ExternalTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → ExternalTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `ExternalTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.ExternalTermination'`

Override the provider string for the component. This should be used to prevent internal module names from being a part of the module name.

### `async reset() → None`

Reset the termination condition.

### `set() → None`

Set the termination condition to terminated.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class FunctionCallTermination(function_name: str)`

Bases: `TerminationCondition`, `Component[FunctionCallTerminationConfig]`

Terminate the conversation if a `FunctionExecutionResult` with a specific name was received.

**Parameters**:
*   **function_name** (`str`) – The name of the function to look for in the messages.

**Raises**:
*   **TerminatedException** – If the termination condition has already been reached.

### `classmethod _from_config(*config: FunctionCallTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → FunctionCallTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `FunctionCallTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.FunctionCallTermination'`

The schema for the component configuration.

### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class FunctionalTermination(func: Callable[[Sequence[BaseAgentEvent | BaseChatMessage]], bool] | Callable[[Sequence[BaseAgentEvent | BaseChatMessage]], Awaitable[bool]])`

Bases: `TerminationCondition`

Terminate the conversation if a functional expression is met.

**Parameters**:
*   **func** (`Callable[[Sequence[BaseAgentEvent | BaseChatMessage]], bool] | Callable[[Sequence[BaseAgentEvent | BaseChatMessage]], Awaitable[bool]]`) – A function that takes a sequence of messages and returns `True` if the termination condition is met, `False` otherwise. The function can be a callable or an async callable.

**Example**:
```python
import   asyncio
from   typing   import   Sequence
from   autogen_agentchat.conditions   import   FunctionalTermination
from   autogen_agentchat.messages   import   BaseAgentEvent ,   BaseChatMessage ,   StopMessage

def   expression ( messages :   Sequence [ BaseAgentEvent   |   BaseChatMessage ])   ->   bool :
    # Check if the last message is a stop message
    return   isinstance ( messages [ - 1 ],   StopMessage )

termination   =   FunctionalTermination ( expression )

async   def   run ()   ->   None :
    messages   =   [   StopMessage ( source = "agent1" ,   content = "Stop" ),   ]
    result   =   await   termination ( messages )
    print ( result )

asyncio . run ( run ())
```
Output:
```
StopMessage(source="FunctionalTermination", content="Functional termination condition met")
```


### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class HandoffTermination(target: str)`

Bases: `TerminationCondition`, `Component[HandoffTerminationConfig]`

Terminate the conversation if a `HandoffMessage` with the given target is received.

**Parameters**:
*   **target** (`str`) – The target of the handoff message.

### `classmethod _from_config(*config: HandoffTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → HandoffTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `HandoffTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.HandoffTermination'`

Override the provider string for the component. This should be used to prevent internal module names from being a part of the module name.

### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class MaxMessageTermination(max_messages: int, include_agent_event: bool = False)`

Bases: `TerminationCondition`, `Component[MaxMessageTerminationConfig]`

Terminate the conversation after a maximum number of messages have been exchanged.

**Parameters**:
*   **max_messages** (`int`) – The maximum number of messages allowed in the conversation.
*   **include_agent_event** (`bool`) – If `True`, include `BaseAgentEvent` in the message count. Otherwise, only include `BaseChatMessage`. Defaults to `False`.

### `classmethod _from_config(*config: MaxMessageTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → MaxMessageTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `MaxMessageTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.MaxMessageTermination'`

Override the provider string for the component. This should be used to prevent internal module names from being a part of the module name.

### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class SourceMatchTermination(sources: List[str])`

Bases: `TerminationCondition`, `Component[SourceMatchTerminationConfig]`

Terminate the conversation after a specific source responds.

**Parameters**:
*   **sources** (`List[str]`) – List of source names to terminate the conversation.

**Raises**:
*   **TerminatedException** – If the termination condition has already been reached.

### `classmethod _from_config(*config: SourceMatchTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → SourceMatchTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `SourceMatchTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.SourceMatchTermination'`

Override the provider string for the component. This should be used to prevent internal module names from being a part of the module name.

### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class StopMessageTermination`

Bases: `TerminationCondition`, `Component[StopMessageTerminationConfig]`

Terminate the conversation if a `StopMessage` is received.

### `classmethod _from_config(*config: StopMessageTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → StopMessageTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `StopMessageTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.StopMessageTermination'`

Override the provider string for the component. This should be used to prevent internal module names from being a part of the module name.

### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class TextMentionTermination(text: str, sources: Sequence[str] | None = None)`

Bases: `TerminationCondition`, `Component[TextMentionTerminationConfig]`

Terminate the conversation if a specific text is mentioned.

**Parameters**:
*   **text** (`str`) – The text to look for in the messages.
*   **sources** (`Sequence[str] | None`) – Check only messages of the specified agents for the text to look for.

### `classmethod _from_config(*config: TextMentionTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → TextMentionTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `TextMentionTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.TextMentionTermination'`

Override the provider string for the component. This should be used to prevent internal module names from being a part of the module name.

### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class TextMessageTermination(source: str | None = None)`

Bases: `TerminationCondition`, `Component[TextMessageTerminationConfig]`

Terminate the conversation if a `TextMessage` is received.

This termination condition checks for `TextMessage` instances in the message sequence. When a `TextMessage` is found, it terminates the conversation if either:
*   No source was specified (terminates on any `TextMessage`)
*   The message source matches the specified source

**Parameters**:
*   **source** (`str | None`, *optional*) – The source name to match against incoming messages. If `None`, matches any source. Defaults to `None`.

### `classmethod _from_config(*config: TextMessageTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → TextMessageTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `TextMessageTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.TextMessageTermination'`

Override the provider string for the component. This should be used to prevent internal module names from being a part of the module name.

### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class TimeoutTermination(timeout_seconds: float)`

Bases: `TerminationCondition`, `Component[TimeoutTerminationConfig]`

Terminate the conversation after a specified duration has passed.

**Parameters**:
*   **timeout_seconds** (`float`) – The maximum duration in seconds before terminating the conversation.

### `classmethod _from_config(*config: TimeoutTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → TimeoutTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `TimeoutTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.TimeoutTermination'`

Override the provider string for the component. This should be used to prevent internal module names from being a part of the module name.

### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---

## `class TokenUsageTermination(max_total_token: int | None = None, max_prompt_token: int | None = None, max_completion_token: int | None = None)`

Bases: `TerminationCondition`, `Component[TokenUsageTerminationConfig]`

Terminate the conversation if a token usage limit is reached.

**Parameters**:
*   **max_total_token** (`int | None`) – The maximum total number of tokens allowed in the conversation.
*   **max_prompt_token** (`int | None`) – The maximum number of prompt tokens allowed in the conversation.
*   **max_completion_token** (`int | None`) – The maximum number of completion tokens allowed in the conversation.

**Raises**:
*   **ValueError** – If none of `max_total_token`, `max_prompt_token`, or `max_completion_token` is provided.

### `classmethod _from_config(*config: TokenUsageTerminationConfig) → Self`

Create a new instance of the component from a configuration object.

**Parameters**:
*   **config** (`T`) – The configuration object.

**Returns**:
*   **Self** – The new instance of the component.

### `_to_config() → TokenUsageTerminationConfig`

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**:
*   **T** – The configuration of the component.

### `component_config_schema`

alias of `TokenUsageTerminationConfig`

### `component_provider_override: ClassVar[str | None]`

`= 'autogen_agentchat.conditions.TokenUsageTermination'`

Override the provider string for the component. This should be used to prevent internal module names from being a part of the module name.

### `async reset() → None`

Reset the termination condition.

### `property terminated: bool`

Check if the termination condition has been reached.

---