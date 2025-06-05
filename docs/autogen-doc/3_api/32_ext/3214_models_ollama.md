### `autogen_ext.models.ollama`

`pydantic model` `BaseOllamaClientConfigurationConfigModel`
Bases: `CreateArgumentsConfigModel`

Show JSON schema
```json
{
  "title": "BaseOllamaClientConfigurationConfigModel",
  "type": "object",
  "properties": {
    "model": {
      "title": "Model",
      "type": "string"
    },
    "host": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Host"
    },
    "response_format": {
      "default": null,
      "title": "Response Format"
    },
    "follow_redirects": {
      "default": true,
      "title": "Follow Redirects",
      "type": "boolean"
    },
    "timeout": {
      "default": null,
      "title": "Timeout"
    },
    "headers": {
      "anyOf": [
        {
          "additionalProperties": {
            "type": "string"
          },
          "type": "object"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Headers"
    },
    "model_capabilities": {
      "anyOf": [
        {
          "$ref": "#/$defs/ModelCapabilities"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "model_info": {
      "anyOf": [
        {
          "$ref": "#/$defs/ModelInfo"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "options": {
      "anyOf": [
        {
          "type": "object"
        },
        {
          "$ref": "#/$defs/Options"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Options"
    }
  },
  "$defs": {
    "ModelCapabilities": {
      "deprecated": true,
      "properties": {
        "vision": {
          "title": "Vision",
          "type": "boolean"
        },
        "function_calling": {
          "title": "Function Calling",
          "type": "boolean"
        },
        "json_output": {
          "title": "Json Output",
          "type": "boolean"
        }
      },
      "required": [
        "vision",
        "function_calling",
        "json_output"
      ],
      "title": "ModelCapabilities",
      "type": "object"
    },
    "ModelInfo": {
      "description": "ModelInfo is a dictionary that contains information about a model's properties.\nIt is expected to be used in the model_info property of a model client.\n\nWe are expecting this to grow over time as we add more features.",
      "properties": {
        "vision": {
          "title": "Vision",
          "type": "boolean"
        },
        "function_calling": {
          "title": "Function Calling",
          "type": "boolean"
        },
        "json_output": {
          "title": "Json Output",
          "type": "boolean"
        },
        "family": {
          "anyOf": [
            {
              "enum": [
                "gpt-41",
                "gpt-45",
                "gpt-4o",
                "o1",
                "o3",
                "o4",
                "gpt-4",
                "gpt-35",
                "r1",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.0-flash",
                "gemini-2.5-pro",
                "claude-3-haiku",
                "claude-3-sonnet",
                "claude-3-opus",
                "claude-3-5-haiku",
                "claude-3-5-sonnet",
                "claude-3-7-sonnet",
                "codestral",
                "open-codestral-mamba",
                "mistral",
                "ministral",
                "pixtral",
                "unknown"
              ],
              "type": "string"
            },
            {
              "type": "string"
            }
          ],
          "title": "Family"
        },
        "structured_output": {
          "title": "Structured Output",
          "type": "boolean"
        },
        "multiple_system_messages": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "title": "Multiple System Messages"
        }
      },
      "required": [
        "vision",
        "function_calling",
        "json_output",
        "family",
        "structured_output"
      ],
      "title": "ModelInfo",
      "type": "object"
    },
    "Options": {
      "properties": {
        "numa": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Numa"
        },
        "num_ctx": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Num Ctx"
        },
        "num_batch": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Num Batch"
        },
        "num_gpu": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Num Gpu"
        },
        "main_gpu": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Main Gpu"
        },
        "low_vram": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Low Vram"
        },
        "f16_kv": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "F16 Kv"
        },
        "logits_all": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Logits All"
        },
        "vocab_only": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Vocab Only"
        },
        "use_mmap": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Use Mmap"
        },
        "use_mlock": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Use Mlock"
        },
        "embedding_only": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Embedding Only"
        },
        "num_thread": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Num Thread"
        },
        "num_keep": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Num Keep"
        },
        "seed": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Seed"
        },
        "num_predict": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Num Predict"
        },
        "top_k": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Top K"
        },
        "top_p": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Top P"
        },
        "tfs_z": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Tfs Z"
        },
        "typical_p": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Typical P"
        },
        "repeat_last_n": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Repeat Last N"
        },
        "temperature": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Temperature"
        },
        "repeat_penalty": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Repeat Penalty"
        },
        "presence_penalty": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Presence Penalty"
        },
        "frequency_penalty": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Frequency Penalty"
        },
        "mirostat": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mirostat"
        },
        "mirostat_tau": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mirostat Tau"
        },
        "mirostat_eta": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Mirostat Eta"
        },
        "penalize_newline": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Penalize Newline"
        },
        "stop": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Stop"
        }
      },
      "title": "Options",
      "type": "object"
    }
  },
  "required": [
    "model"
  ]
}
```

