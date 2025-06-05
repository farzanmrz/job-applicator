# Migration Guide for v0.2 to v0.4

This document serves as a migration guide for users transitioning from the `v0.2.*` versions of `autogen-agentchat` to the `v0.4` version. The `v0.4` release introduces a new set of APIs and features, including breaking changes, necessitating careful review of this guide. While the `v0.2` version is still maintained in the `0.2` branch, upgrading to `v0.4` is highly recommended.

**Note**: As of version 0.2.34, releases from the `pyautogen` PyPI package are no longer from Microsoft due to a lack of admin access. To continue using the `v0.2` version of AutoGen, installation should be performed using `autogen-agentchat~=0.2`. Users are advised to review the clarification statement regarding forks.

### What is v0.4?

Since its release in 2023, AutoGen has gathered significant community and user feedback from various sectors, ranging from small startups to large enterprises. This feedback directly informed the development of AutoGen `v0.4`, which represents a complete rewrite. This new version adopts an asynchronous, event-driven architecture, specifically designed to address critical aspects such as observability, flexibility, interactive control, and scalability.

The `v0.4` API is structured in layers:
*   The **Core API** forms the foundational layer, providing a scalable, event-driven actor framework for constructing agentic workflows.
*   Built upon the Core API, the **AgentChat API** offers a task-driven, high-level framework tailored for building interactive agentic applications. The AgentChat API serves as the direct replacement for AutoGen `v0.2`.

Most of this guide focuses on `v0.4`’s AgentChat API; however, it is also possible to construct custom high-level frameworks utilizing only the Core API.

### New to AutoGen?

For new users, it is recommended to directly access the AgentChat Tutorial to commence working with `v0.4`.

### What’s in this guide?

This guide provides detailed instructions for migrating existing codebases from `v0.2` to `v0.4`. Detailed migration information is provided for each feature listed below:
*   Model Client
*   Use component config
*   Use model client class directly
*   Model Client for OpenAI-Compatible APIs
*   Model Client Cache
*   Assistant Agent
*   Multi-Modal Agent
*   User Proxy
*   RAG Agent
*   Conversable Agent and Register Reply
*   Save and Load Agent State
*   Two-Agent Chat
*   Tool Use
*   Chat Result
*   Conversion between v0.2 and v0.4 Messages
*   Group Chat
*   Group Chat with Resume
*   Save and Load Group Chat State
*   Group Chat with Tool Use
*   Group Chat with Custom Selector (Stateflow)
*   Nested Chat
*   Sequential Chat
*   GPTAssistantAgent
*   Long Context Handling
*   Observability and Control
*   Code Executors

The following features, currently available in `v0.2`, are planned for future releases of `v0.4.*` versions:
*   Model Client Cost #4835
*   Teachable Agent
*   RAG Agent

This guide will be updated as these missing features become available.

### Model Client

In `v0.2`, the model client was configured by creating an `OpenAIWrapper` object with a `config_list`:

```python
from autogen.oai import OpenAIWrapper

config_list = [
    { "model": "gpt-4o", "api_key": "sk-xxx" },
    { "model": "gpt-4o-mini", "api_key": "sk-xxx" },
]

model_client = OpenAIWrapper(config_list=config_list)
```


**Note**: In AutoGen 0.2, the OpenAI client would attempt configurations in the provided list until a successful one was found. Conversely, 0.4 expects a specific model configuration to be selected.

In `v0.4`, two primary methods are available for creating a model client:

#### Use component config

AutoGen 0.4 features a generic component configuration system, for which model clients are an excellent use case. Below is an example of creating an OpenAI chat completion client using this system:

```python
from autogen_core.models import ChatCompletionClient

config = {
    "provider": "OpenAIChatCompletionClient",
    "config": {
        "model": "gpt-4o",
        "api_key": "sk-xxx"  # os.environ["...']
    }
}

model_client = ChatCompletionClient.load_component(config)
```


#### Use model client class directly

For direct class instantiation in `v0.4`, the following approaches are available:

**Open AI**:
```python
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key="sk-xxx")
```


**Azure OpenAI**:
```python
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

model_client = AzureOpenAIChatCompletionClient(
    azure_deployment="gpt-4o",
    azure_endpoint="https://<your-endpoint>.openai.azure.com/",
    model="gpt-4o",
    api_version="2024-09-01-preview",
    api_key="sk-xxx",
)
```


Further details can be found in the `OpenAIChatCompletionClient` documentation.

### Model Client for OpenAI-Compatible APIs

The `OpenAIChatCompletionClient` can be utilized to connect to an OpenAI-Compatible API. This requires specifying both the `base_url` and `model_info` parameters:

```python
from autogen_ext.models.openai import OpenAIChatCompletionClient

custom_model_client = OpenAIChatCompletionClient(
    model="custom-model-name",
    base_url="https://custom-model.com/reset/of/the/path",
    api_key="placeholder",
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
        "structured_output": True,
    },
)
```


**Note**: Not all OpenAI-Compatible APIs are tested, and many may function differently from the official OpenAI API despite claiming support. It is crucial to test them prior to use.

