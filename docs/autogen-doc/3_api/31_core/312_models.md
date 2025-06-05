# `autogen_core.models`

*   `pydantic model` **AssistantMessage**[source]
    *   Bases: `BaseModel`

    Assistant messages are sampled from the language model.

    Show JSON schema
    ```json
    {
      "title": "AssistantMessage",
      "description": "Assistant message are sampled from the language model.",
      "type": "object",
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
        }
      },
      "required": [
        "content",
        "source"
      ]
    }
    ```

    Fields:
    *   `content` (`str` | `List[autogen_core._types.FunctionCall]`)
        *   `field` `content`: `str` | `List[FunctionCall]` **[Required]** # The content of the message.
    *   `source` (`str`)
        *   `field` `source`: `str` **[Required]** # The name of the agent that sent this message.
    *   `thought` (`str` | `None`)
        *   `field` `thought`: `str` | `None` = `None` # The reasoning text for the completion if available. Used for reasoning model and additional text content besides function calls.
    *   `type` (`Literal['AssistantMessage']`)
        *   `field` `type`: `Literal['AssistantMessage']` = `'AssistantMessage'`

*   `class` **ChatCompletionClient**[source]
    *   Bases: `ComponentBase[BaseModel]`, `ABC`

    *   `abstract` **actual_usage**() → `RequestUsage`[source]
    *   `abstract property` **capabilities**: `ModelCapabilities`
    *   `abstract async` **close**() → `None`[source]
    *   `abstract` **count_tokens**(messages : `Sequence[Annotated[SystemMessage|UserMessage|AssistantMessage|FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]`, \*, tools : `Sequence[Tool|ToolSchema]` = `[]`) → `int`[source]
    *   `abstract async` **create**(messages : `Sequence[Annotated[SystemMessage|UserMessage|AssistantMessage|FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]`, \*, tools : `Sequence[Tool|ToolSchema]` = `[]`, json_output : `bool|type[BaseModel]|None` = `None`, extra_create_args : `Mapping[str, Any]` = `{}`, cancellation_token : `CancellationToken|None` = `None`) → `CreateResult`[source]
        Creates a single response from the model.

        Parameters:
        *   **messages** (`Sequence[LLMMessage]`) – The messages to send to the model.
        *   **tools** (`Sequence[Tool|ToolSchema]`, *optional*) – The tools to use with the model. Defaults to `[]`.
        *   **json_output** (`Optional[bool|type[BaseModel]]`, *optional*) – Whether to use JSON mode, structured output, or neither. Defaults to `None`. If set to a Pydantic `BaseModel` type, it will be used as the output type for structured output. If set to a boolean, it will be used to determine whether to use JSON mode or not. If set to `True`, make sure to instruct the model to produce JSON output in the instruction or prompt.
        *   **extra_create_args** (`Mapping[str, Any]`, *optional*) – Extra arguments to pass to the underlying client. Defaults to `{}`.
        *   **cancellation_token** (`Optional[CancellationToken]`, *optional*) – A token for cancellation. Defaults to `None`.

        Returns:
        *   **CreateResult** – The result of the model call.

    *   `abstract async` **create_stream**(messages : `Sequence[Annotated[SystemMessage|UserMessage|AssistantMessage|FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]`, \*, tools : `Sequence[Tool|ToolSchema]` = `[]`, json_output : `bool|type[BaseModel]|None` = `None`, extra_create_args : `Mapping[str, Any]` = `{}`, cancellation_token : `CancellationToken|None` = `None`) → `AsyncGenerator[str|CreateResult, None]`[source]
        Creates a stream of string chunks from the model ending with a `CreateResult`.

        Parameters:
        *   **messages** (`Sequence[LLMMessage]`) – The messages to send to the model.
        *   **tools** (`Sequence[Tool|ToolSchema]`, *optional*) – The tools to use with the model. Defaults to `[]`.
        *   **json_output** (`Optional[bool|type[BaseModel]]`, *optional*) – Whether to use JSON mode, structured output, or neither. Defaults to `None`. If set to a Pydantic `BaseModel` type, it will be used as the output type for structured output. If set to a boolean, it will be used to determine whether to use JSON mode or not. If set to `True`, make sure to instruct the model to produce JSON output in the instruction or prompt.
        *   **extra_create_args** (`Mapping[str, Any]`, *optional*) – Extra arguments to pass to the underlying client. Defaults to `{}`.
        *   **cancellation_token** (`Optional[CancellationToken]`, *optional*) – A token for cancellation. Defaults to `None`.

        Returns:
        *   **AsyncGenerator[Union[str, CreateResult], None]** – A generator that yields string chunks and ends with a `CreateResult`.

    *   `abstract property` **model_info**: `ModelInfo`
    *   `abstract` **remaining_tokens**(messages : `Sequence[Annotated[SystemMessage|UserMessage|AssistantMessage|FunctionExecutionResultMessage, FieldInfo(annotation=NoneType, required=True, discriminator='type')]]`, \*, tools : `Sequence[Tool|ToolSchema]` = `[]`) → `int`[source]
    *   `abstract` **total_usage**() → `RequestUsage`[source]