**Fields**

*   `follow_redirects` (`bool`)
*   `headers` (`Mapping[str, str] | None`)
*   `model_capabilities` (`autogen_core.models._model_client.ModelCapabilities | None`)
*   `model_info` (`autogen_core.models._model_client.ModelInfo | None`)
*   `options` (`Mapping[str, Any] | ollama._types.Options | None`)
*   `timeout` (`Any`)

*field* `follow_redirects`: `bool` *= True*
*field* `headers`: `Mapping[str, str] | None` *= None*
*field* `model_capabilities`: `ModelCapabilities | None` *= None*
*field* `model_info`: `ModelInfo | None` *= None*
*field* `options`: `Mapping[str, Any] | Options | None` *= None*
*field* `timeout`: `Any` *= None*

`pydantic model` `CreateArgumentsConfigModel`
Bases: `BaseModel`

Show JSON schema
```json
{
  "title": "CreateArgumentsConfigModel",
  "type": "object",
  "properties": {
    "model": {
      "title": "Model",
      "type": "string"
    },
    "host": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Host"
    },
    "response_format": {
      "default": null,
      "title": "Response Format"
    }
  },
  "required": [
    "model"
  ]
}
```

**Fields**

*   `host` (`str | None`)
*   `model` (`str`)
*   `response_format` (`Any`)

*field* `host`: `str | None` *= None*
*field* `model`: `str` *[Required]*
*field* `response_format`: `Any` *= None*

`class` `OllamaChatCompletionClient`(`**kwargs`: `Unpack`)[source]
Bases: `BaseOllamaChatCompletionClient`, `Component[BaseOllamaClientConfigurationConfigModel]`

Chat completion client for Ollama hosted models.
Ollama must be installed and the appropriate model pulled.

**Parameters**

*   **model** (`str`) – Which Ollama model to use.
*   **host** (`optional`, `str`) – Model host url.
*   **response_format** (`optional`, `pydantic.BaseModel`) – The format of the response. If provided, the response will be parsed into this format as json.
*   **options** (`optional`, `Mapping`[`str`, `Any`] `|` `Options`) – Additional options to pass to the Ollama client.
*   **model_info** (`optional`, `ModelInfo`) – The capabilities of the model. **Required if the model is not listed in the ollama model info.**

**Note**
Only models with 200k+ downloads (as of Jan 21, 2025), + phi4, deepseek-r1 have pre-defined model infos. Refer to this file for the full list. An entry for one model encompasses all parameter variants of that model.

To use this client, you must install the `ollama` extension:
```bash
pip install "autogen-ext[ollama]"
```

The following code snippet shows how to use the client with an Ollama model:
```python
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.models import UserMessage

ollama_client = OllamaChatCompletionClient(
    model="llama3",
)

result = await ollama_client.create([UserMessage(content="What is the capital of France?", source="user")]) # type: ignore
print(result)
```

To load the client from a configuration, you can use the `load_component` method:
```python
from autogen_core.models import ChatCompletionClient

config = {
    "provider": "OllamaChatCompletionClient",
    "config": {"model": "llama3"},
}

client = ChatCompletionClient.load_component(config)
```

To output structured data, you can use the `response_format` argument:
```python
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.models import UserMessage
from pydantic import BaseModel

class StructuredOutput(BaseModel):
    first_name: str
    last_name: str

ollama_client = OllamaChatCompletionClient(
    model="llama3",
    response_format=StructuredOutput,
)

result = await ollama_client.create([UserMessage(content="Who was the first man on the moon?", source="user")]) # type: ignore
print(result)
```

**Note**
Tool usage in ollama is stricter than in its OpenAI counterparts. While OpenAI accepts a map of [`str`, `Any`], Ollama requires a map of [`str`, `Property`] where `Property` is a typed object containing `type` and `description` fields. Therefore, only the keys `type` and `description` will be converted from the properties blob in the tool schema.

To view the full list of available configuration options, see the `OllamaClientConfigurationConfigModel` class.

*classmethod* `_from_config`(config : `BaseOllamaClientConfigurationConfigModel`) `→` `Self`[source]
Create a new instance of the component from a configuration object.

**Parameters**

*   **config** (`T`) – The configuration object.

**Returns**

*   **Self** – The new instance of the component.

`_to_config`(` `) `→` `BaseOllamaClientConfigurationConfigModel`[source]
Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns**

*   **T** – The configuration of the component.

`component_config_schema`
alias of `BaseOllamaClientConfigurationConfigModel`

`component_provider_override`: `ClassVar[str | None]` *= 'autogen_ext.models.ollama.OllamaChatCompletionClient'*
Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

`component_type`: `ClassVar[ComponentType]` *= 'model'*
The logical type of the component.