More information on Model Clients is available in the AgentChat Tutorial, with more detailed information provided in the Core API Docs. Support for other hosted models is slated for future inclusion.

### Model Client Cache

In `v0.2`, caching was enabled by default and configured via the `cache_seed` parameter within the LLM configuration:

```python
llm_config = {
    "config_list": [{ "model": "gpt-4o", "api_key": "sk-xxx" }],
    "seed": 42,
    "temperature": 0,
    "cache_seed": 42,
}
```


In `v0.4`, caching is not enabled by default. To use it, a `ChatCompletionCache` wrapper must be employed around the model client. Cache storage can be managed using either a `DiskCacheStore` or `RedisStore`.

Installation of necessary packages can be done via `pip`:
```bash
pip install -U "autogen-ext[openai, diskcache, redis]"
```


Here is an example demonstrating the use of `diskcache` for local caching:

```python
import asyncio
import tempfile
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.cache import ChatCompletionCache, CHAT_CACHE_VALUE_TYPE
from autogen_ext.cache_store.diskcache import DiskCacheStore
from diskcache import Cache

async def main():
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Initialize the original client
        openai_model_client = OpenAIChatCompletionClient(model="gpt-4o")

        # Then initialize the CacheStore, in this case with diskcache.Cache.
        # You can also use redis like:
        # from autogen_ext.cache_store.redis import RedisStore
        # import redis
        # redis_instance = redis.Redis()
        # cache_store = RedisCacheStore[CHAT_CACHE_VALUE_TYPE](redis_instance)
        cache_store = DiskCacheStore[CHAT_CACHE_VALUE_TYPE](Cache(tmpdirname))

        cache_client = ChatCompletionCache(openai_model_client, cache_store)

        response = await cache_client.create([UserMessage(content="Hello, how are you?", source="user")])
        print(response) # Should print response from OpenAI

        response = await cache_client.create([UserMessage(content="Hello, how are you?", source="user")])
        print(response) # Should print cached response

        await openai_model_client.close()

asyncio.run(main())
```


### Assistant Agent

In `v0.2`, an assistant agent was created as follows:

```python
from autogen.agentchat import AssistantAgent

llm_config = {
    "config_list": [{ "model": "gpt-4o", "api_key": "sk-xxx" }],
    "seed": 42,
    "temperature": 0,
}

assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config=llm_config,
)
```


In `v0.4`, the creation process is similar, but `model_client` is specified instead of `llm_config`:

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key="sk-xxx", seed=42, temperature=0)

assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    model_client=model_client,
)
```


The usage, however, differs somewhat. In `v0.4`, instead of calling `assistant.send`, one calls `assistant.on_messages` or `assistant.on_messages_stream` to handle incoming messages. Both `on_messages` and `on_messages_stream` methods are asynchronous. The latter returns an async generator, enabling streaming of the agent's inner thoughts.

Below is an example of how to directly call the assistant agent in `v0.4`, building upon the previous example:

```python
import asyncio
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        model_client=model_client,
    )

    cancellation_token = CancellationToken()
    response = await assistant.on_messages([TextMessage(content="Hello!", source="user")], cancellation_token)
    print(response)

    await model_client.close()

asyncio.run(main())
```


The `CancellationToken` facilitates asynchronous cancellation of requests. Invoking `cancellation_token.cancel()` will cause the `await` on the `on_messages` call to raise a `CancelledError`. Further details are available in the Agent Tutorial and on `AssistantAgent`.

### Multi-Modal Agent

The `AssistantAgent` in `v0.4` supports multi-modal inputs, provided the underlying model client also supports this capability. The `vision` capability of the model client is used to determine if the agent can handle multi-modal inputs.

```python
import asyncio
from pathlib import Path
from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken, Image
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        model_client=model_client,
    )

    cancellation_token = CancellationToken()
    message = MultiModalMessage(
        content=["Here is an image:", Image.from_file(Path("test.png"))],
        source="user",
    )

    response = await assistant.on_messages([message], cancellation_token)
    print(response)

    await model_client.close()

asyncio.run(main())
```


### User Proxy

In `v0.2`, a user proxy was created as follows:

```python
from autogen.agentchat import UserProxyAgent

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config=False,
    llm_config=False,
)
```


This `v0.2` user proxy would receive input from the user via the console and would terminate if an incoming message ended with “TERMINATE”.

In `v0.4`, a user proxy is streamlined to simply be an agent that exclusively receives user input, requiring no additional special configuration. A user proxy can be created as shown below:

```python
from autogen_agentchat.agents import UserProxyAgent

user_proxy = UserProxyAgent("user_proxy")
```


More details and customization options for the input function, including timeouts, are available in the `UserProxyAgent` documentation.

### RAG Agent

In `v0.2`, concepts like teachable agents and RAG agents capable of taking a database configuration were present:

```python
teachable_agent = ConversableAgent(
    name="teachable_agent",
    llm_config=llm_config
)