*   `pydantic model` **ChatCompletionTokenLogprob**[source]
    *   Bases: `BaseModel`

    Show JSON schema
    ```json
    {
      "title": "ChatCompletionTokenLogprob",
      "type": "object",
      "properties": {
        "token": {
          "title": "Token",
          "type": "string"
        },
        "logprob": {
          "title": "Logprob",
          "type": "number"
        },
        "top_logprobs": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/TopLogprob"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Top Logprobs"
        },
        "bytes": {
          "anyOf": [
            {
              "items": {
                "type": "integer"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Bytes"
        }
      },
      "$defs": {
        "TopLogprob": {
          "properties": {
            "logprob": {
              "title": "Logprob",
              "type": "number"
            },
            "bytes": {
              "anyOf": [
                {
                  "items": {
                    "type": "integer"
                  },
                  "type": "array"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Bytes"
            }
          },
          "required": [
            "logprob"
          ],
          "title": "TopLogprob",
          "type": "object"
        }
      },
      "required": [
        "token",
        "logprob"
      ]
    }
    ```

    Fields:
    *   `bytes` (`List[int]` | `None`)
        *   `field` `bytes`: `List[int]` | `None` = `None`
    *   `logprob` (`float`)
        *   `field` `logprob`: `float` **[Required]**
    *   `token` (`str`)
        *   `field` `token`: `str` **[Required]**
    *   `top_logprobs` (`List[autogen_core.models._types.TopLogprob]` | `None`)
        *   `field` `top_logprobs`: `List[TopLogprob]` | `None` = `None`

*   `pydantic model` **CreateResult**[source]
    *   Bases: `BaseModel`

    `CreateResult` contains the output of a model completion.

    Show JSON schema
    ```json
    {
      "title": "CreateResult",
      "description": "Create result contains the output of a model completion.",
      "type": "object",
      "properties": {
        "finish_reason": {
          "enum": [
            "stop",
            "length",
            "function_calls",
            "content_filter",
            "unknown"
          ],
          "title": "Finish Reason",
          "type": "string"
        },
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
        "usage": {
          "$ref": "#/$defs/RequestUsage"
        },
        "cached": {
          "title": "Cached",
          "type": "boolean"
        },
        "logprobs": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/ChatCompletionTokenLogprob"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Logprobs"
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
        }
      },
      "$defs": {
        "ChatCompletionTokenLogprob": {
          "properties": {
            "token": {
              "title": "Token",
              "type": "string"
            },
            "logprob": {
              "title": "Logprob",
              "type": "number"
            },
            "top_logprobs": {
              "anyOf": [
                {
                  "items": {
                    "$ref": "#/$defs/TopLogprob"
                  },
                  "type": "array"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Top Logprobs"
            },
            "bytes": {
              "anyOf": [
                {
                  "items": {
                    "type": "integer"
                  },
                  "type": "array"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Bytes"
            }
          },
          "required": [
            "token",
            "logprob"
          ],
          "title": "ChatCompletionTokenLogprob",
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
        "TopLogprob": {
          "properties": {
            "logprob": {
              "title": "Logprob",
              "type": "number"
            },
            "bytes": {
              "anyOf": [
                {
                  "items": {
                    "type": "integer"
                  },
                  "type": "array"
                },
                {
                  "type": "null"
                }
              ],
              "default": null,
              "title": "Bytes"
            }
          },
          "required": [
            "logprob"
          ],
          "title": "TopLogprob",
          "type": "object"
        }
      },
      "required": [
        "finish_reason",
        "content",
        "usage",
        "cached"
      ]
    }
    ```

    Fields:
    *   `cached` (`bool`)
        *   `field` `cached`: `bool` **[Required]** # Whether the completion was generated from a cached response.
    *   `content` (`str` | `List[autogen_core._types.FunctionCall]`)
        *   `field` `content`: `str` | `List[FunctionCall]` **[Required]** # The output of the model completion.
    *   `finish_reason` (`Literal['stop', 'length', 'function_calls', 'content_filter', 'unknown']`)
        *   `field` `finish_reason`: `Literal['stop', 'length', 'function_calls', 'content_filter', 'unknown']` **[Required]** # The reason the model finished generating the completion.
    *   `logprobs` (`List[autogen_core.models._types.ChatCompletionTokenLogprob]` | `None`)
        *   `field` `logprobs`: `List[ChatCompletionTokenLogprob]` | `None` = `None` # The logprobs of the tokens in the completion.
    *   `thought` (`str` | `None`)
        *   `field` `thought`: `str` | `None` = `None` # The reasoning text for the completion if available. Used for reasoning models and additional text content besides function calls.
    *   `usage` (`autogen_core.models._types.RequestUsage`)
        *   `field` `usage`: `RequestUsage` **[Required]** # The usage of tokens in the prompt and completion.

