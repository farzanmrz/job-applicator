# autogen_agentchat.agents #
This module initializes various pre-defined agents provided by the package. `BaseChatAgent` is established as the foundational base class for all agents within AgentChat.

## class AssistantAgent ##
(`name` : `str`, `model_client` : `ChatCompletionClient`, `***`, `tools` : `List[BaseTool[Any, Any] | Callable[[...], Any] | Callable[[...], Awaitable[Any]]] | None = None`, `workbench` : `Workbench | None = None`, `handoffs` : `List[Handoff | str] | None = None`, `model_context` : `ChatCompletionContext | None = None`, `description` : `str = 'An agent that provides assistance with ability to use tools.'`, `system_message` : `str | None = 'You are a helpful AI assistant. Solve tasks using your tools. Reply with TERMINATE when the task has been completed.'`, `model_client_stream` : `bool = False`, `reflect_on_tool_use` : `bool | None = None`, `tool_call_summary_format` : `str = '{result}'`, `output_content_type` : `type[BaseModel] | None = None`, `output_content_type_format` : `str | None = None`, `memory` : `Sequence[Memory] | None = None`, `metadata` : `Dict[str, str] | None = None`)
Bases: `BaseChatAgent`, `Component[AssistantAgentConfig]`

An agent designed to provide assistance, inherently equipped with the capability to utilize tools.

The `on_messages()` method delivers a `Response` where the `chat_message` encapsulates the final response message. Conversely, `on_messages_stream()` generates an asynchronous generator that produces inner messages as they are created, with the `Response` object serving as the conclusive item before the generator's closure. The `BaseChatAgent.run()` method culminates in a `TaskResult` containing the agent's produced messages, where the last message in the `messages` list signifies the ultimate response. Similarly, `BaseChatAgent.run_stream()` yields an asynchronous generator that produces inner messages incrementally, with the `TaskResult` object as the final item before the generator concludes.

### Attention ###
The caller is strictly required to pass only new messages to the agent for each invocation of `on_messages()`, `on_messages_stream()`, `BaseChatAgent.run()`, or `BaseChatAgent.run_stream()` methods. The agent intrinsically maintains its state across these method calls, eliminating the necessity to transmit the entire conversation history with every invocation.

### Warning ###
It is crucial to note that the assistant agent is neither thread-safe nor coroutine-safe. Consequently, it must not be shared among multiple tasks or coroutines, nor should its methods be invoked concurrently.

The operational flow of the assistant agent is visually represented in the following diagram:
*(Diagram content not provided in source excerpts. This indicates a placeholder for a visual element.)*

### Structured output ###
When `output_content_type` is configured, the agent will default to responding with a `StructuredMessage` rather than a `TextMessage` in its final response.

**Note**
Currently, setting `output_content_type` hinders the agent's ability to utilize `load_component` and `dump_component` methods for serializable configuration. This identified limitation is slated for future resolution.

### Tool call behavior ###
Should the model not return any tool calls, the response is immediately yielded as either a `TextMessage` or a `StructuredMessage` (when structured output is active) within `chat_message`.

When the model issues tool calls, they are executed without delay.
- If `reflect_on_tool_use` is `False`, the outcomes of the tool calls are returned as a `ToolCallSummaryMessage` in `chat_message`. The `tool_call_summary_format` parameter allows for customization of this summary.
- If `reflect_on_tool_use` is `True`, an additional model inference is performed using the tool calls and their results, with the final response presented as a `TextMessage` or `StructuredMessage` (for structured output) in `chat_message`.
- By default, `reflect_on_tool_use` is automatically set to `True` when `output_content_type` is defined.
- Conversely, `reflect_on_tool_use` is set to `False` by default when `output_content_type` is not specified.
- If the model generates multiple tool calls, they are executed concurrently. To disable parallel tool execution, the model client must be configured accordingly; for instance, by setting `parallel_tool_calls=False` for `OpenAIChatCompletionClient` and `AzureOpenAIChatCompletionClient`.

**Tip**
By default, tool call results are returned as part of the response. Therefore, it is advisable to carefully consider the formatting of tool return values, especially if another agent anticipates them in a specific format. The `tool_call_summary_format` can be utilized to customize the tool call summary as needed.

### Hand off behavior ###
If a handoff event is triggered, a `HandoffMessage` will be conveyed within `chat_message`. Any pending tool calls will be executed immediately prior to the handoff. The tool calls and their corresponding results are then relayed to the target agent via context.

**Note**
Should multiple handoffs be detected, only the first one will be executed. To circumvent this, parallel tool calls should be disabled in the model client configuration.

### Limit context size sent to the model ###
The volume of messages transmitted to the model can be regulated by assigning a `BufferedChatCompletionContext` to the `model_context` parameter. This effectively restricts the number of recent messages sent to the model, proving beneficial when the model has token processing limitations. An alternative is the `TokenLimitedChatCompletionContext`, which imposes a token limit on messages. Users can also implement custom model contexts by deriving from `ChatCompletionContext`.

### Streaming mode ###
The assistant agent supports streaming mode, activated by setting `model_client_stream=True`. In this mode, the `on_messages_stream()` and `BaseChatAgent.run_stream()` methods will also yield `ModelClientStreamingChunkEvent` messages as the model client incrementally produces portions of the response. These chunk messages are intentionally excluded from the final response's inner messages.