# Instantiate a Teachability object. Its parameters are all optional.
teachability = Teachability(
    reset_db=False,
    path_to_db_dir="./tmp/interactive/teachability_db"
)
teachability.add_to_agent(teachable_agent)
```


In `v0.4`, a RAG agent can be implemented using the `Memory` class. This involves defining a memory store class and passing it as a parameter to the assistant agent. The Memory tutorial provides further details.

This clear separation of concerns enables users to implement a memory store inheriting from the `Memory` class, using any desired database or storage system, and integrate it with an assistant agent. The application logic is responsible for determining how and when content is added to the memory store; for instance, `memory.add` could be called for every assistant agent response, or a separate LLM call could decide content inclusion.

The example below illustrates the use of a ChromaDB vector memory store with the assistant agent:

```python
# ...
# example of a ChromaDBVectorMemory class
chroma_user_memory = ChromaDBVectorMemory(
    config=PersistentChromaDBVectorMemoryConfig(
        collection_name="preferences",
        persistence_path=os.path.join(str(Path.home()), ".chromadb_autogen"),
        k=2,  # Return top k results
        score_threshold=0.4,  # Minimum similarity score
    )
)

# you can add logic such as a document indexer that adds content to the memory store
assistant_agent = AssistantAgent(
    name="assistant_agent",
    model_client=OpenAIChatCompletionClient(
        model="gpt-4o",
    ),
    tools=[get_weather],
    memory=[chroma_user_memory],
)
```


### Conversable Agent and Register Reply

In `v0.2`, a conversable agent could be created and a reply function registered as follows:

```python
from typing import Any, Dict, List, Optional, Tuple, Union
from autogen.agentchat import ConversableAgent

llm_config = {
    "config_list": [{ "model": "gpt-4o", "api_key": "sk-xxx" }],
    "seed": 42,
    "temperature": 0,
}

conversable_agent = ConversableAgent(
    name="conversable_agent",
    system_message="You are a helpful assistant.",
    llm_config=llm_config,
    code_execution_config={ "work_dir": "coding" },
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
)

def reply_func(
    recipient: ConversableAgent,
    messages: Optional[List[Dict]] = None,
    sender: Optional[Agent] = None,
    config: Optional[Any] = None,
) -> Tuple[bool, Union[str, Dict, None]]:
    # Custom reply logic here
    return True, "Custom reply"

# Register the reply function
conversable_agent.register_reply([ConversableAgent], reply_func, position=0)

# NOTE: An async reply function will only be invoked with async send.
```


In `v0.4`, rather than inferring the behavior, parameters, or `position` of `reply_func`, users can simply create a custom agent and implement the `on_messages`, `on_reset`, and `produced_message_types` methods:

```python
from typing import Sequence
from autogen_core import CancellationToken
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import TextMessage, BaseChatMessage
from autogen_agentchat.base import Response

class CustomAgent(BaseChatAgent):
    async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
        return Response(chat_message=TextMessage(content="Custom reply", source=self.name))

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass

    @property
    def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
        return (TextMessage,)
```


This custom agent can then be used in the same manner as the `AssistantAgent`. The Custom Agent Tutorial provides further details.

### Save and Load Agent State

In `v0.2`, there was no built-in mechanism for saving and loading an agent’s state. Users were required to implement this functionality themselves by exporting the `chat_messages` attribute of `ConversableAgent` and re-importing it via the `chat_messages` parameter.

In `v0.4`, agents now provide `save_state` and `load_state` methods for managing their state.

```python
import asyncio
import json
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        model_client=model_client,
    )

    cancellation_token = CancellationToken()
    response = await assistant.on_messages([TextMessage(content="Hello!", source="user")], cancellation_token)
    print(response)

    # Save the state.
    state = await assistant.save_state()

    # (Optional) Write state to disk.
    with open("assistant_state.json", "w") as f:
        json.dump(state, f)

    # (Optional) Load it back from disk.
    with open("assistant_state.json", "r") as f:
        state = json.load(f)
    print(state) # Inspect the state, which contains the chat history.

    # Carry on the chat.
    response = await assistant.on_messages([TextMessage(content="Tell me a joke.", source="user")], cancellation_token)
    print(response)

    # Load the state, resulting the agent to revert to the previous state before the last message.
    await assistant.load_state(state)

    # Carry on the same chat again.
    response = await assistant.on_messages([TextMessage(content="Tell me a joke.", source="user")], cancellation_token)

    # Close the connection to the model client.
    await model_client.close()

asyncio.run(main())
```


The `save_state` and `load_state` methods can also be invoked on teams, such as `RoundRobinGroupChat`, to save and load the state of the entire team.

### Two-Agent Chat

In `v0.2`, a two-agent chat for code execution was established as follows:

```python
from autogen.coding import LocalCommandLineCodeExecutor
from autogen.agentchat import AssistantAgent, UserProxyAgent

llm_config = {
    "config_list": [{ "model": "gpt-4o", "api_key": "sk-xxx" }],
    "seed": 42,
    "temperature": 0,
}

assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant. Write all code in python. Reply only 'TERMINATE' if the task is done.",
    llm_config=llm_config,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={ "code_executor": LocalCommandLineCodeExecutor(work_dir="coding")},
    llm_config=False,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)

