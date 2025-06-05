### `autogen_agentchat.messages`

This module defines various message types utilized for agent-to-agent communication. Each message type inherits either from the `BaseChatMessage` class or the `BaseAgentEvent` class, incorporating specific fields pertinent to the message being transmitted.

#### `AgentEvent`

The union type of all built-in concrete subclasses of `BaseAgentEvent`.
`alias of Annotated[ToolCallRequestEvent | ToolCallExecutionEvent | MemoryQueryEvent | UserInputRequestedEvent | ModelClientStreamingChunkEvent | ThoughtEvent | SelectSpeakerEvent | CodeGenerationEvent | CodeExecutionEvent, FieldInfo(annotation=NoneType, required=True, discriminator='type')]`

---

#### `BaseAgentEvent`

*pydantic model* `BaseAgentEvent` [source]
Bases: `BaseMessage`, `ABC`

This serves as the base class for agent events.

**Note**: If the intent is to create a new message type for signaling observable events to a user and application, inheritance from this class is required. Agent events are specifically designed to signal actions and thoughts produced by agents and teams to users and applications. They are not intended for agent-to-agent communication and are not expected to be processed by other agents. To provide a custom rendering of the content, the `to_text()` method should be overridden.

Show JSON schema
```json
{
  "title": "BaseAgentEvent",
  "description": "Base class for agent events.\n\n.. note::\n\n If you want to create a new message type for signaling observable events\n to user and application, inherit from this class.\n\nAgent events are used to signal actions and thoughts produced by agents\nand teams to user and applications. They are not used for agent-to-agent\ncommunication and are not expected to be processed by other agents.\n\nYou should override the :meth:`to_text` method if you want to provide\na custom rendering of the content.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source"
  ]
}
```


**Fields**:
*   `metadata` (`Dict[str, str]`)
    *field* `metadata`: `Dict[str, str]` = `{}`
    Additional metadata concerning the message.
*   `models_usage` (`autogen_core.models._types.RequestUsage | None`)
    *field* `models_usage`: `RequestUsage | None` = `None`
    The model client usage incurred during the production of this message.
*   `source` (`str`)
    *field* `source`: `str` [*Required*]
    The name of the agent that dispatched this message.

---

#### `BaseChatMessage`

*pydantic model* `BaseChatMessage` [source]
Bases: `BaseMessage`, `ABC`

This is an abstract base class designated for chat messages.

**Note**: To establish a new message type intended for agent-to-agent communication, one should inherit from this class. Alternatively, if the content type is a subclass of Pydantic `BaseModel`, `StructuredMessage` can be directly utilized.

This class specifically handles messages exchanged between agents within a chat conversation. Agents are expected to process the message content using models and subsequently return a response as another `BaseChatMessage`.

Show JSON schema
```json
{
  "title": "BaseChatMessage",
  "description": "Abstract base class for chat messages.\n\n.. note::\n\n If you want to create a new message type that is used for agent-to-agent\n communication, inherit from this class, or simply use\n :class:`StructuredMessage` if your content type is a subclass of\n Pydantic BaseModel.\n\nThis class is used for messages that are sent between agents in a chat\nconversation. Agents are expected to process the content of the\nmessage using models and return a response as another :class:`BaseChatMessage`.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source"
  ]
}
```


**Fields**:
*   `metadata` (`Dict[str, str]`)
    *field* `metadata`: `Dict[str, str]` = `{}`
    Additional metadata concerning the message.
*   `models_usage` (`autogen_core.models._types.RequestUsage | None`)
    *field* `models_usage`: `RequestUsage | None` = `None`
    The model client usage incurred during the production of this message.
*   `source` (`str`)
    *field* `source`: `str` [*Required*]
    The name of the agent that dispatched this message.

*abstract* `to_model_message` ( ) → `UserMessage` [source]
Converts the message content into a `UserMessage` suitable for use with a model client, such as `ChatCompletionClient`.

*abstract* `to_model_text` ( ) → `str` [source]
Converts the message content into a text-only representation, which is utilized for constructing text-only content for models. This method is not employed for rendering the message in the console; for that purpose, `to_text()` should be used. The distinction between `to_model_text()` and `to_model_message()` lies in their application: `to_model_text()` is used to construct parts of a message for the model client, whereas `to_model_message()` generates a complete message for the model client.

---

#### `BaseMessage`

*pydantic model* `BaseMessage` [source]
Bases: `BaseModel`, `ABC`

This serves as the abstract base class for all message types within `AgentChat`.

