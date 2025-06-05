# autogen_core.model_context #

## *class* **BufferedChatCompletionContext** (*buffer_size* : *int*, *initial_messages* : *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]] | None = None) [source] #

Bases: **ChatCompletionContext, Component[BufferedChatCompletionContextConfig]**

A buffered chat completion context that keeps a view of the last n messages, where n is the buffer size. The buffer size is set at initialization.

### Parameters :

*   **buffer_size** (*int*) – The size of the buffer.
*   **initial_messages** (*List[LLMMessage] | None*) – The initial messages.

### *classmethod* **_from_config** (*config : BufferedChatCompletionContextConfig*) → *Self* [source] #

Create a new instance of the component from a configuration object.

### Parameters :

*   **config** (*T*) – The configuration object.

### Returns :

*   **Self** – The new instance of the component.

### **_to_config** () → *BufferedChatCompletionContextConfig* [source] #

Dump the configuration that would be requisite to create a new instance of a component matching the configuration of this instance.

### Returns :

*   **T** – The configuration of the component.

### **component_config_schema** #

alias of **BufferedChatCompletionContextConfig**

### **component_provider_override**: *ClassVar[str | None]* = **'autogen_core.model_context.BufferedChatCompletionContext'** #

Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

### *async* **get_messages** () → *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]* [source] #

Get at most `buffer_size` recent messages.

## *class* **ChatCompletionContext** (*initial_messages* : *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]] | None = None) [source] #

Bases: **ABC, ComponentBase[BaseModel]**

An abstract base class for defining the interface of a chat completion context. A chat completion context lets agents store and retrieve LLM messages. It can be implemented with different recall strategies.

### Parameters :

*   **initial_messages** (*List[LLMMessage] | None*) – The initial messages.

### Example

To create a custom model context that filters out the thought field from AssistantMessage. This is useful for reasoning models like DeepSeek R1, which produces very long thought that is not needed for subsequent completions.

```python
from typing import List
from autogen_core.model_context import UnboundedChatCompletionContext
from autogen_core.models import AssistantMessage , LLMMessage

class ReasoningModelContext(UnboundedChatCompletionContext):
    """A model context for reasoning models."""
    async def get_messages(self) -> List[LLMMessage]:
        messages = await super().get_messages()
        # Filter out thought field from AssistantMessage.
        messages_out : List[LLMMessage] = []
        for message in messages :
            if isinstance(message , AssistantMessage):
                message.thought = None
            messages_out.append(message)
        return messages_out
```

### *async* **add_message** (*message* : *Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage *, FieldInfo(annotation=NoneType, required=True, discriminator='type')]*) → *None* [source] #

Add a message to the context.

### *async* **clear** () → *None* [source] #

Clear the context.

### **component_type** : *ClassVar[ComponentType]* = **'chat_completion_context'** #

The logical type of the component.

### *abstract async* **get_messages** () → *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]* [source] #

### *async* **load_state** (*state : Mapping[str, Any]*) → *None* [source] #

### *async* **save_state** () → *Mapping[str, Any]* [source] #

### *pydantic model* **ChatCompletionContextState** [source] #

Bases: **BaseModel**

### Show JSON schema