chat_result = user_proxy.initiate_chat(assistant, message="Write a python script to print 'Hello, world!'")

# Intermediate messages are printed to the console directly.
print(chat_result)
```


To achieve equivalent behavior in `v0.4`, the `AssistantAgent` and `CodeExecutorAgent` can be utilized together within a `RoundRobinGroupChat`:

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant. Write all code in python. Reply only 'TERMINATE' if the task is done.",
        model_client=model_client,
    )

    code_executor = CodeExecutorAgent(
        name="code_executor",
        code_executor=LocalCommandLineCodeExecutor(work_dir="coding"),
    )

    # The termination condition is a combination of text termination and max message termination, either of which will cause the chat to terminate.
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

    # The group chat will alternate between the assistant and the code executor.
    group_chat = RoundRobinGroupChat([assistant, code_executor], termination_condition=termination)

    # `run_stream` returns an async generator to stream the intermediate messages.
    stream = group_chat.run_stream(task="Write a python script to print 'Hello, world!'")

    # `Console` is a simple UI to display the stream.
    await Console(stream)

    # Close the connection to the model client.
    await model_client.close()

asyncio.run(main())
```


### Tool Use

In `v0.2`, creating a tool-use chatbot required two agents: one for calling the tool and one for executing it. A two-agent chat had to be initiated for every user request:

```python
from autogen.agentchat import AssistantAgent, UserProxyAgent, register_function

llm_config = {
    "config_list": [{ "model": "gpt-4o", "api_key": "sk-xxx" }],
    "seed": 42,
    "temperature": 0,
}

tool_caller = AssistantAgent(
    name="tool_caller",
    system_message="You are a helpful assistant. You can call tools to help user.",
    llm_config=llm_config,
    max_consecutive_auto_reply=1, # Set to 1 so that we return to the application after each assistant reply as we are building a chatbot.
)

tool_executor = UserProxyAgent(
    name="tool_executor",
    human_input_mode="NEVER",
    code_execution_config=False,
    llm_config=False,
)

def get_weather(city: str) -> str:
    return f"The weather in {city} is 72 degree and sunny."

# Register the tool function to the tool caller and executor.
register_function(get_weather, caller=tool_caller, executor=tool_executor)

while True:
    user_input = input("User: ")
    if user_input == "exit":
        break
    chat_result = tool_executor.initiate_chat(
        tool_caller,
        message=user_input,
        summary_method="reflection_with_llm", # To let the model reflect on the tool use, set to "last_msg" to return the tool call result directly.
    )
    print("Assistant:", chat_result.summary)
```


In `v0.4`, only one agent—the `AssistantAgent`—is needed to manage both tool calling and tool execution:

```python
import asyncio
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage

def get_weather(city: str) -> str:
    # Async tool is possible too.
    return f"The weather in {city} is 72 degree and sunny."

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant. You can call tools to help user.",
        model_client=model_client,
        tools=[get_weather],
        reflect_on_tool_use=True, # Set to True to have the model reflect on the tool use, set to False to return the tool call result directly.
    )

    while True:
        user_input = input("User: ")
        if user_input == "exit":
            break
        response = await assistant.on_messages([TextMessage(content=user_input, source="user")], CancellationToken())
        print("Assistant:", response.chat_message.to_text())

    await model_client.close()

asyncio.run(main())
```


When incorporating tool-equipped agents within a group chat, such as `RoundRobinGroupChat`, tools are added to the agents in the same manner as described above, and the group chat is then created with these agents.

### Chat Result

In `v0.2`, the `initiate_chat` method returned a `ChatResult` object:

```python
chat_result = tool_executor.initiate_chat(
    tool_caller,
    message=user_input,
    summary_method="reflection_with_llm",
)
print(chat_result.summary) # Get LLM-reflected summary of the chat.
print(chat_result.chat_history) # Get the chat history.
print(chat_result.cost) # Get the cost of the chat.
print(chat_result.human_input) # Get the human input solicited by the chat.
```


More details are available in the ChatResult Docs.

In `v0.4`, the `run` or `run_stream` methods return a `TaskResult` object. The `TaskResult` object contains the `messages` attribute, which represents the complete message history of the chat, encompassing both agents’ private (e.g., tool calls) and public messages.

There are notable differences between `TaskResult` and `ChatResult`:
*   The `messages` list within `TaskResult` employs a different message format compared to the `ChatResult.chat_history` list.
*   The `summary` field is absent. The application is responsible for summarizing the chat using the `messages` list.
*   `human_input` is not provided in the `TaskResult` object, as user input can be extracted from the `messages` list by filtering based on the `source` field.
*   `cost` is not included in the `TaskResult` object; however, cost can be calculated based on token usage. Adding cost calculation would be a valuable community extension; refer to community extensions for more.

### Conversion between v0.2 and v0.4 Messages

Conversion functions are provided to facilitate transformation between a `v0.4` message (found in `autogen_agentchat.base.TaskResult.messages`) and a `v0.2` message (found in `ChatResult.chat_history`):

