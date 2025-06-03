# Models

In many cases, agents necessitate access to LLM model services, encompassing providers such as OpenAI, Azure OpenAI, or local models. Given the diversity of providers and their respective APIs, `autogen-core` establishes a protocol for model clients, while `autogen-ext` delivers a collection of model clients for widely-used model services. These model clients enable AgentChat to interact with the various model services.

This section presents a concise overview of the available model clients. For more granular details on direct usage, consult the Model Clients documentation within the Core API.

---

**Note**
Refer to `ChatCompletionCache` for a caching wrapper designed for use with the following clients.

---

### Log Model Calls

AutoGen employs the standard Python logging module to record events such as model calls and their corresponding responses. The designated logger name is `autogen_core.EVENT_LOGGER_NAME`, and the associated event type is `LLMCall`.

```python
import logging
from autogen_core import EVENT_LOGGER_NAME

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
```

### OpenAI

To interface with OpenAI models, install the `openai` extension, which facilitates the use of the `OpenAIChatCompletionClient`.

```bash
pip install "autogen-ext[openai]"
```

An API key must be obtained from OpenAI.

```python
from autogen_ext.models.openai import OpenAIChatCompletionClient

openai_model_client = OpenAIChatCompletionClient(
    model="gpt-4o-2024-08-06",
    # api_key="sk-...", # Optional if you have an OPENAI_API_KEY environment variable set.
)
```

To validate the functionality of the model client, the following code snippet can be executed:

```python
from autogen_core.models import UserMessage

result = await openai_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
print(result)
await openai_model_client.close()
```

**Output Example:**
```
CreateResult(finish_reason='stop', content='The capital of France is Paris.', usage=RequestUsage(prompt_tokens=15, completion_tokens=7), cached=False, logprobs=None)
```

---

**Note**
This client is compatible with models hosted on OpenAI-compatible endpoints; however, this specific functionality has not been thoroughly tested. Consult `OpenAIChatCompletionClient` for additional information.

---

### Azure OpenAI

Similarly, to utilize the `AzureOpenAIChatCompletionClient`, install both the `azure` and `openai` extensions.

```bash
pip install "autogen-ext[openai,azure]"
```

Employing this client necessitates providing your deployment ID, Azure Cognitive Services endpoint, API version, and model capabilities. For authentication, either an API key or an Azure Active Directory (AAD) token credential can be supplied.

The subsequent code snippet demonstrates the process of using AAD authentication. The identity leveraged must possess the `Cognitive Services OpenAI User` role.

```python
from autogen_ext.auth.azure import AzureTokenProvider
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import DefaultAzureCredential

# Create the token provider
token_provider = AzureTokenProvider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

az_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment="{your-azure-deployment}",
    model="{model-name, such as gpt-4o}",
    api_version="2024-06-01",
    azure_endpoint="https://{your-custom-endpoint}.openai.azure.com/",
    azure_ad_token_provider=token_provider, # Optional if you choose key-based authentication.
    # api_key="sk-...", # For key-based authentication.
)

result = await az_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
print(result)
await az_model_client.close()
```

For further details on how to directly utilize the Azure client or for more extensive information, please refer to the relevant documentation.

### Azure AI Foundry

Azure AI Foundry, previously known as Azure AI Studio, hosts models on Azure. To interact with these models, the `AzureAIChatCompletionClient` is employed.

The `azure` extra must be installed to use this client.

```bash
pip install "autogen-ext[azure]"
```

An example demonstrating the use of this client with the Phi-4 model from GitHub Marketplace is provided below.

```python
import os
from autogen_core.models import UserMessage
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential

client = AzureAIChatCompletionClient(
    model="Phi-4",
    endpoint="https://models.inference.ai.azure.com",
    # To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings.
    # Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
    credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
    model_info={
        "json_output": False,
        "function_calling": False,
        "vision": False,
        "family": "unknown",
        "structured_output": False,
    },
)

result = await client.create([UserMessage(content="What is the capital of France?", source="user")])
print(result)
await client.close()
```

**Output Example:**
```
finish_reason='stop' content='The capital of France is Paris.' usage=RequestUsage(prompt_tokens=14, completion_tokens=8) cached=False logprobs=None
```

### Anthropic (experimental)

To use the `AnthropicChatCompletionClient`, the `anthropic` extra must be installed. Internally, it leverages the `anthropic` Python SDK to access the models. Additionally, an API key from Anthropic is required.

```python
# !pip install -U "autogen-ext[anthropic]"
from autogen_core.models import UserMessage
from autogen_ext.models.anthropic import AnthropicChatCompletionClient

anthropic_client = AnthropicChatCompletionClient(model="claude-3-7-sonnet-20250219")

result = await anthropic_client.create([UserMessage(content="What is the capital of France?", source="user")])
print(result)
await anthropic_client.close()
```