### Parameters ###
- **`name`** (`str`) – The designated name of the agent.
- **`model_client`** (`ChatCompletionClient`) – The model client to be utilized for inference operations.
- **`tools`** (`List[BaseTool[Any, Any] | Callable[[...], Any] | Callable[[...], Awaitable[Any]]] | None`, *optional*) – A collection of tools to be registered with the agent.
- **`workbench`** (`Workbench | None`, *optional*) – The workbench designated for the agent. It is important to note that tools cannot be used when a workbench is set, and vice versa.
- **`handoffs`** (`List[HandoffBase | str] | None`, *optional*) – Configurations for agent handoffs, enabling the agent to transfer control to other agents by responding with a `HandoffMessage`. This transfer is exclusively executed when the team is operating in Swarm mode. If a handoff is provided as a string, it is interpreted as the target agent's name.
- **`model_context`** (`ChatCompletionContext | None`, *optional*) – The model context responsible for storing and retrieving `LLMMessage` instances. It can be preloaded with initial messages, which will be cleared upon agent reset.
- **`description`** (`str`, *optional*) – A descriptive string for the agent.
- **`system_message`** (`str | None`, *optional*) – The system message provided to the model. If specified, it will be prepended to the messages within the model context during inference. Setting this to `None` disables the system message.
- **`model_client_stream`** (`bool`, *optional*) – A boolean flag indicating whether the model client should operate in streaming mode. If `True`, `on_messages_stream()` and `BaseChatAgent.run_stream()` methods will additionally yield `ModelClientStreamingChunkEvent` messages as the model client generates response chunks. Defaults to `False`.
- **`reflect_on_tool_use`** (`bool | None`, *optional*) – If `True`, the agent performs an additional model inference using the tool call and its result to formulate a response. If `False`, the tool call result is returned directly as the response. By default, this is `True` if `output_content_type` is set, and `False` otherwise.
- **`output_content_type`** (`type[BaseModel] | None`, *optional*) – The desired output content type for `StructuredMessage` responses, defined as a Pydantic model. This type will be utilized with the model client to produce structured output. If set, the agent will respond with a `StructuredMessage` instead of a `TextMessage` in the final response, unless `reflect_on_tool_use` is `False` and a tool call is made.
- **`output_content_type_format`** (`str | None`, *optional*) – (Experimental) The format string employed for the content of a `StructuredMessage` response.
- **`tool_call_summary_format`** (`str`, *optional*) – The format string used to construct the content for a `ToolCallSummaryMessage` response. This string formats the summary for each tool call result, defaulting to "{result}". When `reflect_on_tool_use` is `False`, a concatenated string of all tool call summaries, separated by a newline character (`'\n'`), will be returned as the response. Available variables for formatting include `{tool_name}`, `{arguments}`, and `{result}`. For instance, `"{tool_name}: {result}"` will generate a summary like `"tool_name: result"`.
- **`memory`** (`Sequence[Memory] | None`, *optional*) – The memory store to be employed by the agent. Defaults to `None`.
- **`metadata`** (`Dict[str, str] | None`, *optional*) – Optional metadata for tracking purposes.

### Raises ###
- **`ValueError`** – If tool names are not unique.
- **`ValueError`** – If handoff names are not unique.
- **`ValueError`** – If handoff names are not unique from tool names.
- **`ValueError`** – If the maximum number of tool iterations is less than 1.

### Examples ###

#### Example 1: basic agent ####
The following example illustrates the creation of an assistant agent with a model client and demonstrates how to generate a response for a simple task.

```python
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent

async def main() -> None:
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        # api_key="your_openai_api_key"
    )
    agent = AssistantAgent(name="assistant", model_client=model_client)
    result = await agent.run(task="Name two cities in North America.")
    print(result)

asyncio.run(main())
```

#### Example 2: model client token streaming ####
This example demonstrates how to instantiate an assistant agent with a model client and produce a token stream by setting `model_client_stream=True`.

```python
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent

async def main() -> None:
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        # api_key="your_openai_api_key"
    )
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        model_client_stream=True,
    )
    stream = agent.run_stream(task="Name two cities in North America.")
    async for message in stream:
        print(message)

asyncio.run(main())
```

Output:
```
source='user' models_usage=None metadata={} content='Name two cities in North America.' type='TextMessage'
source='assistant' models_usage=None metadata={} content='Two' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' cities' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' in' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' North' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' America' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' are' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' New' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' York' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' City' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' and' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' Toronto' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content='.' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content=' TERMIN' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=None metadata={} content='ATE' type='ModelClientStreamingChunkEvent'
source='assistant' models_usage=RequestUsage(prompt_tokens=0, completion_tokens=0) metadata={} content='Two cities in North America are New York City and Toronto. TERMINATE' type='TextMessage'
messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Name two cities in North America.', type='TextMessage'), TextMessage(source='assistant', models_usage=RequestUsage(prompt_tokens=0, completion_tokens=0), metadata={}, content='Two cities in North America are New York City and Toronto. TERMINATE', type='TextMessage')]
stop_reason=None
```

#### Example 3: agent with tools ####
The subsequent example demonstrates the creation of an assistant agent integrating a model client and a tool. It further illustrates how to generate a stream of messages for a given task and display them to the console using `Console`. The tool itself is a straightforward function returning the current time. Under the hood, this function is encapsulated within a `FunctionTool` and employed with the agent’s model client. The function’s doc string is leveraged as the tool description, its name as the tool name, and its signature, including type hints, as the tool arguments.

```python
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

async def get_current_time() -> str:
    return "The current time is 12:00 PM."

async def main() -> None:
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        # api_key="your_openai_api_key"
    )
    agent = AssistantAgent(name="assistant", model_client=model_client, tools=[get_current_time])
    await Console(agent.run_stream(task="What is the current time?"))

asyncio.run(main())
```

#### Example 4: agent with Model-Context Protocol (MCP) workbench ####
The following example showcases the creation of an assistant agent equipped with a model client and an `McpWorkbench` for facilitating interaction with a Model-Context Protocol (MCP) server.

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench

async def main() -> None:
    params = StdioServerParams(
        command="uvx",
        args=["mcp-server-fetch"],
        read_timeout_seconds=60,
    )
    # You can also use `start()` and `stop()` to manage the session.
    async with McpWorkbench(server_params=params) as workbench:
        model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
        assistant = AssistantAgent(
            name="Assistant",
            model_client=model_client,
            workbench=workbench,
            reflect_on_tool_use=True,
        )
        await Console(
            assistant.run_stream(task="Go to https://github.com/microsoft/autogen and tell me what you see.")
        )

asyncio.run(main())
```

#### Example 5: agent with structured output and tool ####
The subsequent example demonstrates how to construct an assistant agent with a model client configured for structured output and integrated with a tool. It's important to note that `FunctionTool` must be used to create the tool, and `strict=True` is a mandatory requirement for structured output mode. Given the model's configuration for structured output, the output reflection response will be delivered as a JSON-formatted string.

```python
import asyncio
from typing import Literal
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pydantic import BaseModel

# Define the structured output format.
class AgentResponse(BaseModel):
    thoughts: str
    response: Literal["happy", "sad", "neutral"]

# Define the function to be called as a tool.
def sentiment_analysis(text: str) -> str:
    """Given a text, return the sentiment."""
    return "happy" if "happy" in text else "sad" if "sad" in text else "neutral"

# Create a FunctionTool instance with `strict=True`,
# which is required for structured output mode.
tool = FunctionTool(sentiment_analysis, description="Sentiment Analysis", strict=True)

# Create an OpenAIChatCompletionClient instance that supports structured output.
model_client = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
)