```python
from typing import Any, Dict, List, Literal
from autogen_agentchat.messages import (
    BaseAgentEvent,
    BaseChatMessage,
    HandoffMessage,
    MultiModalMessage,
    StopMessage,
    TextMessage,
    ToolCallExecutionEvent,
    ToolCallRequestEvent,
    ToolCallSummaryMessage,
)
from autogen_core import FunctionCall, Image
from autogen_core.models import FunctionExecutionResult

def convert_to_v02_message(
    message: BaseAgentEvent | BaseChatMessage,
    role: Literal["assistant", "user", "tool"],
    image_detail: Literal["auto", "high", "low"] = "auto",
) -> Dict[str, Any]:
    """Convert a v0.4 AgentChat message to a v0.2 message.
    Args:
    message (BaseAgentEvent | BaseChatMessage): The message to convert.
    role (Literal["assistant", "user", "tool"]): The role of the message.
    image_detail (Literal["auto", "high", "low"], optional): The detail level of image content in multi-modal message. Defaults to "auto".
    Returns:
    Dict[str, Any]: The converted AutoGen v0.2 message.
    """
    v02_message: Dict[str, Any] = {}
    if isinstance(message, TextMessage | StopMessage | HandoffMessage | ToolCallSummaryMessage):
        v02_message = { "content": message.content, "role": role, "name": message.source }
    elif isinstance(message, MultiModalMessage):
        v02_message = { "content": [], "role": role, "name": message.source }
        for modal in message.content:
            if isinstance(modal, str):
                v02_message["content"].append({ "type": "text", "text": modal })
            elif isinstance(modal, Image):
                v02_message["content"].append(modal.to_openai_format(detail=image_detail))
            else:
                raise ValueError(f"Invalid multimodal message content: {modal}")
    elif isinstance(message, ToolCallRequestEvent):
        v02_message = { "tool_calls": [], "role": "assistant", "content": None, "name": message.source }
        for tool_call in message.content:
            v02_message["tool_calls"].append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": { "name": tool_call.name, "args": tool_call.arguments },
                }
            )
    elif isinstance(message, ToolCallExecutionEvent):
        tool_responses: List[Dict[str, str]] = []
        for tool_result in message.content:
            tool_responses.append(
                {
                    "tool_call_id": tool_result.call_id,
                    "role": "tool",
                    "content": tool_result.content,
                }
            )
        content = "\n\n".join([response["content"] for response in tool_responses])
        v02_message = { "tool_responses": tool_responses, "role": "tool", "content": content }
    else:
        raise ValueError(f"Invalid message type: {type(message)}")
    return v02_message

def convert_to_v04_message(message: Dict[str, Any]) -> BaseAgentEvent | BaseChatMessage:
    """Convert a v0.2 message to a v0.4 AgentChat message."""
    if "tool_calls" in message:
        tool_calls: List[FunctionCall] = []
        for tool_call in message["tool_calls"]:
            tool_calls.append(
                FunctionCall(
                    id=tool_call["id"],
                    name=tool_call["function"]["name"],
                    arguments=tool_call["function"]["args"],
                )
            )
        return ToolCallRequestEvent(source=message["name"], content=tool_calls)
    elif "tool_responses" in message:
        tool_results: List[FunctionExecutionResult] = []
        for tool_response in message["tool_responses"]:
            tool_results.append(
                FunctionExecutionResult(
                    call_id=tool_response["tool_call_id"],
                    content=tool_response["content"],
                    is_error=False,
                    name=tool_response["name"],
                )
            )
        return ToolCallExecutionEvent(source="tools", content=tool_results)
    elif isinstance(message["content"], list):
        content: List[str | Image] = []
        for modal in message["content"]: # type: ignore
            if modal["type"] == "text": # type: ignore
                content.append(modal["text"]) # type: ignore
            else:
                content.append(Image.from_uri(modal["image_url"]["url"])) # type: ignore
        return MultiModalMessage(content=content, source=message["name"])
    elif isinstance(message["content"], str):
        return TextMessage(content=message["content"], source=message["name"])
    else:
        raise ValueError(f"Unable to convert message: {message}")
```


### Group Chat

In `v0.2`, group chat required the creation of a `GroupChat` class, its passing into a `GroupChatManager`, and a user proxy participant to initiate the chat. For a simple writer and critic scenario, the following was performed:

```python
from autogen.agentchat import AssistantAgent, GroupChat, GroupChatManager

llm_config = {
    "config_list": [{ "model": "gpt-4o", "api_key": "sk-xxx" }],
    "seed": 42,
    "temperature": 0,
}

writer = AssistantAgent(
    name="writer",
    description="A writer.",
    system_message="You are a writer.",
    llm_config=llm_config,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("APPROVE"),
)

critic = AssistantAgent(
    name="critic",
    description="A critic.",
    system_message="You are a critic, provide feedback on the writing. Reply only 'APPROVE' if the task is done.",
    llm_config=llm_config,
)

# Create a group chat with the writer and critic.
groupchat = GroupChat(agents=[writer, critic], messages=[], max_round=12)

# Create a group chat manager to manage the group chat, use round-robin selection method.
manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config, speaker_selection_method="round_robin")

# Initiate the chat with the editor, intermediate messages are printed to the console directly.
result = editor.initiate_chat(
    manager,
    message="Write a short story about a robot that discovers it has feelings.",
)
print(result.summary)
```