**Output Example:**
```
finish_reason='stop' content="The capital of France is Paris. It's not only the political and administrative capital but also a major global center for art, fashion, gastronomy, and culture. Paris is known for landmarks such as the Eiffel Tower, the Louvre Museum, Notre-Dame Cathedral, and the Champs-Élysées." usage=RequestUsage(prompt_tokens=14, completion_tokens=73) cached=False logprobs=None thought=None
```

### Ollama (experimental)

Ollama functions as a local model server, enabling models to operate directly on your machine.

---

**Note**
Small local models typically exhibit reduced capabilities compared to larger cloud-based models. For certain tasks, their performance may be suboptimal, and the resulting output could be surprising.

---

To use Ollama, install the `ollama` extension and employ the `OllamaChatCompletionClient`.

```bash
pip install -U "autogen-ext[ollama]"
```

```python
from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient

# Assuming your Ollama server is running locally on port 11434.
ollama_model_client = OllamaChatCompletionClient(model="llama3.2")

response = await ollama_model_client.create([UserMessage(content="What is the capital of France?", source="user")])
print(response)
await ollama_model_client.close()
```

**Output Example:**
```
finish_reason='unknown' content='The capital of France is Paris.' usage=RequestUsage(prompt_tokens=32, completion_tokens=8) cached=False logprobs=None thought=None
```

### Gemini (experimental)

Gemini currently provides an OpenAI-compatible API (beta). Consequently, the `OpenAIChatCompletionClient` can be used with the Gemini API.

---

**Note**
While some model providers may offer OpenAI-compatible APIs, minor differences can still exist. For instance, the `finish_reason` field in the response might vary.

---

```python
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="gemini-1.5-flash-8b",
    # api_key="GEMINI_API_KEY",
)

response = await model_client.create([UserMessage(content="What is the capital of France?", source="user")])
print(response)
await model_client.close()
```

**Output Example:**
```
finish_reason='stop' content='Paris\n' usage=RequestUsage(prompt_tokens=7, completion_tokens=2) cached=False logprobs=None thought=None
```

Furthermore, as Gemini introduces new models, it may be necessary to define their capabilities via the `model_info` field. For example, to use `gemini-2.0-flash-lite` or a similar new model, the following code can be utilized:

```python
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash-lite",
    model_info=ModelInfo(
        vision=True,
        function_calling=True,
        json_output=True,
        family="unknown",
        structured_output=True
    )
    # api_key="GEMINI_API_KEY",
)

response = await model_client.create([UserMessage(content="What is the capital of France?", source="user")])
print(response)
await model_client.close()
```

### Semantic Kernel Adapter

The `SKChatCompletionAdapter` facilitates the use of Semantic Kernel model clients as a `ChatCompletionClient` by adapting them to the required interface.

To use this adapter, you must install the relevant provider extras.

The list of installable extras includes:
*   `semantic-kernel-anthropic`: Install this extra to use Anthropic models.
*   `semantic-kernel-google`: Install this extra to use Google Gemini models.
*   `semantic-kernel-ollama`: Install this extra to use Ollama models.
*   `semantic-kernel-mistralai`: Install this extra to use MistralAI models.
*   `semantic-kernel-aws`: Install this extra to use AWS models.
*   `semantic-kernel-hugging-face`: Install this extra to use Hugging Face models.

For instance, to incorporate Anthropic models, you need to install `semantic-kernel-anthropic`.

```bash
# pip install "autogen-ext[semantic-kernel-anthropic]"
```

To employ this adapter, a Semantic Kernel model client must be created and subsequently passed to the adapter.

An example demonstrating the use of the Anthropic model is as follows:

```python
import os
from autogen_core.models import UserMessage
from autogen_ext.models.semantic_kernel import SKChatCompletionAdapter
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.anthropic import AnthropicChatCompletion, AnthropicChatPromptExecutionSettings
from semantic_kernel.memory.null_memory import NullMemory

sk_client = AnthropicChatCompletion(
    ai_model_id="claude-3-5-sonnet-20241022",
    api_key=os.environ["ANTHROPIC_API_KEY"],
    service_id="my-service-id",  # Optional; for targeting specific services within Semantic Kernel
)

settings = AnthropicChatPromptExecutionSettings(
    temperature=0.2,
)

anthropic_model_client = SKChatCompletionAdapter(
    sk_client,
    kernel=Kernel(memory=NullMemory()),
    prompt_settings=settings
)

# Call the model directly.
model_result = await anthropic_model_client.create(
    messages=[UserMessage(content="What is the capital of France?", source="User")]
)
print(model_result)
await anthropic_model_client.close()
```

**Output Example:**
```
finish_reason='stop' content='The capital of France is Paris. It is also the largest city in France and one of the most populous metropolitan areas in Europe.' usage=RequestUsage(prompt_tokens=0, completion_tokens=0) cached=False logprobs=None
```

Further information regarding the Semantic Kernel Adapter can be found in its dedicated documentation.