# Create an AssistantAgent instance that uses the tool and model client.
agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    tools=[tool],
    system_message="Use the tool to analyze sentiment.",
    output_content_type=AgentResponse,
)

async def main() -> None:
    stream = agent.run_stream(task="I am happy today!")
    await Console(stream)

asyncio.run(main())
```

Output:
```
---------- assistant ----------
[FunctionCall(id='call_tIZjAVyKEDuijbBwLY6RHV2p', arguments='{"text":"I am happy today!"}', name='sentiment_analysis')]
---------- assistant ----------
[FunctionExecutionResult(content='happy', call_id='call_tIZjAVyKEDuijbBwLY6RHV2p', is_error=False)]
---------- assistant ----------
{"thoughts":"The user expresses a clear positive emotion by stating they are happy today, suggesting an upbeat mood.","response":"happy"}
```

#### Example 6: agent with bounded model context ####
The subsequent example illustrates the application of a `BufferedChatCompletionContext` that retains only the last two messages (one user message and one assistant message). This bounded model context proves particularly useful when the model operates under token processing limitations.

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    # Create a model client.
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        # api_key="your_openai_api_key"
    )

    # Create a model context that only keeps the last 2 messages (1 user + 1 assistant).
    model_context = BufferedChatCompletionContext(buffer_size=2)

    # Create an AssistantAgent instance with the model client and context.
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        model_context=model_context,
        system_message="You are a helpful assistant.",
    )

    result = await agent.run(task="Name two cities in North America.")
    print(result.messages[-1].content) # type: ignore

    result = await agent.run(task="My favorite color is blue.")
    print(result.messages[-1].content) # type: ignore

    result = await agent.run(task="Did I ask you any question?")
    print(result.messages[-1].content) # type: ignore

asyncio.run(main())
```

Output:
```
Two cities in North America are New York City and Toronto.
That's great! Blue is often associated with calmness and serenity. Do you have a specific shade of blue that you like, or any particular reason why it's your favorite?
No, you didn't ask a question. I apologize for any misunderstanding. If you have something specific you'd like to discuss or ask, feel free to let me know!
```

#### Example 7: agent with memory ####
The ensuing example demonstrates the integration of a list-based memory with the assistant agent. This memory is preloaded with initial content. Internally, the memory updates the model context using the `update_context()` method before an inference is made.

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_core.memory import ListMemory, MemoryContent
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    # Create a model client.
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        # api_key="your_openai_api_key"
    )

    # Create a list-based memory with some initial content.
    memory = ListMemory()
    await memory.add(MemoryContent(content="User likes pizza.", mime_type="text/plain"))
    await memory.add(MemoryContent(content="User dislikes cheese.", mime_type="text/plain"))

    # Create an AssistantAgent instance with the model client and memory.
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        memory=[memory],
        system_message="You are a helpful assistant.",
    )

    result = await agent.run(task="What is a good dinner idea?")
    print(result.messages[-1].content) # type: ignore

asyncio.run(main())
```

Output:
```
How about making a delicious pizza without cheese? You can create a flavorful veggie pizza with a variety of toppings. Here's a quick idea: **Veggie Tomato Sauce Pizza** - Start with a pizza crust (store-bought or homemade). - Spread a layer of marinara or tomato sauce evenly over the crust. - Top with your favorite vegetables like bell peppers, mushrooms, onions, olives, and spinach. - Add some protein if you’d like, such as grilled chicken or pepperoni (ensure it's cheese-free). - Sprinkle with herbs like oregano and basil, and maybe a drizzle of olive oil. - Bake according to the crust instructions until the edges are golden and the veggies are cooked. Serve it with a side salad or some garlic bread to complete the meal! Enjoy your dinner!
```

#### Example 8: agent with `o1-mini` ####
The following example illustrates how to utilize the `o1-mini` model with the assistant agent.

```python
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent

async def main() -> None:
    model_client = OpenAIChatCompletionClient(
        model="o1-mini",
        # api_key="your_openai_api_key"
    )

    # The system message is not supported by the o1 series model.
    agent = AssistantAgent(name="assistant", model_client=model_client, system_message=None)
    result = await agent.run(task="What is the capital of France?")
    print(result.messages[-1].content) # type: ignore

asyncio.run(main())
```

**Note**
The `o1-preview` and `o1-mini` models do not support system messages or function calling. Consequently, `system_message` should be set to `None`, and `tools` and `handoffs` should not be configured. Further details can be found in the o1 beta limitations documentation.

#### Example 9: agent using reasoning model with custom model context. ####
The subsequent example demonstrates the integration of a reasoning model (DeepSeek R1) with the assistant agent. A custom model context is employed to filter out the thought field from the assistant message.

```python
import asyncio
from typing import List
from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import UnboundedChatCompletionContext
from autogen_core.models import AssistantMessage, LLMMessage, ModelFamily
from autogen_ext.models.ollama import OllamaChatCompletionClient

class ReasoningModelContext(UnboundedChatCompletionContext):
    """A model context for reasoning models."""
    async def get_messages(self) -> List[LLMMessage]:
        messages = await super().get_messages()
        # Filter out thought field from AssistantMessage.
        messages_out: List[LLMMessage] = []
        for message in messages:
            if isinstance(message, AssistantMessage):
                message.thought = None
            messages_out.append(message)
        return messages_out

# Create an instance of the model client for DeepSeek R1 hosted locally on Ollama.
model_client = OllamaChatCompletionClient(
    model="deepseek-r1:8b",
    model_info={
        "vision": False,
        "function_calling": False,
        "json_output": False,
        "family": ModelFamily.R1,
        "structured_output": True,
    },
)

agent = AssistantAgent(
    "reasoning_agent",
    model_client=model_client,
    model_context=ReasoningModelContext(), # Use the custom model context.
)

async def run_reasoning_agent() -> None:
    result = await agent.run(task="What is the capital of France?")
    print(result)

asyncio.run(run_reasoning_agent())
```

### `component_config_schema` ###
alias of `AssistantAgentConfig`

### `component_provider_override` ###
`: ClassVar[str | None]` = `'autogen_agentchat.agents.AssistantAgent'`
Overrides the provider string for the component, preventing internal module names from being part of the module name.

### `async load_state` ###
(`state` : `Mapping[str, Any]`) → `None`
Loads the state of the assistant agent.

### `property model_context` ###
`: ChatCompletionContext`
Represents the model context currently in use by the agent.

### `async on_messages` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `Response`
Handles incoming messages and generates a response.

**Note**
Agents maintain their state, and therefore, messages passed to this method must be only the new messages since the last invocation. The agent is responsible for preserving its state between calls. For instance, if an agent needs to recall previous messages to formulate a response to the current message, it should store those previous messages within its internal state.

### `async on_messages_stream` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]`
Processes incoming messages with the assistant agent, yielding events or responses as they occur.