*   `pydantic model` **FunctionExecutionResult**[source]
    *   Bases: `BaseModel`

    `FunctionExecutionResult` contains the output of a function call.

    Show JSON schema
    ```json
    {
      "title": "FunctionExecutionResult",
      "description": "Function execution result contains the output of a function call.",
      "type": "object",
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
      ]
    }
    ```

    Fields:
    *   `call_id` (`str`)
        *   `field` `call_id`: `str` **[Required]** # The ID of the function call. Note this ID may be empty for some models.
    *   `content` (`str`)
        *   `field` `content`: `str` **[Required]** # The output of the function call.
    *   `is_error` (`bool` | `None`)
        *   `field` `is_error`: `bool` | `None` = `None` # Whether the function call resulted in an error.
    *   `name` (`str`)
        *   `field` `name`: `str` **[Required]** # (New in v0.4.8) The name of the function that was called.

*   `pydantic model` **FunctionExecutionResultMessage**[source]
    *   Bases: `BaseModel`

    `FunctionExecutionResultMessage` contains the output of multiple function calls.

    Show JSON schema
    ```json
    {
      "title": "FunctionExecutionResultMessage",
      "description": "Function execution result message contains the output of multiple function calls.",
      "type": "object",
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
        }
      },
      "required": [
        "content"
      ]
    }
    ```

    Fields:
    *   `content` (`List[autogen_core.models._types.FunctionExecutionResult]`)
        *   `field` `content`: `List[FunctionExecutionResult]` **[Required]**
    *   `type` (`Literal['FunctionExecutionResultMessage']`)
        *   `field` `type`: `Literal['FunctionExecutionResultMessage']` = `'FunctionExecutionResultMessage'`

*   `class` **ModelCapabilities**(*\*\*kwargs*) [source]
    *   Bases: `TypedDict`
    *   `function_calling`: **[Required]**`[bool]`
    *   `json_output`: **[Required]**`[bool]`
    *   `vision`: **[Required]**`[bool]`

*   `class` **ModelFamily**(\*args : `Any`, \*\*kwargs : `Any`) [source]
    *   Bases: `object`

    A model family is a group of models that share similar characteristics from a capabilities perspective. This is distinct from discrete supported features such as vision, function calling, and JSON output. This namespace class holds constants for the model families understood by AutoGen. Other families exist and can be represented by a string, but AutoGen will treat them as unknown.

    *   `ANY` # alias of `Literal['gpt-41', 'gpt-45', 'gpt-4o', 'o1', 'o3', 'o4', 'gpt-4', 'gpt-35', 'r1', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-2.5-pro', 'claude-3-haiku', 'claude-3-sonnet', 'claude-3-opus', 'claude-3-5-haiku', 'claude-3-5-sonnet', 'claude-3-7-sonnet', 'codestral', 'open-codestral-mamba', 'mistral', 'ministral', 'pixtral', 'unknown']`
    *   `CLAUDE_3_5_HAIKU` = `'claude-3-5-haiku'`
    *   `CLAUDE_3_5_SONNET` = `'claude-3-5-sonnet'`
    *   `CLAUDE_3_7_SONNET` = `'claude-3-7-sonnet'`
    *   `CLAUDE_3_HAIKU` = `'claude-3-haiku'`
    *   `CLAUDE_3_OPUS` = `'claude-3-opus'`
    *   `CLAUDE_3_SONNET` = `'claude-3-sonnet'`
    *   `CODESRAL` = `'codestral'`
    *   `GEMINI_1_5_FLASH` = `'gemini-1.5-flash'`
    *   `GEMINI_1_5_PRO` = `'gemini-1.5-pro'`
    *   `GEMINI_2_0_FLASH` = `'gemini-2.0-flash'`
    *   `GEMINI_2_5_PRO` = `'gemini-2.5-pro'`
    *   `GPT_35` = `'gpt-35'`
    *   `GPT_4` = `'gpt-4'`
    *   `GPT_41` = `'gpt-41'`
    *   `GPT_45` = `'gpt-45'`
    *   `GPT_4O` = `'gpt-4o'`
    *   `MINISTRAL` = `'ministral'`
    *   `MISTRAL` = `'mistral'`
    *   `O1` = `'o1'`
    *   `O3` = `'o3'`
    *   `O4` = `'o4'`
    *   `OPEN_CODESRAL_MAMBA` = `'open-codestral-mamba'`
    *   `PIXTRAL` = `'pixtral'`
    *   `R1` = `'r1'`
    *   `UNKNOWN` = `'unknown'`

    *   `static` **is_claude**(family : `str`) → `bool`[source]
    *   `static` **is_gemini**(family : `str`) → `bool`[source]
    *   `static` **is_mistral**(family : `str`) → `bool`[source]
    *   `static` **is_openai**(family : `str`) → `bool`[source]