```json
{
    "title": "ChatCompletionContextState",
    "type": "object",
    "properties": {
        "messages": {
            "items": {
                "discriminator": {
                    "mapping": {
                        "AssistantMessage": "#/$defs/AssistantMessage",
                        "FunctionExecutionResultMessage": "#/$defs/FunctionExecutionResultMessage",
                        "SystemMessage": "#/$defs/SystemMessage",
                        "UserMessage": "#/$defs/UserMessage"
                    },
                    "propertyName": "type"
                },
                "oneOf": [
                    {
                        "$ref": "#/$defs/SystemMessage"
                    },
                    {
                        "$ref": "#/$defs/UserMessage"
                    },
                    {
                        "$ref": "#/$defs/AssistantMessage"
                    },
                    {
                        "$ref": "#/$defs/FunctionExecutionResultMessage"
                    }
                ]
            },
            "title": "Messages",
            "type": "array"
        }
    },
    "$defs": {
        "AssistantMessage": {
            "description": "Assistant message are sampled from the language model.",
            "properties": {
                "content": {
                    "anyOf": [
                        {
                            "type": "string"
                        },
                        {
                            "items": {
                                "$ref": "#/$defs/FunctionCall"
                            },
                            "type": "array"
                        }
                    ],
                    "title": "Content"
                },
                "thought": {
                    "anyOf": [
                        {
                            "type": "string"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": null,
                    "title": "Thought"
                },
                "source": {
                    "title": "Source",
                    "type": "string"
                },
                "type": {
                    "const": "AssistantMessage",
                    "default": "AssistantMessage",
                    "title": "Type",
                    "type": "string"
                }
            },
            "required": [
                "content",
                "source"
            ],
            "title": "AssistantMessage",
            "type": "object"
        },
        "FunctionCall": {
            "properties": {
                "id": {
                    "title": "Id",
                    "type": "string"
                },
                "arguments": {
                    "title": "Arguments",
                    "type": "string"
                },
                "name": {
                    "title": "Name",
                    "type": "string"
                }
            },
            "required": [
                "id",
                "arguments",
                "name"
            ],
            "title": "FunctionCall",
            "type": "object"
        },
        "FunctionExecutionResult": {
            "description": "Function execution result contains the output of a function call.",
            "properties": {
                "content": {
                    "title": "Content",
                    "type": "string"
                },
                "name": {
                    "title": "Name",
                    "type": "string"
                },
                "call_id": {
                    "title": "Call Id",
                    "type": "string"
                },
                "is_error": {
                    "anyOf": [
                        {
                            "type": "boolean"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": null,
                    "title": "Is Error"
                }
            },
            "required": [
                "content",
                "name",
                "call_id"
            ],
            "title": "FunctionExecutionResult",
            "type": "object"
        },
        "FunctionExecutionResultMessage": {
            "description": "Function execution result message contains the output of multiple function calls.",
            "properties": {
                "content": {
                    "items": {
                        "$ref": "#/$defs/FunctionExecutionResult"
                    },
                    "title": "Content",
                    "type": "array"
                },
                "type": {
                    "const": "FunctionExecutionResultMessage",
                    "default": "FunctionExecutionResultMessage",
                    "title": "Type",
                    "type": "string"
                }
            },
            "required": [
                "content"
            ],
            "title": "FunctionExecutionResultMessage",
            "type": "object"
        },
        "SystemMessage": {
            "description": "System message contains instructions for the model coming from the developer.\n\n.. note::\n\n Open AI is moving away from using 'system' role in favor of 'developer' role.\n See `Model Spec <https://cdn.openai.com/spec/model-spec-2024-05-08.html#definitions>`_ for more details.\n However, the 'system' role is still allowed in their API and will be automatically converted to 'developer' role\n on the server side.\n So, you can use `SystemMessage` for developer messages.",
            "properties": {
                "content": {
                    "title": "Content",
                    "type": "string"
                },
                "type": {
                    "const": "SystemMessage",
                    "default": "SystemMessage",
                    "title": "Type",
                    "type": "string"
                }
            },
            "required": [
                "content"
            ],
            "title": "SystemMessage",
            "type": "object"
        },
        "UserMessage": {
            "description": "User message contains input from end users, or a catch-all for data provided to the model.",
            "properties": {
                "content": {
                    "anyOf": [
                        {
                            "type": "string"
                        },
                        {
                            "items": {
                                "anyOf": [
                                    {
                                        "type": "string"
                                    },
                                    {}
                                ]
                            },
                            "type": "array"
                        }
                    ],
                    "title": "Content"
                },
                "source": {
                    "title": "Source",
                    "type": "string"
                },
                "type": {
                    "const": "UserMessage",
                    "default": "UserMessage",
                    "title": "Type",
                    "type": "string"
                }
            },
            "required": [
                "content",
                "source"
            ],
            "title": "UserMessage",
            "type": "object"
        }
    }
}
```

### Fields :

*   **messages** (*List[autogen_core.models._types.SystemMessage | autogen_core.models._types.UserMessage | autogen_core.models._types.AssistantMessage | autogen_core.models._types.FunctionExecutionResultMessage]*)

### *field* **messages**: *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage *, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]* [Optional] #

## *class* **HeadAndTailChatCompletionContext** (*head_size* : *int*, *tail_size* : *int*, *initial_messages* : *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]] | None = None) [source] #

Bases: **ChatCompletionContext, Component[HeadAndTailChatCompletionContextConfig]**

A chat completion context that keeps a view of the first n and last m messages, where n is the head size and m is the tail size. The head and tail sizes are set at initialization.

### Parameters :

*   **head_size** (*int*) – The size of the head.
*   **tail_size** (*int*) – The size of the tail.
*   **initial_messages** (*List[LLMMessage] | None*) – The initial messages.

### *classmethod* **_from_config** (*config : HeadAndTailChatCompletionContextConfig*) → *Self* [source] #

Create a new instance of the component from a configuration object.

### Parameters :

*   **config** (*T*) – The configuration object.

### Returns :

*   **Self** – The new instance of the component.

### **_to_config** () → *HeadAndTailChatCompletionContextConfig* [source] #

Dump the configuration that would be requisite to create a new instance of a component matching the configuration of this instance.

### Returns :

*   **T** – The configuration of the component.

### **component_config_schema** #

alias of **HeadAndTailChatCompletionContextConfig**

### **component_provider_override**: *ClassVar[str | None]* = **'autogen_core.model_context.HeadAndTailChatCompletionContext'** #

Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

### *async* **get_messages** () → *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]* [source] #

Get at most `head_size` recent messages and `tail_size` oldest messages.

## *class* **TokenLimitedChatCompletionContext** (*model_client* : *ChatCompletionClient*, ***, *token_limit* : *int | None = None*, *tool_schema* : *List[ToolSchema] | None = None*, *initial_messages* : *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]] | None = None) [source] #

Bases: **ChatCompletionContext, Component[TokenLimitedChatCompletionContextConfig]**

(Experimental) A token based chat completion context maintains a view of the context up to a token limit.

### Note

Added in v0.4.10. This is an experimental component and may change in the future.

### Parameters :

*   **model_client** (*ChatCompletionClient*) – The model client to use for token counting. The model client must implement the `count_tokens()` and `remaining_tokens()` methods.
*   **token_limit** (*int | None*) – The maximum number of tokens to keep in the context using the `count_tokens()` method. If None, the context will be limited by the model client using the `remaining_tokens()` method.
*   **tools** (*List[ToolSchema] | None*) – A list of tool schema to use in the context.
*   **initial_messages** (*List[LLMMessage] | None*) – A list of initial messages to include in the context.

### *classmethod* **_from_config** (*config : TokenLimitedChatCompletionContextConfig*) → *Self* [source] #

Create a new instance of the component from a configuration object.

### Parameters :

*   **config** (*T*) – The configuration object.

### Returns :

*   **Self** – The new instance of the component.

### **_to_config** () → *TokenLimitedChatCompletionContextConfig* [source] #

Dump the configuration that would be requisite to create a new instance of a component matching the configuration of this instance.

### Returns :

*   **T** – The configuration of the component.

### **component_config_schema** #

alias of **TokenLimitedChatCompletionContextConfig**

### **component_provider_override**: *ClassVar[str | None]* = **'autogen_core.model_context.TokenLimitedChatCompletionContext'** #

Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

### *async* **get_messages** () → *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]* [source] #

Get at most `token_limit` tokens in recent messages. If the token limit is not provided, then return as many messages as the remaining token allowed by the model client.

## *class* **UnboundedChatCompletionContext** (*initial_messages* : *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]] | None = None) [source] #

Bases: **ChatCompletionContext, Component[UnboundedChatCompletionContextConfig]**

An unbounded chat completion context that keeps a view of all the messages.

### *classmethod* **_from_config** (*config : UnboundedChatCompletionContextConfig*) → *Self* [source] #

Create a new instance of the component from a configuration object.

### Parameters :

*   **config** (*T*) – The configuration object.

### Returns :

*   **Self** – The new instance of the component.

### **_to_config** () → *UnboundedChatCompletionContextConfig* [source] #

Dump the configuration that would be requisite to create a new instance of a component matching the configuration of this instance.

### Returns :

*   **T** – The configuration of the component.

### **component_config_schema** #

alias of **UnboundedChatCompletionContextConfig**

### **component_provider_override**: *ClassVar[str | None]* = **'autogen_core.model_context.UnboundedChatCompletionContext'** #

Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

### *async* **get_messages** () → *List[Annotated[SystemMessage| UserMessage| AssistantMessage| FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]* [source] #

Get at most `buffer_size` recent messages.