---

## class BaseChatAgent ##
(`name` : `str`, `description` : `str`)
Bases: `ChatAgent`, `ABC`, `ComponentBase[BaseModel]`

This abstract class serves as the foundational base for any chat agent. To implement a new chat agent, developers must subclass `BaseChatAgent` and provide concrete implementations for `on_messages()`, `on_reset()`, and `produced_message_types`. If streaming functionality is desired, the `on_messages_stream()` method must also be implemented.

Agents are inherently stateful, meaning they preserve their state across invocations of `on_messages()` or `on_messages_stream()`. The agent should store its state within its instance. Additionally, the `on_reset()` method must be implemented to revert the agent to its initial state.

**Note**
It is a fundamental design principle that the caller should exclusively pass new messages to the agent during each call to `on_messages()` or `on_messages_stream()`. The entire conversation history should not be passed repeatedly. This principle is paramount when designing new agents.

### `async close` ###
(`self`) → `None`
Releases any resources held by the agent. By default, this is a no-operation (`no-op`) in the `BaseChatAgent` class. Subclasses are encouraged to override this method to implement specific resource closing behaviors.

### `component_type` ###
`: ClassVar[ComponentType]` = `'agent'`
Represents the logical type of the component.

### `property description` ###
`: str`
A descriptive string for the agent. This description is instrumental for teams in making informed decisions about which agents to engage. It should clearly outline the agent’s capabilities and guidelines for interaction.

### `async load_state` ###
(`state` : `Mapping[str, Any]`) → `None`
Restores the agent from a previously saved state. This is the default implementation for stateless agents.

### `property name` ###
`: str`
The designated name of the agent. This name serves as a unique identifier within a team.

### `abstract async on_messages` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `Response`
An abstract method that handles incoming messages and provides a response.

**Note**
Agents are stateful and the messages passed to this method should be the new messages since the last call to this method. The agent should maintain its state between calls to this method. For example, if the agent needs to remember the previous messages to respond to the current message, it should store the previous messages in the agent state.

### `async on_messages_stream` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]`
Handles incoming messages and returns a stream of messages, with the final item being the response. The base implementation in `BaseChatAgent` simply invokes `on_messages()` and yields the messages contained within the response.

**Note**
Agents are stateful and the messages passed to this method should be the new messages since the last call to this method. The agent should maintain its state between calls to this method. For example, if the agent needs to remember the previous messages to respond to the current message, it should store the previous messages in the agent state.

### `async on_pause` ###
(`cancellation_token` : `CancellationToken`) → `None`
Invoked when the agent is paused while executing its `on_messages()` or `on_messages_stream()` method. By default, this is a no-operation (`no-op`) in the `BaseChatAgent` class. Subclasses have the option to override this method to implement custom pause behaviors.

### `abstract async on_reset` ###
(`cancellation_token` : `CancellationToken`) → `None`
An abstract method that resets the agent to its initialization state.

### `async on_resume` ###
(`cancellation_token` : `CancellationToken`) → `None`
Called when the agent resumes from a pause while executing its `on_messages()` or `on_messages_stream()` method. By default, this is a no-operation (`no-op`) in the `BaseChatAgent` class. Subclasses can override this method to implement custom resume behaviors.

### `abstract property produced_message_types` ###
`: Sequence[type[BaseChatMessage]]`
An abstract property indicating the types of messages that the agent produces within the `Response.chat_message` field. These types must be `BaseChatMessage` types.

### `async run` ###
(`***`, `task` : `str | BaseChatMessage | Sequence[BaseChatMessage] | None = None`, `cancellation_token` : `CancellationToken | None = None`) → `TaskResult`
Executes the agent with the specified task and returns the resulting `TaskResult`.

### `async run_stream` ###
(`***`, `task` : `str | BaseChatMessage | Sequence[BaseChatMessage] | None = None`, `cancellation_token` : `CancellationToken | None = None`) → `AsyncGenerator[BaseAgentEvent | BaseChatMessage | TaskResult, None]`
Executes the agent with the specified task and returns a stream of messages, with the final `TaskResult` as the last item in the stream.

### `async save_state` ###
(`self`) → `Mapping[str, Any]`
Exports the current state of the agent. This is the default implementation for stateless agents.

---

## class CodeExecutorAgent ##
(`name` : `str`, `code_executor` : `CodeExecutor`, `***`, `model_client` : `ChatCompletionClient | None = None`, `model_context` : `ChatCompletionContext | None = None`, `model_client_stream` : `bool = False`, `max_retries_on_error` : `int = 0`, `description` : `str | None = None`, `system_message` : `str | None = DEFAULT_SYSTEM_MESSAGE`, `sources` : `Sequence[str] | None = None`)
Bases: `BaseChatAgent`, `Component[CodeExecutorAgentConfig]`

(Experimental) An agent capable of generating and executing code snippets based on user instructions.

**Note**
This agent is currently experimental, and its API may undergo changes in future releases.

It is typically deployed either within a team alongside another agent responsible for code generation, or as a standalone agent. When used independently with a `model_client` provided, it can autonomously generate code based on user queries, execute it, and reflect on the execution results. The model will also reflect on the code execution results. The agent will yield the final reflection result from the model as the final response.

When invoked without a `model_client`, its functionality is limited to executing code blocks found within `TextMessage` messages, returning only the output of the code execution.

**Note**
An alternative to this agent is employing `AssistantAgent` with `PythonCodeExecutionTool`. However, this approach requires the model for that agent to generate properly escaped code strings as parameters for the tool.