In `v0.4`, the same behavior can be achieved using `RoundRobinGroupChat`:

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    writer = AssistantAgent(
        name="writer",
        description="A writer.",
        system_message="You are a writer.",
        model_client=model_client,
    )
    critic = AssistantAgent(
        name="critic",
        description="A critic.",
        system_message="You are a critic, provide feedback on the writing. Reply only 'APPROVE' if the task is done.",
        model_client=model_client,
    )

    # The termination condition is a text termination, which will cause the chat to terminate when the text "APPROVE" is received.
    termination = TextMentionTermination("APPROVE")

    # The group chat will alternate between the writer and the critic.
    group_chat = RoundRobinGroupChat([writer, critic], termination_condition=termination, max_turns=12)

    # `run_stream` returns an async generator to stream the intermediate messages.
    stream = group_chat.run_stream(task="Write a short story about a robot that discovers it has feelings.")

    # `Console` is a simple UI to display the stream.
    await Console(stream)

    # Close the connection to the model client.
    await model_client.close()

asyncio.run(main())
```


For LLM-based speaker selection, `SelectorGroupChat` can be used. Refer to the Selector Group Chat Tutorial and `SelectorGroupChat` documentation for more details.

**Note**: In `v0.4`, it is not necessary to register functions on a user proxy for tool use within a group chat. Tool functions can be directly passed to the `AssistantAgent` as demonstrated in the Tool Use section. The agent will automatically invoke tools when needed. If a tool's output is not well-formed, the `reflect_on_tool_use` parameter can be set to enable the model to reflect on the tool's use.

### Group Chat with Resume

Resuming group chats in `v0.2` was more complex, requiring explicit saving and loading of group chat messages. For more details, see Resuming Group Chat in v0.2.

In `v0.4`, resuming a chat is simplified: one can simply call `run` or `run_stream` again on the same group chat object. To export and load the state, the `save_state` and `load_state` methods are available.

```python
import asyncio
import json
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

def create_team(model_client : OpenAIChatCompletionClient) -> RoundRobinGroupChat:
    writer = AssistantAgent(
        name="writer",
        description="A writer.",
        system_message="You are a writer.",
        model_client=model_client,
    )
    critic = AssistantAgent(
        name="critic",
        description="A critic.",
        system_message="You are a critic, provide feedback on the writing. Reply only 'APPROVE' if the task is done.",
        model_client=model_client,
    )

    # The termination condition is a text termination, which will cause the chat to terminate when the text "APPROVE" is received.
    termination = TextMentionTermination("APPROVE")

    # The group chat will alternate between the writer and the critic.
    group_chat = RoundRobinGroupChat([writer, critic], termination_condition=termination)
    return group_chat

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)

    # Create team.
    group_chat = create_team(model_client)

    # `run_stream` returns an async generator to stream the intermediate messages.
    stream = group_chat.run_stream(task="Write a short story about a robot that discovers it has feelings.")

    # `Console` is a simple UI to display the stream.
    await Console(stream)

    # Save the state of the group chat and all participants.
    state = await group_chat.save_state()
    with open("group_chat_state.json", "w") as f:
        json.dump(state, f)

    # Create a new team with the same participants configuration.
    group_chat = create_team(model_client)

    # Load the state of the group chat and all participants.
    with open("group_chat_state.json", "r") as f:
        state = json.load(f)
    await group_chat.load_state(state)

    # Resume the chat.
    stream = group_chat.run_stream(task="Translate the story into Chinese.")
    await Console(stream)

    # Close the connection to the model client.
    await model_client.close()

asyncio.run(main())
```


### Save and Load Group Chat State

In `v0.2`, explicit saving and loading of group chat messages were required to resume a chat. In `v0.4`, the `save_state` and `load_state` methods can be directly called on the group chat object. An example demonstrating this is provided in the Group Chat with Resume section.

### Group Chat with Tool Use

In `v0.2` group chat, when tools were involved, tool functions needed to be registered on a user proxy, and this user proxy had to be included in the group chat. Tool calls made by other agents would then be routed through the user proxy for execution.

This approach presented numerous issues, such as unexpected tool call routing and models lacking function calling support being unable to accept tool call requests and results.

In `v0.4`, there is no longer a need to register tool functions on a user proxy. Tools are directly executed within the `AssistantAgent`, which then publishes the tool's response to the group chat. Consequently, the group chat manager is not involved in routing tool calls. An example of using tools in a group chat can be found in the Selector Group Chat Tutorial.

### Group Chat with Custom Selector (Stateflow)

In `v0.2` group chat, setting `speaker_selection_method` to a custom function allowed overriding the default selection method, which was useful for implementing state-based selection. More details are available in Custom Speaker Selection in v0.2.

In `v0.4`, the `SelectorGroupChat` with a `selector_func` achieves the same behavior. The `selector_func` is a function that accepts the current message thread of the group chat and returns the name of the next speaker. If `None` is returned, the LLM-based selection method will be employed.

Below is an example utilizing the state-based selection method to implement a web search/analysis scenario:

```python
import asyncio
from typing import Sequence
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Note: This example uses mock tools instead of real APIs for demonstration purposes
def search_web_tool(query: str) -> str:
    if "2006-2007" in query:
        return """Here are the total points scored by Miami Heat players in the 2006-2007 season:
Udonis Haslem: 844 points
Dwayne Wade: 1397 points
James Posey: 550 points
...
"""
    elif "2007-2008" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214."
    elif "2008-2009" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398."
    return "No data found."