*   `class` **ModelInfo**[source]
    *   Bases: `TypedDict`

    `ModelInfo` is a dictionary that contains information about a model’s properties. It is expected to be used in the `model_info` property of a model client. This structure is designed to expand over time as features are added.

    *   `family`: **[Required]**`[Literal['gpt-41', 'gpt-45', 'gpt-4o', 'o1', 'o3', 'o4', 'gpt-4', 'gpt-35', 'r1', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-2.5-pro', 'claude-3-haiku', 'claude-3-sonnet', 'claude-3-opus', 'claude-3-5-haiku', 'claude-3-5-sonnet', 'claude-3-7-sonnet', 'codestral', 'open-codestral-mamba', 'mistral', 'ministral', 'pixtral', 'unknown'] | str]` # Model family should be one of the constants from `ModelFamily` or a string representing an unknown model family.
    *   `function_calling`: **[Required]**`[bool]` # `True` if the model supports function calling, otherwise `False`.
    *   `json_output`: **[Required]**`[bool]` # `True` if the model supports JSON output, otherwise `False`. Note this is different to structured JSON.
    *   `multiple_system_messages`: `bool` | `None` # `True` if the model supports multiple, non-consecutive system messages, otherwise `False`.
    *   `structured_output`: **[Required]**`[bool]` # `True` if the model supports structured output, otherwise `False`. This is different to `json_output`.
    *   `vision`: **[Required]**`[bool]` # `True` if the model supports vision, also known as image input, otherwise `False`.

*   `class` **RequestUsage**(`prompt_tokens` : `int`, `completion_tokens` : `int`) [source]
    *   Bases: `object`
    *   `completion_tokens`: `int`
    *   `prompt_tokens`: `int`

*   `pydantic model` **SystemMessage**[source]
    *   Bases: `BaseModel`

    `SystemMessage` contains instructions for the model originating from the developer.

    Note: Open AI is transitioning away from using the ‘system’ role in favor of the ‘developer’ role. More details are available in their Model Spec. However, the ‘system’ role remains permitted in their API and will be automatically converted to the ‘developer’ role on the server side. Therefore, you can continue to use `SystemMessage` for developer messages.

    Show JSON schema
    ```json
    {
      "title": "SystemMessage",
      "description": "System message contains instructions for the model coming from the developer.\n\n.. note::\n\n Open AI is moving away from using 'system' role in favor of 'developer' role.\n See `Model Spec <https://cdn.openai.com/spec/model-spec-2024-05-08.html#definitions>`_ for more details.\n However, the 'system' role is still allowed in their API and will be automatically converted to 'developer' role\n on the server side.\n So, you can use `SystemMessage` for developer messages.",
      "type": "object",
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
      ]
    }
    ```

    Fields:
    *   `content` (`str`)
        *   `field` `content`: `str` **[Required]** # The content of the message.
    *   `type` (`Literal['SystemMessage']`)
        *   `field` `type`: `Literal['SystemMessage']` = `'SystemMessage'`

*   `class` **TopLogprob**(`logprob` : `float`, `bytes` : `List[int]` | `None` = `None`) [source]
    *   Bases: `object`
    *   `bytes`: `List[int]` | `None` = `None`
    *   `logprob`: `float`

*   `pydantic model` **UserMessage**[source]
    *   Bases: `BaseModel`

    `UserMessage` contains input from end users, or serves as a catch-all for data provided to the model.

    Show JSON schema
    ```json
    {
      "title": "UserMessage",
      "description": "User message contains input from end users, or a catch-all for data provided to the model.",
      "type": "object",
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
      ]
    }
    ```

    Fields:
    *   `content` (`str` | `List[str | autogen_core._image.Image]`)
        *   `field` `content`: `str` | `List[str|Image]` **[Required]** # The content of the message.
    *   `source` (`str`)
        *   `field` `source`: `str` **[Required]** # The name of the agent that sent this message.
    *   `type` (`Literal['UserMessage']`)
        *   `field` `type`: `Literal['UserMessage']` = `'UserMessage'`

*   **validate_model_info**(`model_info` : `ModelInfo`) → `None`[source]
    Validates the `model_info` dictionary.

    Raises:
    *   `ValueError` – If the model info dictionary is missing required fields.