### Parameters ###
- **`name`** (`str`) – The designated name of the agent.
- **`code_executor`** (`CodeExecutor`) – The code executor responsible for executing code received in messages (DockerCommandLineCodeExecutor is recommended).
- **`model_client`** (`ChatCompletionClient`, *optional*) – The model client to be utilized for inference and code generation. If not provided, the agent will only execute code blocks present in input messages. Currently, the model must inherently support structured output mode, a prerequisite for the automatic retry mechanism.
- **`model_client_stream`** (`bool`, *optional*) – A boolean flag indicating whether the model client should operate in streaming mode. If `True`, `on_messages_stream()` and `BaseChatAgent.run_stream()` methods will additionally yield `ModelClientStreamingChunkEvent` messages as the model client generates response chunks. Defaults to `False`.
- **`description`** (`str`, *optional*) – A descriptive string for the agent. If not provided, `DEFAULT_AGENT_DESCRIPTION` will be used.
- **`system_message`** (`str`, *optional`) – The system message provided to the model. If specified, it will be prepended to the messages within the model context during inference. Setting this to `None` disables the system message. Defaults to `DEFAULT_SYSTEM_MESSAGE`. This parameter is only utilized if `model_client` is provided.
- **`sources`** (`Sequence[str] | None`, *optional*) – A sequence of agent names from which to check messages for code to execute. This is particularly useful in group chat scenarios where code execution should be restricted to messages from specific agents. If not provided, all messages will be scanned for code blocks. This parameter is only utilized if `model_client` is not provided.
- **`max_retries_on_error`** (`int`, *optional*) – The maximum number of retry attempts in case of code execution errors. If code execution fails after this number of retries, the agent will yield a reflection result.

**Note**
It is highly recommended that the `CodeExecutorAgent` utilizes a Docker container for code execution. This practice guarantees that model-generated code is executed within an isolated environment, enhancing security and preventing unintended system modifications. To leverage Docker, your environment must have Docker installed and actively running. Follow the official Docker installation instructions to set up your environment.

**Note**
The code executor exclusively processes code that is correctly formatted within markdown code blocks using triple backticks. For example:
```python
print("Hello World")
```
# or
```sh
echo "Hello World"
```

In this example, we demonstrate how to configure a `CodeExecutorAgent` that leverages the `DockerCommandLineCodeExecutor` to execute code snippets within a Docker container. The `work_dir` parameter specifies the local directory where all executed files are initially saved before being transferred to and executed within the Docker container.

```python
import asyncio
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_core import CancellationToken

async def run_code_executor_agent() -> None:
    # Create a code executor agent that uses a Docker container to execute code.
    code_executor = DockerCommandLineCodeExecutor(work_dir="coding")
    await code_executor.start()

    code_executor_agent = CodeExecutorAgent("code_executor", code_executor=code_executor)

    # Run the agent with a given code snippet.
    task = TextMessage(
        content='''Here is some code
```python
print('Hello world')
```
''',
        source="user",
    )
    response = await code_executor_agent.on_messages([task], CancellationToken())
    print(response.chat_message)

    # Stop the code executor.
    await code_executor.stop()

asyncio.run(run_code_executor_agent())
```

In this example, we illustrate the setup of a `CodeExecutorAgent` that utilizes `DeviceRequest` to expose a GPU to the container, enabling CUDA-accelerated code execution.

```python
import asyncio
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_core import CancellationToken
from docker.types import DeviceRequest

async def run_code_executor_agent() -> None:
    # Create a code executor agent that uses a Docker container to execute code.
    code_executor = DockerCommandLineCodeExecutor(
        work_dir="coding",
        device_requests=[DeviceRequest(count=-1, capabilities=[["gpu"]])]
    )
    await code_executor.start()

    code_executor_agent = CodeExecutorAgent("code_executor", code_executor=code_executor)

    # Display the GPU information
    task = TextMessage(
        content='''Here is some code
```bash
nvidia-smi
```
''',
        source="user",
    )
    response = await code_executor_agent.on_messages([task], CancellationToken())
    print(response.chat_message)

    # Stop the code executor.
    await code_executor.stop()

asyncio.run(run_code_executor_agent())
```

In the subsequent example, we demonstrate how to configure `CodeExecutorAgent` without the `model_client` parameter. This setup allows it to execute code blocks generated by other agents within a group chat, leveraging `DockerCommandLineCodeExecutor`.

```python
import asyncio
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

termination_condition = MaxMessageTermination(3)

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    # define the Docker CLI Code Executor
    code_executor = DockerCommandLineCodeExecutor(work_dir="coding")

    # start the execution container
    await code_executor.start()

    code_executor_agent = CodeExecutorAgent("code_executor_agent", code_executor=code_executor)
    coder_agent = AssistantAgent("coder_agent", model_client=model_client)

    groupchat = RoundRobinGroupChat(
        participants=[coder_agent, code_executor_agent],
        termination_condition=termination_condition
    )

    task = "Write python code to print Hello World!"
    await Console(groupchat.run_stream(task=task))

    # stop the execution container
    await code_executor.stop()

asyncio.run(main())
```

Output:
```
---------- user ----------
Write python code to print Hello World!
---------- coder_agent ----------
Certainly! Here's a simple Python code to print "Hello World!":
```python
print("Hello World!")
```
You can run this code in any Python environment to display the message.
---------- code_executor_agent ----------
Hello World!
```

In the following example, we illustrate the setup of `CodeExecutorAgent` with a `model_client`. This configuration enables it to autonomously generate its own code without reliance on other agents, executing it within `DockerCommandLineCodeExecutor`.

```python
import asyncio
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_agentchat.conditions import TextMessageTermination
from autogen_agentchat.ui import Console

termination_condition = TextMessageTermination("code_executor_agent")

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    # define the Docker CLI Code Executor
    code_executor = DockerCommandLineCodeExecutor(work_dir="coding")

    # start the execution container
    await code_executor.start()

    code_executor_agent = CodeExecutorAgent(
        "code_executor_agent",
        code_executor=code_executor,
        model_client=model_client
    )

    task = "Write python code to print Hello World!"
    await Console(code_executor_agent.run_stream(task=task))

    # stop the execution container
    await code_executor.stop()

asyncio.run(main())
```

Output:
```
---------- user ----------
Write python code to print Hello World!
---------- code_executor_agent ----------
Certainly! Here is a simple Python code to print "Hello World!" to the console:
```python
print("Hello World!")
```
Let's execute it to confirm the output.
---------- code_executor_agent ----------
Hello World!
---------- code_executor_agent ----------
The code has been executed successfully, and it printed "Hello World!" as expected. If you have any more requests or questions, feel free to ask!
```

`DEFAULT_AGENT_DESCRIPTION` = `'A Code Execution Agent that generates and executes Python and shell scripts based on user instructions. Python code should be provided in ```python code blocks, and sh shell scripts should be provided in ```sh code blocks for execution. It ensures correctness, efficiency, and minimal errors while gracefully handling edge cases.'`
`DEFAULT_SYSTEM_MESSAGE` = `'You are a Code Execution Agent. Your role is to generate and execute Python code based on user instructions, ensuring correctness, efficiency, and minimal errors. Handle edge cases gracefully.'`
`DEFAULT_TERMINAL_DESCRIPTION` = `'A computer terminal that performs no other action than running Python scripts (provided to it quoted in ```python code blocks), or sh shell scripts (provided to it quoted in ```sh code blocks).'`
`NO_CODE_BLOCKS_FOUND_MESSAGE` = `'No code blocks found in the thread. Please provide at least one markdown-encoded code block to execute (i.e., quoting code in ```python or ```sh code blocks).'`

### `classmethod _from_config` ###
(`*config` : `CodeExecutorAgentConfig`) → `Self`
Instantiates a new component from a configuration object.

### Parameters ###
- **`config`** (`T`) – The configuration object.

### Returns ###
- **`Self`** – The newly created instance of the component.

### `_to_config` ###
(`self`) → `CodeExecutorAgentConfig`
Generates the configuration required to create a new instance of a component that matches the current instance's configuration.

### Returns ###
- **`T`** – The configuration of the component.

### `component_config_schema` ###
alias of `CodeExecutorAgentConfig`

### `component_provider_override` ###
`: ClassVar[str | None]` = `'autogen_agentchat.agents.CodeExecutorAgent'`
Overrides the provider string for the component. This is used to prevent internal module names from becoming part of the module name.

### `async execute_code_block` ###
(`code_blocks` : `List[CodeBlock]`, `cancellation_token` : `CancellationToken`) → `CodeResult`

### `async extract_code_blocks_from_messages` ###
(`messages` : `Sequence[BaseChatMessage]`) → `List[CodeBlock]`

### `property model_context` ###
`: ChatCompletionContext`
The model context currently in use by the agent.

### `async on_messages` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `Response`
Handles incoming messages and returns a response.

**Note**
Agents are stateful and the messages passed to this method should be the new messages since the last call to this method. The agent should maintain its state between calls to this method. For example, if the agent needs to remember the previous messages to respond to the current message, it should store the previous messages in the agent state.

### `async on_messages_stream` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]`
Processes the incoming messages with the assistant agent, yielding events or responses as they occur.

### `async on_reset` ###
(`cancellation_token` : `CancellationToken`) → `None`
This is a no-operation (`no-op`) as the code executor agent inherently lacks mutable state.

### `property produced_message_types` ###
`: Sequence[type[BaseChatMessage]]`
The types of messages that the code executor agent generates.

---

## class MessageFilterAgent ##
(`name` : `str`, `wrapped_agent` : `BaseChatAgent`, `filter` : `MessageFilterConfig`)
Bases: `BaseChatAgent`, `Component[MessageFilterAgentConfig]`
A wrapper agent designed to filter incoming messages before they are passed to the underlying inner agent.

### Warning ###
This feature is currently experimental, and its API is subject to modifications in future releases.

This agent proves valuable in complex scenarios, such as multi-agent workflows, where an agent should process only a specific subset of the complete message history. For example, it can be configured to process only the most recent message from each upstream agent, or exclusively the first message from a particular source.

Message filtering is configured through `MessageFilterConfig`, offering capabilities such as:
- Filtering based on the message source (e.g., messages originating solely from "user" or another specific agent).
- Selecting the first N or last N messages from each source.
- If `position` is `None`, all messages from that source are included.

This agent exhibits compatibility with both direct message passing paradigms and team-based execution frameworks like `GraphFlow`.

### Example ###
```python
>>> agent_a = MessageFilterAgent(
... name="A",
... wrapped_agent=some_other_agent,
... filter=MessageFilterConfig(
... per_source=[
... PerSourceFilter(source="user", position="first", count=1),
... PerSourceFilter(source="B", position="last", count=2),
... ]
... ),
... )
```

### Example use case with Graph: ###
Consider a looping multi-agent graph structured as: A → B → A → B → C.
Desired filtering behavior:
- Agent A should only receive the user message and the most recent message from Agent B.
- Agent B should receive the user message, the most recent message from Agent A, and its own previous 10 responses (for reflection purposes).
- Agent C should only receive the user message and the most recent message from Agent B.

Wrap the agents as follows to achieve this:

```python
>>> agent_a = MessageFilterAgent(
... name="A",
... wrapped_agent=agent_a_inner,
... filter=MessageFilterConfig(
... per_source=[
... PerSourceFilter(source="user", position="first", count=1),
... PerSourceFilter(source="B", position="last", count=1),
... ]
... ),
... )
>>> agent_b = MessageFilterAgent(
... name="B",
... wrapped_agent=agent_b_inner,
... filter=MessageFilterConfig(
... per_source=[
... PerSourceFilter(source="user", position="first", count=1),
... PerSourceFilter(source="A", position="last", count=1),
... PerSourceFilter(source="B", position="last", count=10),
... ]
... ),
... )
>>> agent_c = MessageFilterAgent(
... name="C",
... wrapped_agent=agent_c_inner,
... filter=MessageFilterConfig(
... per_source=[
... PerSourceFilter(source="user", position="first", count=1),
... PerSourceFilter(source="B", position="last", count=1),
... ]
... ),
... )
```

Subsequently, define the graph structure:

```python
>>> graph = DiGraph(
... nodes={
... "A": DiGraphNode(name="A", edges=[DiGraphEdge(target="B")]),
... "B": DiGraphNode(
... name="B",
... edges=[
... DiGraphEdge(target="C", condition="exit"),
... DiGraphEdge(target="A", condition="loop"),
... ],
... ),
... "C": DiGraphNode(name="C", edges=[]),
... },
... default_start_node="A",
... )
```

This configuration guarantees that each agent receives only the information essential for its decision-making or action logic.

### `classmethod _from_config` ###
(`*config` : `MessageFilterAgentConfig`) → `MessageFilterAgent`
Instantiates a new component from a configuration object.

### Parameters ###
- **`config`** (`T`) – The configuration object.

### Returns ###
- **`Self`** – The newly created instance of the component.

### `_to_config` ###
(`self`) → `MessageFilterAgentConfig`
Generates the configuration required to create a new instance of a component that matches the current instance's configuration.

### Returns ###
- **`T`** – The configuration of the component.

### `component_config_schema` ###
alias of `MessageFilterAgentConfig`

### `component_provider_override` ###
`: ClassVar[str | None]` = `'autogen_agentchat.agents.MessageFilterAgent'`
Overrides the provider string for the component, preventing internal module names from being part of the module name.

### `async on_messages` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `Response`
Handles incoming messages and returns a response.

**Note**
Agents are stateful and the messages passed to this method should be the new messages since the last call to this method. The agent should maintain its state between calls to this method. For example, if the agent needs to remember the previous messages to respond to the current message, it should store the previous messages in the agent state.

### `async on_messages_stream` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]`
Handles incoming messages and returns a stream of messages, with the final item being the response. The base implementation in `BaseChatAgent` simply invokes `on_messages()` and yields the messages within the response.

**Note**
Agents are stateful and the messages passed to this method should be the new messages since the last call to this method. The agent should maintain its state between calls to this method. For example, if the agent needs to remember the previous messages to respond to the current message, it should store the previous messages in the agent state.

### `async on_reset` ###
(`cancellation_token` : `CancellationToken`) → `None`
Resets the agent to its initialization state.

### `property produced_message_types` ###
`: Sequence[type[BaseChatMessage]]`
The types of messages that the agent produces within the `Response.chat_message` field. These types must be `BaseChatMessage` types.

### `pydantic model MessageFilterConfig` ###

Bases: `BaseModel`

Show JSON schema:
```json
{
  "title": "MessageFilterConfig",
  "type": "object",
  "properties": {
    "per_source": {
      "items": {
        "$ref": "#/$defs/PerSourceFilter"
      },
      "title": "Per Source",
      "type": "array"
    }
  },
  "$defs": {
    "PerSourceFilter": {
      "properties": {
        "source": {
          "title": "Source",
          "type": "string"
        },
        "position": {
          "anyOf": [
            {
              "enum": [
                "first",
                "last"
              ],
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Position"
        },
        "count": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Count"
        }
      },
      "required": [
        "source"
      ],
      "title": "PerSourceFilter",
      "type": "object"
    }
  },
  "required": [
    "per_source"
  ]
}
```

### Fields ###
- `per_source` (`List[autogen_agentchat.agents._message_filter_agent.PerSourceFilter]`)

### `field per_source` ###
`: List[PerSourceFilter]` [Required]

### `pydantic model PerSourceFilter` ###

Bases: `BaseModel`

Show JSON schema:
```json
{
  "title": "PerSourceFilter",
  "type": "object",
  "properties": {
    "source": {
      "title": "Source",
      "type": "string"
    },
    "position": {
      "anyOf": [
        {
          "enum": [
            "first",
            "last"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Position"
    },
    "count": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Count"
    }
  },
  "required": [
    "source"
  ]
}
```

### Fields ###
- `count` (`int | None`)
- `position` (`Literal['first', 'last'] | None`)
- `source` (`str`)

### `field count` ###
`: int | None` = `None`

### `field position` ###
`: Literal['first', 'last'] | None` = `None`

### `field source` ###
`: str` [Required]

---

## class SocietyOfMindAgent ##
(`name` : `str`, `team` : `Team`, `model_client` : `ChatCompletionClient`, `***`, `description` : `str = DEFAULT_DESCRIPTION`, `instruction` : `str = DEFAULT_INSTRUCTION`, `response_prompt` : `str = DEFAULT_RESPONSE_PROMPT`, `model_context` : `ChatCompletionContext | None = None`)
Bases: `BaseChatAgent`, `Component[SocietyOfMindAgentConfig]`

An agent that orchestrates an inner team of agents to generate responses. Each time the agent's `on_messages()` or `on_messages_stream()` method is invoked, it initiates the inner team's operation. Subsequently, it leverages the model client to formulate a response based on the messages exchanged within the inner team. Once the response is generated, the agent resets the inner team by calling `Team.reset()`.

### Limit context size sent to the model ###
The volume of messages transmitted to the model can be regulated by assigning a `BufferedChatCompletionContext` to the `model_context` parameter. This effectively restricts the number of recent messages sent to the model, proving beneficial when the model has token processing limitations. Users can also implement custom model contexts by deriving from `ChatCompletionContext`.

### Parameters ###
- **`name`** (`str`) – The designated name of the agent.
- **`team`** (`Team`) – The team of agents to be utilized.
- **`model_client`** (`ChatCompletionClient`) – The model client employed for preparing responses.
- **`description`** (`str`, *optional*) – A descriptive string for the agent.
- **`instruction`** (`str`, *optional`) – The instruction to be employed when generating a response using the inner team's messages. Defaults to `DEFAULT_INSTRUCTION`. This instruction assumes the role of 'system'.
- **`response_prompt`** (`str`, *optional*) – The response prompt to be employed when generating a response using the inner team's messages. Defaults to `DEFAULT_RESPONSE_PROMPT`. This prompt assumes the role of 'system'.
- **`model_context`** (`ChatCompletionContext | None`, *optional*) – The model context for storing and retrieving `LLMMessage` instances. It can be preloaded with initial messages, which will be cleared upon agent reset.

### Example ###
```python
import asyncio
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent, SocietyOfMindAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    agent1 = AssistantAgent("assistant1", model_client=model_client, system_message="You are a writer, write well.")
    agent2 = AssistantAgent(
        "assistant2",
        model_client=model_client,
        system_message="You are an editor, provide critical feedback. Respond with 'APPROVE' if the text addresses all feedbacks.",
    )

    inner_termination = TextMentionTermination("APPROVE")
    inner_team = RoundRobinGroupChat([agent1, agent2], termination_condition=inner_termination)

    society_of_mind_agent = SocietyOfMindAgent("society_of_mind", team=inner_team, model_client=model_client)

    agent3 = AssistantAgent(
        "assistant3",
        model_client=model_client,
        system_message="Translate the text to Spanish."
    )

    team = RoundRobinGroupChat([society_of_mind_agent, agent3], max_turns=2)

    stream = team.run_stream(task="Write a short story with a surprising ending.")
    await Console(stream)

asyncio.run(main())
```

`DEFAULT_DESCRIPTION` = `'An agent that uses an inner team of agents to generate responses.'`
The default description for a `SocietyOfMindAgent`.

### Type ###
`str`

`DEFAULT_INSTRUCTION` = `'Earlier you were asked to fulfill a request. You and your team worked diligently to address that request. Here is a transcript of that conversation:'`
The default instruction utilized when generating a response based on the inner team’s messages. This instruction will be prepended to the inner team’s messages during response generation using the model. It assumes the role of ‘system’.

### Type ###
`str`

`DEFAULT_RESPONSE_PROMPT` = `'Output a standalone response to the original request, without mentioning any of the intermediate discussion.'`
The default response prompt employed when generating a response using the inner team’s messages. It assumes the role of ‘system’.

### Type ###
`str`

### `classmethod _from_config` ###
(`*config` : `SocietyOfMindAgentConfig`) → `Self`
Instantiates a new component from a configuration object.

### Parameters ###
- **`config`** (`T`) – The configuration object.

### Returns ###
- **`Self`** – The newly created instance of the component.

### `_to_config` ###
(`self`) → `SocietyOfMindAgentConfig`
Generates the configuration required to create a new instance of a component that matches the current instance's configuration.

### Returns ###
- **`T`** – The configuration of the component.

### `component_config_schema` ###
alias of `SocietyOfMindAgentConfig`

### `component_provider_override` ###
`: ClassVar[str | None]` = `'autogen_agentchat.agents.SocietyOfMindAgent'`
Overrides the provider string for the component, preventing internal module names from being part of the module name.

### `async load_state` ###
(`state` : `Mapping[str, Any]`) → `None`
Restores the agent from a previously saved state. This is the default implementation for stateless agents.

### `property model_context` ###
`: ChatCompletionContext`
The model context currently in use by the agent.

### `async on_messages` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `Response`
Handles incoming messages and returns a response.

**Note**
Agents are stateful and the messages passed to this method should be the new messages since the last call to this method. The agent should maintain its state between calls to this method. For example, if the agent needs to remember the previous messages to respond to the current message, it should store the previous messages in the agent state.

### `async on_messages_stream` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]`
Handles incoming messages and returns a stream of messages, with the final item being the response. The base implementation in `BaseChatAgent` simply invokes `on_messages()` and yields the messages within the response.

**Note**
Agents are stateful and the messages passed to this method should be the new messages since the last call to this method. The agent should maintain its state between calls to this method. For example, if the agent needs to remember the previous messages to respond to the current message, it should store the previous messages in the agent state.

### `async on_reset` ###
(`cancellation_token` : `CancellationToken`) → `None`
Resets the agent to its initialization state.

### `property produced_message_types` ###
`: Sequence[type[BaseChatMessage]]`
The types of messages that the agent produces within the `Response.chat_message` field. These types must be `BaseChatMessage` types.

### `async save_state` ###
(`self`) → `Mapping[str, Any]`
Exports the current state of the agent. This is the default implementation for stateless agents.

---

## class UserProxyAgent ##
(`name` : `str`, `***`, `description` : `str = 'A human user'`, `input_func` : `Callable[[str], str] | Callable[[str, CancellationToken | None], Awaitable[str]] | None = None`)
Bases: `BaseChatAgent`, `Component[UserProxyAgentConfig]`
An agent designed to represent a human user through the provision of an input function. This agent facilitates the integration of human user interaction within a chat system by accepting a custom input function.

**Note**
Utilizing `UserProxyAgent` places a running team into a temporary blocked state until the user provides a response. Therefore, it is crucial to implement a timeout for the user input function and to cancel the operation using `CancellationToken` if the user fails to respond within the allotted time. The input function should also be robust enough to handle exceptions and return a default response if necessary.

For typical use cases involving slow human responses, it is advisable to employ termination conditions such as `HandoffTermination` or `SourceMatchTermination` to halt the running team and return control to the application. The team can then be resumed once the user provides input. This approach allows for the preservation and restoration of the team's state upon user response.

For further details, consult the "Human-in-the-loop" documentation.

### Parameters ###
- **`name`** (`str`) – The designated name of the agent.
- **`description`** (`str`, *optional*) – A descriptive string for the agent.
- **`input_func`** (`Optional[Callable[[str], str] | Callable[[str, Optional[CancellationToken]], Awaitable[str]]]`) – A function that accepts a prompt and returns a user input string.

For examples of integrating with web and UI frameworks, refer to the following:
- FastAPI
- ChainLit

### Example ###
Simple usage case:
```python
import asyncio
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage

async def simple_user_agent():
    agent = UserProxyAgent("user_proxy")
    response = await asyncio.create_task(
        agent.on_messages(
            [TextMessage(content="What is your name? ", source="user")],
            cancellation_token=CancellationToken(),
        )
    )
    assert isinstance(response.chat_message, TextMessage)
    print(f"Your name is {response.chat_message.content}")
```

### Example ###
Cancellable usage case:
```python
import asyncio
from typing import Any
from autogen_core import CancellationToken
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.messages import TextMessage

token = CancellationToken()
agent = UserProxyAgent("user_proxy")

async def timeout(delay: float):
    await asyncio.sleep(delay)

def cancellation_callback(task: asyncio.Task[Any]):
    token.cancel()

async def cancellable_user_agent():
    try:
        timeout_task = asyncio.create_task(timeout(3))
        timeout_task.add_done_callback(cancellation_callback)

        agent_task = asyncio.create_task(
            agent.on_messages(
                [TextMessage(content="What is your name? ", source="user")],
                cancellation_token=token,
            )
        )
        response = await agent_task
        assert isinstance(response.chat_message, TextMessage)
        print(f"Your name is {response.chat_message.content}")
    except Exception as e:
        print(f"Exception: {e}")
    except BaseException as e:
        print(f"BaseException: {e}")
```

## class InputRequestContext ##
Bases: `object`

### `classmethod request_id` ###
(`self`) → `str`

### `classmethod _from_config` ###
(`*config` : `UserProxyAgentConfig`) → `Self`
Instantiates a new component from a configuration object.

### Parameters ###
- **`config`** (`T`) – The configuration object.

### Returns ###
- **`Self`** – The newly created instance of the component.

### `_to_config` ###
(`self`) → `UserProxyAgentConfig`
Generates the configuration required to create a new instance of a component that matches the current instance's configuration.

### Returns ###
- **`T`** – The configuration of the component.

### `component_config_schema` ###
alias of `UserProxyAgentConfig`

### `component_provider_override` ###
`: ClassVar[str | None]` = `'autogen_agentchat.agents.UserProxyAgent'`
Overrides the provider string for the component, preventing internal module names from being part of the module name.

### `component_type` ###
`: ClassVar[ComponentType]` = `'agent'`
The logical type of the component.

### `async on_messages` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `Response`
Handles incoming messages and returns a response.

**Note**
Agents are stateful and the messages passed to this method should be the new messages since the last call to this method. The agent should maintain its state between calls to this method. For example, if the agent needs to remember the previous messages to respond to the current message, it should store the previous messages in the agent state.

### `async on_messages_stream` ###
(`messages` : `Sequence[BaseChatMessage]`, `cancellation_token` : `CancellationToken`) → `AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]`
Handles incoming messages by requesting user input.

### `async on_reset` ###
(`cancellation_token` : `CancellationToken | None` = `None`) → `None`
Resets the agent's state.

### `property produced_message_types` ###
`: Sequence[type[BaseChatMessage]]`
The types of messages that this agent is capable of producing.

---