**Warning**: It is crucial not to inherit directly from this class when creating a new message type. Instead, inheritance should be from `BaseChatMessage` or `BaseAgentEvent` to clearly define the message type's purpose.

Show JSON schema
```json
{
  "title": "BaseMessage",
  "description": "Abstract base class for all message types in AgentChat.\n\n.. warning::\n\n If you want to create a new message type, do not inherit from this class.\n Instead, inherit from :class:`BaseChatMessage` or :class:`BaseAgentEvent`\n to clarify the purpose of the message type.",
  "type": "object",
  "properties": {}
}
```


`dump` ( ) → `Mapping[str, Any]` [source]
Converts the message into a JSON-serializable dictionary. The default implementation leverages the Pydantic model’s `model_dump()` method for this conversion. This method can be overridden to customize the serialization process or to incorporate additional fields into the output.

*classmethod* `load` (`data`: `Mapping[str, Any]`) → `Self` [source]
Constructs a message from a dictionary of JSON-serializable data. The default implementation utilizes the Pydantic model’s `model_validate()` method to create the message from the provided data. This method can be overridden to customize the deserialization process or to integrate additional fields into the input data.

*abstract* `to_text` ( ) → `str` [source]
Converts the message content into a string-only representation, suitable for rendering in the console and for inspection by the user or conditions. This method is not used for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `BaseTextChatMessage`

*pydantic model* `BaseTextChatMessage` [source]
Bases: `BaseChatMessage`, `ABC`

This is the base class for all text-only `BaseChatMessage` types. It provides implementations for the `to_text()`, `to_model_text()`, and `to_model_message()` methods.

Inherit from this class if your message content type is a string.