def percentage_change_tool(start: float, end: float) -> float:
    return ((end - start) / start) * 100

def create_team(model_client : OpenAIChatCompletionClient) -> SelectorGroupChat:
    planning_agent = AssistantAgent(
        "PlanningAgent",
        description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
        model_client=model_client,
        system_message="""
    You are a planning agent.
    Your job is to break down complex tasks into smaller, manageable subtasks.
    Your team members are:
    Web search agent: Searches for information
    Data analyst: Performs calculations
    You only plan and delegate tasks - you do not execute them yourself.
    When assigning tasks, use this format:
    1. <agent> : <task>
    After all tasks are complete, summarize the findings and end with "TERMINATE".
    """,
    )
    web_search_agent = AssistantAgent(
        "WebSearchAgent",
        description="A web search agent.",
        tools=[search_web_tool],
        model_client=model_client,
        system_message="""
    You are a web search agent.
    Your only tool is search_tool - use it to find information.
    You make only one search call at a time.
    Once you have the results, you never do calculations based on them.
    """,
    )
    data_analyst_agent = AssistantAgent(
        "DataAnalystAgent",
        description="A data analyst agent. Useful for performing calculations.",
        model_client=model_client,
        tools=[percentage_change_tool],
        system_message="""
    You are a data analyst.
    Given the tasks you have been assigned, you should analyze the data and provide results using the tools provided.
    """,
    )

    # The termination condition is a combination of text mention termination and max message termination.
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination

    # The selector function is a function that takes the current message thread of the group chat
    # and returns the next speaker's name. If None is returned, the LLM-based selection method will be used.
    def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
        if messages[-1].source != planning_agent.name:
            return planning_agent.name # Always return to the planning agent after the other agents have spoken.
        return None

    team = SelectorGroupChat(
        [planning_agent, web_search_agent, data_analyst_agent],
        model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"), # Use a smaller model for the selector.
        termination_condition=termination,
        selector_func=selector_func,
    )
    return team

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    team = create_team(model_client)
    task = "Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?"
    await Console(team.run_stream(task=task))

asyncio.run(main())
```


### Nested Chat

Nested chat enables the embedding of an entire team or another agent within an agent. This functionality is beneficial for establishing hierarchical agent structures or "information silos," as the nested agents are restricted from direct communication with agents outside their immediate group.

In `v0.2`, nested chat was supported via the `register_nested_chats` method on the `ConversableAgent` class, requiring the specification of nested agent sequences using dictionaries. See Nested Chat in v0.2 for more details.

In `v0.4`, nested chat is implemented as an internal detail of a custom agent. A custom agent can be created that accepts a team or another agent as a parameter and implements the `on_messages` method to trigger the nested team or agent. The application is responsible for determining how messages are passed or transformed to and from the nested team or agent.

The following example demonstrates a simple nested chat for counting numbers:

```python
import asyncio
from typing import Sequence
from autogen_core import CancellationToken
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage, BaseChatMessage
from autogen_agentchat.base import Response

class CountingAgent(BaseChatAgent):
    """An agent that returns a new number by adding 1 to the last number in the input messages."""
    async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
        if len(messages) == 0:
            last_number = 0 # Start from 0 if no messages are given.
        else:
            assert isinstance(messages[-1], TextMessage)
            last_number = int(messages[-1].content) # Otherwise, start from the last number.
        return Response(chat_message=TextMessage(content=str(last_number + 1), source=self.name))

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass

    @property
    def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
        return (TextMessage,)

class NestedCountingAgent(BaseChatAgent):
    """An agent that increments the last number in the input messages
    multiple times using a nested counting team."""
    def __init__(self, name: str, counting_team: RoundRobinGroupChat) -> None:
        super().__init__(name, description="An agent that counts numbers.")
        self._counting_team = counting_team

    async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
        # Run the inner team with the given messages and returns the last message produced by the team.
        result = await self._counting_team.run(task=messages, cancellation_token=cancellation_token)

        # To stream the inner messages, implement `on_messages_stream` and use that to implement `on_messages`.
        assert isinstance(result.messages[-1], TextMessage)
        return Response(chat_message=result.messages[-1], inner_messages=result.messages[len(messages):-1])

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        # Reset the inner team.
        await self._counting_team.reset()

    @property
    def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
        return (TextMessage,)

async def main() -> None:
    # Create a team of two counting agents as the inner team.
    counting_agent_1 = CountingAgent("counting_agent_1", description="An agent that counts numbers.")
    counting_agent_2 = CountingAgent("counting_agent_2", description="An agent that counts numbers.")
    counting_team = RoundRobinGroupChat([counting_agent_1, counting_agent_2], max_turns=5)

    # Create a nested counting agent that takes the inner team as a parameter.
    nested_counting_agent = NestedCountingAgent("nested_counting_agent", counting_team)

    # Run the nested counting agent with a message starting from 1.
    response = await nested_counting_agent.on_messages([TextMessage(content="1", source="user")], CancellationToken())

    assert response.inner_messages is not None
    for message in response.inner_messages:
        print(message)
    print(response.chat_message)

asyncio.run(main())
```


The expected output for this example is:
```
source = 'counting_agent_1'
models_usage = None
content = '2'
type = 'TextMessage'
source = 'counting_agent_2'
models_usage = None
content = '3'
type = 'TextMessage'
source = 'counting_agent_1'
models_usage = None
content = '4'
type = 'TextMessage'
source = 'counting_agent_2'
models_usage = None
content = '5'
type = 'TextMessage'
source = 'counting_agent_1'
models_usage = None
content = '6'
type = 'TextMessage'
```


For a more complex implementation, refer to `SocietyOfMindAgent`.

### Sequential Chat

In `v0.2`, sequential chat was supported by the `initiate_chats` function, which accepted a list of dictionary configurations for each step in the sequence. Further details can be found in Sequential Chat in v0.2.

Based on community feedback, the `initiate_chats` function was deemed too opinionated and insufficiently flexible for the diverse range of scenarios users aimed to implement. Users frequently encountered difficulties with `initiate_chats` when the steps could be more easily connected using basic Python code. Consequently, `v0.4` does not include a built-in function for sequential chat within the AgentChat API.

Instead, users can construct an event-driven sequential workflow using the Core API and leverage other components provided by the AgentChat API to implement each step of the workflow. An example of a sequential workflow is available in the Core API Tutorial. The developers acknowledge that workflows are central to many applications and plan to provide more built-in support for them in the future.

### GPTAssistantAgent

In `v0.2`, `GPTAssistantAgent` was a specialized agent class backed by the OpenAI Assistant API.

In `v0.4`, the equivalent is the `OpenAIAssistantAgent` class. This class supports the same features as `GPTAssistantAgent` in `v0.2`, along with additional capabilities such as customizable threads and file uploads. Refer to `OpenAIAssistantAgent` for more details.

### Long Context Handling

In `v0.2`, long contexts that exceeded the model’s context window could be managed using the `transforms` capability, which was added to a `ConversableAgent` after its construction. Feedback from the community indicated that this feature was essential and should be a built-in component of `AssistantAgent`, usable by any custom agent.

In `v0.4`, the `ChatCompletionContext` base class is introduced. This class manages message history and provides a virtual view of that history. Applications can utilize built-in implementations like `BufferedChatCompletionContext` to limit the message history sent to the model, or they can provide their own implementations to create different virtual views.

To use `BufferedChatCompletionContext` within an `AssistantAgent` in a chatbot scenario:

```python
import asyncio
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        model_client=model_client,
        model_context=BufferedChatCompletionContext(buffer_size=10), # Model can only view the last 10 messages.
    )

    while True:
        user_input = input("User: ")
        if user_input == "exit":
            break
        response = await assistant.on_messages([TextMessage(content=user_input, source="user")], CancellationToken())
        print("Assistant:", response.chat_message.to_text())

    await model_client.close()

asyncio.run(main())
```


In this example, the chatbot is configured to only read the last 10 messages in the history.

### Observability and Control

In `v0.4` AgentChat, agents can be observed using the `on_messages_stream` method, which returns an async generator for streaming the agent's inner thoughts and actions. For teams, the `run_stream` method can be used to stream the internal conversation among agents. Applications can leverage these streams to observe agents and teams in real-time.

Both `on_messages_stream` and `run_stream` methods accept a `CancellationToken` parameter, enabling asynchronous cancellation of the output stream and stopping the agent or team. For teams, termination conditions can also be employed to halt the team when a specific condition is met. See Termination Condition Tutorial for more details.

Unlike `v0.2`, which included a specialized logging module, the `v0.4` API directly utilizes Python’s standard `logging` module to record events such as model client calls. More information is available in the Logging section of the Core API documentation.

### Code Executors

The code executors in `v0.2` and `v0.4` are almost identical, with the primary distinction being that `v0.4` executors support an asynchronous API. A `CancellationToken` can also be used to cancel a code execution if it becomes excessively long. Refer to the Command Line Code Executors Tutorial in the Core API documentation for further details.

Additionally, the `ACADynamicSessionsCodeExecutor` has been introduced, which facilitates code execution using Azure Container Apps (ACA) dynamic sessions. See the ACA Dynamic Sessions Code Executor Docs for more information.

---