Show JSON schema
```json
{
  "title": "BaseTextChatMessage",
  "description": "Base class for all text-only :class:`BaseChatMessage` types.\nIt has implementations for :meth:`to_text`, :meth:`to_model_text`,\nand :meth:`to_model_message` methods.\n\nInherit from this class if your message content type is a string.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "title": "Content",
      "type": "string"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `content` (`str`)
    *field* `content`: `str` [*Required*]
    The content of the message.

`to_model_message` ( ) → `UserMessage` [source]
Converts the message content to a `UserMessage` for interaction with a model client, such as `ChatCompletionClient`.

`to_model_text` ( ) → `str` [source]
Converts the content of the message to a text-only representation, used specifically for creating text-only content for models. This method is not for rendering the message in the console; for that, `to_text()` is utilized. The distinction between this and `to_model_message()` is that `to_model_text()` constructs parts of a message for the model client, whereas `to_model_message()` generates a complete message for the model client.

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be used instead.

---

#### `ChatMessage`

The union type of all built-in concrete subclasses of `BaseChatMessage`. This type specifically excludes `StructuredMessage` types.
`alias of Annotated[TextMessage | MultiModalMessage | StopMessage | ToolCallSummaryMessage | HandoffMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]`

---

#### `CodeExecutionEvent`

*pydantic model* `CodeExecutionEvent` [source]
Bases: `BaseAgentEvent`

An event designed to signal a code execution event.

Show JSON schema
```json
{
  "title": "CodeExecutionEvent",
  "description": "An event signaling code execution event.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "retry_attempt": {
      "title": "Retry Attempt",
      "type": "integer"
    },
    "result": {
      "$ref": "#/$defs/CodeResult"
    },
    "type": {
      "const": "CodeExecutionEvent",
      "default": "CodeExecutionEvent",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "CodeResult": {
      "properties": {
        "exit_code": {
          "title": "Exit Code",
          "type": "integer"
        },
        "output": {
          "title": "Output",
          "type": "string"
        }
      },
      "required": [
        "exit_code",
        "output"
      ],
      "title": "CodeResult",
      "type": "object"
    },
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "retry_attempt",
    "result"
  ]
}
```


**Fields**:
*   `result` (`autogen_core.code_executor._base.CodeResult`)
    *field* `result`: `CodeResult` [*Required*]
    The result of code execution.
*   `retry_attempt` (`int`)
    *field* `retry_attempt`: `int` [*Required*]
    The retry number, where `0` indicates the first execution.
*   `type` (`Literal['CodeExecutionEvent']`)
    *field* `type`: `Literal['CodeExecutionEvent']` = `'CodeExecutionEvent'`

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `CodeGenerationEvent`

*pydantic model* `CodeGenerationEvent` [source]
Bases: `BaseAgentEvent`

An event designed to signal a code generation event.

Show JSON schema
```json
{
  "title": "CodeGenerationEvent",
  "description": "An event signaling code generation event.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "retry_attempt": {
      "title": "Retry Attempt",
      "type": "integer"
    },
    "content": {
      "title": "Content",
      "type": "string"
    },
    "code_blocks": {
      "items": {
        "$ref": "#/$defs/CodeBlock"
      },
      "title": "Code Blocks",
      "type": "array"
    },
    "type": {
      "const": "CodeGenerationEvent",
      "default": "CodeGenerationEvent",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "CodeBlock": {
      "properties": {
        "code": {
          "title": "Code",
          "type": "string"
        },
        "language": {
          "title": "Language",
          "type": "string"
        }
      },
      "required": [
        "code",
        "language"
      ],
      "title": "CodeBlock",
      "type": "object"
    },
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "retry_attempt",
    "content",
    "code_blocks"
  ]
}
```


**Fields**:
*   `code_blocks` (`List[autogen_core.code_executor._base.CodeBlock]`)
    *field* `code_blocks`: `List[CodeBlock]` [*Required*]
    A list containing all code blocks present within the content.
*   `content` (`str`)
    *field* `content`: `str` [*Required*]
    The complete content as a string.
*   `retry_attempt` (`int`)
    *field* `retry_attempt`: `int` [*Required*]
    The retry number, where `0` signifies the first generation attempt.
*   `type` (`Literal['CodeGenerationEvent']`)
    *field* `type`: `Literal['CodeGenerationEvent']` = `'CodeGenerationEvent'`

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `HandoffMessage`

*pydantic model* `HandoffMessage` [source]
Bases: `BaseTextChatMessage`

A message designed to request the handoff of a conversation to another agent.

Show JSON schema
```json
{
  "title": "HandoffMessage",
  "description": "A message requesting handoff of a conversation to another agent.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "title": "Content",
      "type": "string"
    },
    "target": {
      "title": "Target",
      "type": "string"
    },
    "context": {
      "default": [],
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
      "title": "Context",
      "type": "array"
    },
    "type": {
      "const": "HandoffMessage",
      "default": "HandoffMessage",
      "title": "Type",
      "type": "string"
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
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
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
  },
  "required": [
    "source",
    "content",
    "target"
  ]
}
```


**Fields**:
*   `context` (`List[Annotated[autogen_core.models._types.SystemMessage | autogen_core.models._types.UserMessage | autogen_core.models._types.AssistantMessage | autogen_core.models._types.FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]`)
    *field* `context`: `List[Annotated[SystemMessage | UserMessage | AssistantMessage | FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]` = `[]`
    The model context intended to be passed to the target agent.
*   `target` (`str`)
    *field* `target`: `str` [*Required*]
    The name of the specific target agent to which the conversation should be handed off.
*   `type` (`Literal['HandoffMessage']`)
    *field* `type`: `Literal['HandoffMessage']` = `'HandoffMessage'`

---

#### `MemoryQueryEvent`

*pydantic model* `MemoryQueryEvent` [source]
Bases: `BaseAgentEvent`

An event signaling the results of memory queries.

Show JSON schema
```json
{
  "title": "MemoryQueryEvent",
  "description": "An event signaling the results of memory queries.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "items": {
        "$ref": "#/$defs/MemoryContent"
      },
      "title": "Content",
      "type": "array"
    },
    "type": {
      "const": "MemoryQueryEvent",
      "default": "MemoryQueryEvent",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "MemoryContent": {
      "description": "A memory content item.",
      "properties": {
        "content": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "format": "binary",
              "type": "string"
            },
            {
              "type": "object"
            },
            {}
          ],
          "title": "Content"
        },
        "mime_type": {
          "anyOf": [
            {
              "$ref": "#/$defs/MemoryMimeType"
            },
            {
              "type": "string"
            }
          ],
          "title": "Mime Type"
        },
        "metadata": {
          "anyOf": [
            {
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Metadata"
        }
      },
      "required": [
        "content",
        "mime_type"
      ],
      "title": "MemoryContent",
      "type": "object"
    },
    "MemoryMimeType": {
      "description": "Supported MIME types for memory content.",
      "enum": [
        "text/plain",
        "application/json",
        "text/markdown",
        "image/*",
        "application/octet-stream"
      ],
      "title": "MemoryMimeType",
      "type": "string"
    },
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `content` (`List[autogen_core.memory._base_memory.MemoryContent]`)
    *field* `content`: `List[MemoryContent]` [*Required*]
    The results obtained from the memory query.
*   `type` (`Literal['MemoryQueryEvent']`)
    *field* `type`: `Literal['MemoryQueryEvent']` = `'MemoryQueryEvent'`

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `ModelClientStreamingChunkEvent`

*pydantic model* `ModelClientStreamingChunkEvent` [source]
Bases: `BaseAgentEvent`

An event designed to signal a text output chunk originating from a model client in streaming mode.

Show JSON schema
```json
{
  "title": "ModelClientStreamingChunkEvent",
  "description": "An event signaling a text output chunk from a model client in streaming mode.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "title": "Content",
      "type": "string"
    },
    "type": {
      "const": "ModelClientStreamingChunkEvent",
      "default": "ModelClientStreamingChunkEvent",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `content` (`str`)
    *field* `content`: `str` [*Required*]
    A string chunk received from the model client.
*   `type` (`Literal['ModelClientStreamingChunkEvent']`)
    *field* `type`: `Literal['ModelClientStreamingChunkEvent']` = `'ModelClientStreamingChunkEvent'`

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `MultiModalMessage`

*pydantic model* `MultiModalMessage` [source]
Bases: `BaseChatMessage`

A message designed to carry multimodal content.

Show JSON schema
```json
{
  "title": "MultiModalMessage",
  "description": "A multimodal message.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "items": {
        "anyOf": [
          {
            "type": "string"
          },
          {}
        ]
      },
      "title": "Content",
      "type": "array"
    },
    "type": {
      "const": "MultiModalMessage",
      "default": "MultiModalMessage",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `content` (`List[str | autogen_core._image.Image]`)
    *field* `content`: `List[str | Image]` [*Required*]
    The content of the message.
*   `type` (`Literal['MultiModalMessage']`)
    *field* `type`: `Literal['MultiModalMessage']` = `'MultiModalMessage'`

`to_model_message` ( ) → `UserMessage` [source]
Converts the message content to a `UserMessage` for interaction with a model client, such as `ChatCompletionClient`.

`to_model_text` (`image_placeholder`: `str | None` = `'[image]'`) → `str` [source]
Converts the message content into a string-only representation. If an image is present, it will be replaced by the image placeholder by default; otherwise, if set to `None`, it will be represented as a base64 string.

`to_text` (`iterm`: `bool` = `False`) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `SelectSpeakerEvent`

*pydantic model* `SelectSpeakerEvent` [source]
Bases: `BaseAgentEvent`

An event designed to signal the selection of speakers for a conversation.

Show JSON schema
```json
{
  "title": "SelectSpeakerEvent",
  "description": "An event signaling the selection of speakers for a conversation.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "items": {
        "type": "string"
      },
      "title": "Content",
      "type": "array"
    },
    "type": {
      "const": "SelectSpeakerEvent",
      "default": "SelectSpeakerEvent",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `content` (`List[str]`)
    *field* `content`: `List[str]` [*Required*]
    The names of the selected speakers.
*   `type` (`Literal['SelectSpeakerEvent']`)
    *field* `type`: `Literal['SelectSpeakerEvent']` = `'SelectSpeakerEvent'`

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `StopMessage`

*pydantic model* `StopMessage` [source]
Bases: `BaseTextChatMessage`

A message designed to request the cessation of a conversation.

Show JSON schema
```json
{
  "title": "StopMessage",
  "description": "A message requesting stop of a conversation.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "title": "Content",
      "type": "string"
    },
    "type": {
      "const": "StopMessage",
      "default": "StopMessage",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `type` (`Literal['StopMessage']`)
    *field* `type`: `Literal['StopMessage']` = `'StopMessage'`

---

#### `StructuredContentType`

Type variable for structured content types.
`alias of TypeVar('StructuredContentType', bound=BaseModel, covariant=True)`

---

#### `StructuredMessage`

*pydantic model* `StructuredMessage` [source]
Bases: `BaseChatMessage`, `Generic[StructuredContentType]`

A `BaseChatMessage` type with an unspecified content type. To create a new structured message type, the content type must be specified as a subclass of Pydantic `BaseModel`.

```python
from pydantic import BaseModel
from autogen_agentchat.messages import StructuredMessage

class MyMessageContent(BaseModel):
    text: str
    number: int

message = StructuredMessage[MyMessageContent](
    content=MyMessageContent(text="Hello", number=42),
    source="agent1",
)

print(message.to_text()) # {"text": "Hello", "number": 42}
```


```python
from pydantic import BaseModel
from autogen_agentchat.messages import StructuredMessage

class MyMessageContent(BaseModel):
    text: str
    number: int

message = StructuredMessage[MyMessageContent](
    content=MyMessageContent(text="Hello", number=42),
    source="agent",
    format_string="Hello, {text} {number}!",
)

print(message.to_text()) # Hello, agent 42!
```


Show JSON schema
```json
{
  "title": "StructuredMessage",
  "description": "A :class:`BaseChatMessage` type with an unspecified content type.\n\nTo create a new structured message type, specify the content type\nas a subclass of `Pydantic BaseModel <https://docs.pydantic.dev/latest/concepts/models/>`_.\n\n.. code-block:: python\n\n from pydantic import BaseModel\n from autogen_agentchat.messages import StructuredMessage\n\n\n class MyMessageContent(BaseModel):\n text: str\n number: int\n\n\n message = StructuredMessage[MyMessageContent](\n content=MyMessageContent(text=\"Hello\", number=42),\n source=\"agent1\",\n )\n\n print(message.to_text()) # {\"text\": \"Hello\", \"number\": 42}\n\n.. code-block:: python\n\n from pydantic import BaseModel\n from autogen_agentchat.messages import StructuredMessage\n\n\n class MyMessageContent(BaseModel):\n text: str\n number: int\n\n\n message = StructuredMessage[MyMessageContent](\n content=MyMessageContent(text=\"Hello\", number=42),\n source=\"agent\",\n format_string=\"Hello, {text} {number}!\",\n )\n\n print(message.to_text()) # Hello, agent 42!",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "$ref": "#/$defs/BaseModel"
    },
    "format_string": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Format String"
    }
  },
  "$defs": {
    "BaseModel": {
      "properties": {},
      "title": "BaseModel",
      "type": "object"
    },
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `content` (`autogen_agentchat.messages.StructuredContentType`)
    *field* `content`: `StructuredContentType` [*Required*]
    The content of the message, which must be a subclass of Pydantic `BaseModel`.
*   `format_string` (`str | None`)
    *field* `format_string`: `str | None` = `None`
    (Experimental) An optional format string for rendering the content into a human-readable format. This string can leverage fields of the content model as placeholders (e.g., `{name}` for a `name` field). The `to_text()` method uses this format string to create a human-readable representation of the message. This setting is experimental and is subject to future changes.

`to_model_message` ( ) → `UserMessage` [source]
Converts the message content to a `UserMessage` for use with a model client, such as `ChatCompletionClient`.

`to_model_text` ( ) → `str` [source]
Converts the content of the message to a text-only representation, utilized for creating text-only content for models. This method is not for rendering the message in the console; for that, `to_text()` is employed. The distinction between this and `to_model_message()` is that this method constructs parts of a message for the model client, while `to_model_message()` creates a complete message for the model client.

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

*property* `type`: `str`

---

#### `TextMessage`

*pydantic model* `TextMessage` [source]
Bases: `BaseTextChatMessage`

A message type featuring string-only content.

Show JSON schema
```json
{
  "title": "TextMessage",
  "description": "A text message with string-only content.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "title": "Content",
      "type": "string"
    },
    "type": {
      "const": "TextMessage",
      "default": "TextMessage",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `type` (`Literal['TextMessage']`)
    *field* `type`: `Literal['TextMessage']` = `'TextMessage'`

---

#### `ThoughtEvent`

*pydantic model* `ThoughtEvent` [source]
Bases: `BaseAgentEvent`

An event signaling the thought process of a model. This is used to convey reasoning tokens generated by a reasoning model or additional text content produced by a function call.

Show JSON schema
```json
{
  "title": "ThoughtEvent",
  "description": "An event signaling the thought process of a model.\nIt is used to communicate the reasoning tokens generated by a reasoning model,\nor the extra text content generated by a function call.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "title": "Content",
      "type": "string"
    },
    "type": {
      "const": "ThoughtEvent",
      "default": "ThoughtEvent",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `content` (`str`)
    *field* `content`: `str` [*Required*]
    The thought process output of the model.
*   `type` (`Literal['ThoughtEvent']`)
    *field* `type`: `Literal['ThoughtEvent']` = `'ThoughtEvent'`

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `ToolCallExecutionEvent`

*pydantic model* `ToolCallExecutionEvent` [source]
Bases: `BaseAgentEvent`

An event signaling the execution of tool calls.

Show JSON schema
```json
{
  "title": "ToolCallExecutionEvent",
  "description": "An event signaling the execution of tool calls.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "items": {
        "$ref": "#/$defs/FunctionExecutionResult"
      },
      "title": "Content",
      "type": "array"
    },
    "type": {
      "const": "ToolCallExecutionEvent",
      "default": "ToolCallExecutionEvent",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
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
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `content` (`List[autogen_core.models._types.FunctionExecutionResult]`)
    *field* `content`: `List[FunctionExecutionResult]` [*Required*]
    The results obtained from the tool calls.
*   `type` (`Literal['ToolCallExecutionEvent']`)
    *field* `type`: `Literal['ToolCallExecutionEvent']` = `'ToolCallExecutionEvent'`

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `ToolCallRequestEvent`

*pydantic model* `ToolCallRequestEvent` [source]
Bases: `BaseAgentEvent`

An event signaling a request to utilize tools.

Show JSON schema
```json
{
  "title": "ToolCallRequestEvent",
  "description": "An event signaling a request to use tools.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "items": {
        "$ref": "#/$defs/FunctionCall"
      },
      "title": "Content",
      "type": "array"
    },
    "type": {
      "const": "ToolCallRequestEvent",
      "default": "ToolCallRequestEvent",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
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
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `content` (`List[autogen_core._types.FunctionCall]`)
    *field* `content`: `List[FunctionCall]` [*Required*]
    The specific tool calls.
*   `type` (`Literal['ToolCallRequestEvent']`)
    *field* `type`: `Literal['ToolCallRequestEvent']` = `'ToolCallRequestEvent'`

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.

---

#### `ToolCallSummaryMessage`

*pydantic model* `ToolCallSummaryMessage` [source]
Bases: `BaseTextChatMessage`

A message designed to signal the summary of tool call results.

Show JSON schema
```json
{
  "title": "ToolCallSummaryMessage",
  "description": "A message signaling the summary of tool call results.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "content": {
      "title": "Content",
      "type": "string"
    },
    "type": {
      "const": "ToolCallSummaryMessage",
      "default": "ToolCallSummaryMessage",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "content"
  ]
}
```


**Fields**:
*   `type` (`Literal['ToolCallSummaryMessage']`)
    *field* `type`: `Literal['ToolCallSummaryMessage']` = `'ToolCallSummaryMessage'`

---

#### `UserInputRequestedEvent`

*pydantic model* `UserInputRequestedEvent` [source]
Bases: `BaseAgentEvent`

An event signaling that the user proxy has requested user input. This event is published prior to invoking the input callback.

Show JSON schema
```json
{
  "title": "UserInputRequestedEvent",
  "description": "An event signaling a that the user proxy has requested user input. Published prior to invoking the input callback.",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "models_usage": {
      "anyOf": [
        {
          "$ref": "#/$defs/RequestUsage"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "metadata": {
      "additionalProperties": {
        "type": "string"
      },
      "default": {},
      "title": "Metadata",
      "type": "object"
    },
    "request_id": {
      "title": "Request Id",
      "type": "string"
    },
    "content": {
      "const": "",
      "default": "",
      "title": "Content",
      "type": "string"
    },
    "type": {
      "const": "UserInputRequestedEvent",
      "default": "UserInputRequestedEvent",
      "title": "Type",
      "type": "string"
    }
  },
  "$defs": {
    "RequestUsage": {
      "properties": {
        "prompt_tokens": {
          "title": "Prompt Tokens",
          "type": "integer"
        },
        "completion_tokens": {
          "title": "Completion Tokens",
          "type": "integer"
        }
      },
      "required": [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title": "RequestUsage",
      "type": "object"
    }
  },
  "required": [
    "source",
    "request_id"
  ]
}
```


**Fields**:
*   `content` (`Literal['']`)
    *field* `content`: `Literal['']` = `''`
    Empty content for compatibility with consumers that expect a content field.
*   `request_id` (`str`)
    *field* `request_id`: `str` [*Required*]
    An identifier for the user input request.
*   `type` (`Literal['UserInputRequestedEvent']`)
    *field* `type`: `Literal['UserInputRequestedEvent']` = `'UserInputRequestedEvent'`

`to_text` ( ) → `str` [source]
Converts the message content into a string-only representation that can be displayed in the console and examined by the user or conditions. This method is not for generating text-only content for models; for `BaseChatMessage` types, `to_model_text()` should be employed instead.