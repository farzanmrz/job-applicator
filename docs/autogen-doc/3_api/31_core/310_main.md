Commencing the meticulous conversion of the provided web documentation excerpts into a singular, comprehensive markdown file, ensuring precise mirroring of the original content and structure, inclusion of all textual components, explanations, and code examples, accurate representation of class and function definitions with their associated parameters and intricate details, and ultimately, delivering a clean, well-organized, and LLM-ready output.

---

```markdown
Skip to main contentCtrl + K
*   0.2 Docs
*   GitHub
*   Discord
*   Twitter
*   GitHub
*   Discord
*   Twitter

### autogen_core

*class* **Agent** (*args*, ***kwargs*) [source]#
Bases: `Protocol`

*property* **metadata**: `AgentMetadata`
Metadata of the agent.

*property* **id**: `AgentId`
ID of the agent.

*async* **bind_id_and_runtime** (id : `AgentId`, runtime : `AgentRuntime`) → `None` [source]#
Function used to bind an Agent instance to an `AgentRuntime`.
Parameters :
*   **agent_id** (`AgentId`) – ID of the agent.
*   **runtime** (`AgentRuntime`) – AgentRuntime instance to bind the agent to.

*async* **on_message** (message : `Any`, ctx : `MessageContext`) → `Any` [source]#
Message handler for the agent. This should only be called by the runtime, not by other agents.
Parameters :
*   **message** (`Any`) – Received message. Type is one of the types in `subscriptions`.
*   **ctx** (`MessageContext`) – Context of the message.
Returns :
*   **Any** – Response to the message. Can be None.
Raises :
*   **CancelledError** – If the message was cancelled.
*   **CantHandleException** – If the agent cannot handle the message.

*async* **save_state** () → `Mapping[str, Any]` [source]#
Save the state of the agent. The result must be JSON serializable.

*async* **load_state** (state : `Mapping[str, Any]`) → `None` [source]#
Load in the state of the agent obtained from `save_state`.
Parameters :
*   **state** (`Mapping[str, Any]`) – State of the agent. Must be JSON serializable.

*async* **close** () → `None` [source]#
Called when the runtime is closed

*class* **AgentId** (type : `str`| `AgentType`, key : `str`) [source]#
Agent ID uniquely identifies an agent instance within an agent runtime - including distributed runtime. It is the ‘address’ of the agent instance for receiving messages.

See here for more information: Agent Identity and Lifecycle

*classmethod* **from_str** (agent_id : `str`) → `Self` [source]#
Convert a string of the format `type/key` into an AgentId

*property* **type**: `str`
An identifier that associates an agent with a specific factory function.
Strings may only be composed of alphanumeric letters (a-z) and (0-9), or underscores (_).

*property* **key**: `str`
Agent instance identifier.
Strings may only be composed of alphanumeric letters (a-z) and (0-9), or underscores (_).

*class* **AgentProxy** (agent : `AgentId`, runtime : `AgentRuntime`) [source]#

A helper class that allows you to use an AgentId in place of its associated Agent

*property* **id**: `AgentId`
Target agent for this proxy

*property* **metadata**: `Awaitable[AgentMetadata]`
Metadata of the agent.

*async* **send_message** (message : `Any`, ***, sender : `AgentId`, cancellation_token : `CancellationToken`| `None` = `None`, message_id : `str`| `None` = `None`) → `Any` [source]#

*async* **save_state** () → `Mapping[str, Any]` [source]#
Save the state of the agent. The result must be JSON serializable.

*async* **load_state** (state : `Mapping[str, Any]`) → `None` [source]#
Load in the state of the agent obtained from `save_state`.

Parameters :
*   **state** (`Mapping[str, Any]`) – State of the agent. Must be JSON serializable.

*class* **AgentMetadata** [source]#
Bases: `TypedDict`

type: `str`
key: `str`
description: `str`

*class* **AgentRuntime** (*args*, ***kwargs*) [source]#
Bases: `Protocol`

*async* **send_message** (message : `Any`, recipient : `AgentId`, ***, sender : `AgentId`| `None` = `None`, cancellation_token : `CancellationToken`| `None` = `None`, message_id : `str`| `None` = `None`) → `Any` [source]#
Send a message to an agent and get a response.
Parameters :
*   **message** (`Any`) – The message to send.

*   **recipient** (`AgentId`) – The agent to send the message to.
*   **sender** (`AgentId` | `None`, *optional*) – Agent which sent the message. Should **only** be None if this was sent from no agent, such as directly to the runtime externally. Defaults to None.
*   **cancellation_token** (`CancellationToken` | `None`, *optional*) – Token used to cancel an in progress. Defaults to None.
Raises :
*   **CantHandleException** – If the recipient cannot handle the message.
*   **UndeliverableException** – If the message cannot be delivered.
*   **Other** – Any other exception raised by the recipient.

Returns :
*   **Any** – The response from the agent.

*async* **publish_message** (message : `Any`, topic_id : `TopicId`, ***, sender : `AgentId`| `None` = `None`, cancellation_token : `CancellationToken`| `None` = `None`, message_id : `str`| `None` = `None`) → `None` [source]#
Publish a message to all agents in the given namespace, or if no namespace is provided, the namespace of the sender.
No responses are expected from publishing.
Parameters :
*   **message** (`Any`) – The message to publish.
*   **topic_id** (`TopicId`) – The topic to publish the message to.

*   **sender** (`AgentId` | `None`, *optional*) – The agent which sent the message. Defaults to None.
*   **cancellation_token** (`CancellationToken` | `None`, *optional*) – Token used to cancel an in progress. Defaults to None.
*   **message_id** (`str` | `None`, *optional*) – The message id. If None, a new message id will be generated. Defaults to None. This message id must be unique. and is recommended to be a UUID.
Raises :
*   **UndeliverableException** – If the message cannot be delivered.

*async* **register_factory** (type : `str`| `AgentType`, agent_factory : `Callable[ [ ] , T | Awaitable[T] ]`, ***, expected_class : `type[T]` | `None` = `None`) → `AgentType` [source]#
Register an agent factory with the runtime associated with a specific type. The type must be unique. This API does not add any subscriptions.

Note
This is a low level API and usually the agent class’s `register` method should be used instead, as this also handles subscriptions automatically.
Example:
```python
from dataclasses import dataclass
from autogen_core import AgentRuntime, MessageContext, RoutedAgent, event
from autogen_core.models import UserMessage

@dataclass
class MyMessage:
    content: str

class MyAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("My core agent")

    @event
    async def handler(self, message: UserMessage, context: MessageContext) -> None:
        print("Event received: ", message.content)

async def my_agent_factory():
    return MyAgent()

async def main() -> None:
    runtime: AgentRuntime = ... # type: ignore
    await runtime.register_factory("my_agent", lambda: MyAgent())

import asyncio
asyncio.run(main())
```
Parameters :

*   **type** (`str`) – The type of agent this factory creates. It is not the same as agent class name. The `type` parameter is used to differentiate between different factory functions rather than agent classes.
*   **agent_factory** (`Callable[ [ ] , T ]`) – The factory that creates the agent, where T is a concrete Agent type. Inside the factory, use `autogen_core.AgentInstantiationContext` to access variables like the current runtime and agent ID.
*   **expected_class** (`type[T]` | `None`, *optional*) – The expected class of the agent, used for runtime validation of the factory. Defaults to None. If None, no validation is performed.

*async* **register_agent_instance** (agent_instance : `Agent`, agent_id : `AgentId`) → `AgentId` [source]#
Register an agent instance with the runtime. The type may be reused, but each agent_id must be unique. All agent instances within a type must be of the same object type. This API does not add any subscriptions.
Note
This is a low level API and usually the agent class’s `register_instance` method should be used instead, as this also handles subscriptions automatically.
Example:
```python
from dataclasses import dataclass
from autogen_core import AgentId, AgentRuntime, MessageContext, RoutedAgent, event
from autogen_core.models import UserMessage

@dataclass
class MyMessage:
    content: str

class MyAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("My core agent")

    @event
    async def handler(self, message: UserMessage, context: MessageContext) -> None:
        print("Event received: ", message.content)

async def main() -> None:
    runtime: AgentRuntime = ... # type: ignore
    agent = MyAgent()
    await runtime.register_agent_instance(
        agent_instance = agent,
        agent_id = AgentId(type="my_agent", key="default")
    )
import asyncio
asyncio.run(main())
```
Parameters :

*   **agent_instance** (`Agent`) – A concrete instance of the agent.
*   **agent_id** (`AgentId`) – The agent’s identifier. The agent’s type is `agent_id.type`.

*async* **try_get_underlying_agent_instance** (id : `AgentId`, type : `Type[T]` = `Agent`) → `T` [source]#
Try to get the underlying agent instance by name and namespace. This is generally discouraged (hence the long name), but can be useful in some cases.
If the underlying agent is not accessible, this will raise an exception.
Parameters :
*   **id** (`AgentId`) – The agent id.

*   **type** (`Type[T]`, *optional*) – The expected type of the agent. Defaults to Agent.
Returns :
*   **T** – The concrete agent instance.
Raises :
*   **LookupError** – If the agent is not found.
*   **NotAccessibleError** – If the agent is not accessible, for example if it is located remotely.
*   **TypeError** – If the agent is not of the expected type.

*async* **get** (id : `AgentId`, */*, ***, lazy : `bool` = `True`) → `AgentId` [source]#
*async* **get** (type : `AgentType`| `str`, */*, key : `str` = `'default'`, ***, lazy : `bool` = `True`) → `AgentId`

*async* **save_state** () → `Mapping[str, Any]` [source]#
Save the state of the entire runtime, including all hosted agents. The only way to restore the state is to pass it to load_state().

The structure of the state is implementation defined and can be any JSON serializable object.
Returns :
*   **Mapping[str, Any]** – The saved state.

*async* **load_state** (state : `Mapping[str, Any]`) → `None` [source]#
Load the state of the entire runtime, including all hosted agents. The state should be the same as the one returned by save_state().
Parameters :
*   **state** (`Mapping[str, Any]`) – The saved state.

*async* **agent_metadata** (agent : `AgentId`) → `AgentMetadata` [source]#
Get the metadata for an agent.
Parameters :

*   **agent** (`AgentId`) – The agent id.
Returns :
*   **AgentMetadata** – The agent metadata.

*async* **agent_save_state** (agent : `AgentId`) → `Mapping[str, Any]` [source]#
Save the state of a single agent.
The structure of the state is implementation defined and can be any JSON serializable object.
Parameters :
*   **agent** (`AgentId`) – The agent id.
Returns :
*   **Mapping[str, Any]** – The saved state.

*async* **agent_load_state** (agent : `AgentId`, state : `Mapping[str, Any]`) → `None` [source]#
Load the state of a single agent.
Parameters :

*   **agent** (`AgentId`) – The agent id.
*   **state** (`Mapping[str, Any]`) – The saved state.

*async* **add_subscription** (subscription : `Subscription`) → `None` [source]#
Add a new subscription that the runtime should fulfill when processing published messages
Parameters :
*   **subscription** (`Subscription`) – The subscription to add

*async* **remove_subscription** (id : `str`) → `None` [source]#
Remove a subscription from the runtime
Parameters :
*   **id** (`str`) – id of the subscription to remove
Raises :
*   **LookupError** – If the subscription does not exist

**add_message_serializer** (serializer : `MessageSerializer[Any]` | `Sequence[MessageSerializer[Any]]`) → `None` [source]#
Add a new message serialization serializer to the runtime
Note: This will deduplicate serializers based on the type_name and data_content_type properties
Parameters :
*   **serializer** (`MessageSerializer[Any]` | `Sequence[MessageSerializer[Any]]`) – The serializer/s to add

*class* **BaseAgent** (description : `str`) [source]#
Bases: `ABC`, `Agent`

*property* **metadata**: `AgentMetadata`
Metadata of the agent.

*async* **bind_id_and_runtime** (id : `AgentId`, runtime : `AgentRuntime`) → `None` [source]#
Function used to bind an Agent instance to an `AgentRuntime`.
Parameters :
*   **agent_id** (`AgentId`) – ID of the agent.
*   **runtime** (`AgentRuntime`) – AgentRuntime instance to bind the agent to.

*property* **type**: `str`
*property* **id**: `AgentId`
ID of the agent.

*property* **runtime**: `AgentRuntime`

*final async* **on_message** (message : `Any`, ctx : `MessageContext`) → `Any` [source]#
Message handler for the agent. This should only be called by the runtime, not by other agents.

Parameters :
*   **message** (`Any`) – Received message. Type is one of the types in `subscriptions`.
*   **ctx** (`MessageContext`) – Context of the message.
Returns :
*   **Any** – Response to the message. Can be None.
Raises :
*   **CancelledError** – If the message was cancelled.
*   **CantHandleException** – If the agent cannot handle the message.

*abstract async* **on_message_impl** (message : `Any`, ctx : `MessageContext`) → `Any`

*async* **send_message** (message : `Any`, recipient : `AgentId`, ***, cancellation_token : `CancellationToken`| `None` = `None`, message_id : `str`| `None` = `None`) → `Any` [source]#
See `autogen_core.AgentRuntime.send_message()` for more information.

*async* **publish_message** (message : `Any`, topic_id : `TopicId`, ***, cancellation_token : `CancellationToken`| `None` = `None`) → `None` [source]#

*async* **save_state** () → `Mapping[str, Any]` [source]#
Save the state of the agent. The result must be JSON serializable.

*async* **load_state** (state : `Mapping[str, Any]`) → `None` [source]#
Load in the state of the agent obtained from `save_state`.
Parameters :
*   **state** (`Mapping[str, Any]`) – State of the agent. Must be JSON serializable.

*async* **close** () → `None` [source]#
Called when the runtime is closed

*async* **register_instance** (runtime : `AgentRuntime`, agent_id : `AgentId`, ***, skip_class_subscriptions : `bool` = `True`, skip_direct_message_subscription : `bool` = `False`) → `AgentId` [source]#
This function is similar to `register` but is used for registering an instance of an agent. A subscription based on the agent ID is created and added to the runtime.

*async classmethod* **register** (runtime : `AgentRuntime`, type : `str`, factory : `Callable[ [ ] , Self| Awaitable[Self] ]`, ***, skip_class_subscriptions : `bool` = `False`, skip_direct_message_subscription : `bool` = `False`) → `AgentType` [source]#
Register a virtual subclass of an ABC.

Returns the subclass, to allow usage as a class decorator.

*class* **CacheStore** [source]#
Bases: `ABC`, `Generic[T]`, `ComponentBase[BaseModel]`
This protocol defines the basic interface for store/cache operations.
Sub-classes should handle the lifecycle of underlying storage.
`component_type`: `ClassVar[ComponentType]` = `'cache_store'`
The logical type of the component.

*abstract* **get** (key : `str`, default : `T` | `None` = `None`) → `T` | `None` [source]#
Retrieve an item from the store.
Parameters :
*   **key** – The key identifying the item in the store.

*   **default** (*optional*) – The default value to return if the key is not found. Defaults to None.
Returns :
*   **The value associated with the key if found, else the default value.**

*abstract* **set** (key : `str`, *value : T*) → `None` [source]#
Set an item in the store.
Parameters :
*   **key** – The key under which the item is to be stored.
*   **value** – The value to be stored in the store.

*class* **InMemoryStore** [source]#
Bases: `CacheStore[T]`, `Component[InMemoryStoreConfig]`
`component_provider_override`: `ClassVar[str|None]` = `'autogen_core.InMemoryStore'`
Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

`component_config_schema`
alias of `InMemoryStoreConfig`

**get** (key : `str`, default : `T` | `None` = `None`) → `T` | `None` [source]#
Retrieve an item from the store.
Parameters :
*   **key** – The key identifying the item in the store.
*   **default** (*optional*) – The default value to return if the key is not found. Defaults to None.
Returns :
*   **The value associated with the key if found, else the default value.**

**set** (key : `str`, *value : T*) → `None` [source]#
Set an item in the store.
Parameters :
*   **key** – The key under which the item is to be stored.

*   **value** – The value to be stored in the store.

`_to_config` () → `InMemoryStoreConfig` [source]#
Dump the configuration that would be requite to create a new instance of a component matching the configuration of this instance.
Returns :
*   **T** – The configuration of the component.

*classmethod* `_from_config` (*config : InMemoryStoreConfig*) → `Self` [source]#
Create a new instance of the component from a configuration object.
Parameters :
*   **config** (`T`) – The configuration object.
Returns :
*   **Self** – The new instance of the component.

*class* **CancellationToken** [source]#
Bases: `object`
A token used to cancel pending async calls

**cancel** () → `None` [source]#
Cancel pending async calls linked to this cancellation token.

**is_cancelled** () → `bool` [source]#
Check if the CancellationToken has been used

**add_callback** (callback : `Callable[ [ ] , None ]`) → `None` [source]#
Attach a callback that will be called when cancel is invoked

**link_future** (future : `Future[Any]`) → `Future[Any]` [source]#
Link a pending async call to a token to allow its cancellation

*class* **AgentInstantiationContext** [source]#
Bases: `object`
A static class that provides context for agent instantiation.
This static class can be used to access the current runtime and agent ID during agent instantiation – inside the factory function or the agent’s class constructor.
Example
Get the current runtime and agent ID inside the factory function and the agent’s constructor:
```python
import asyncio
from dataclasses import dataclass
from autogen_core import (
    AgentId,
    AgentInstantiationContext,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    message_handler,
)

@dataclass
class TestMessage:
    content: str

class TestAgent(RoutedAgent):
    def __init__(self, description: str):
        super().__init__(description)
        # Get the current runtime -- we don't use it here, but it's available.
        _ = AgentInstantiationContext.current_runtime()
        # Get the current agent ID.
        agent_id = AgentInstantiationContext.current_agent_id()
        print(f"Current AgentID from constructor: {agent_id}")

    @message_handler
    async def handle_test_message(self, message: TestMessage, ctx: MessageContext) -> None:
        print(f"Received message: {message.content}")

def test_agent_factory() -> TestAgent:
    # Get the current runtime -- we don't use it here, but it's available.
    _ = AgentInstantiationContext.current_runtime()
    # Get the current agent ID.
    agent_id = AgentInstantiationContext.current_agent_id()
    print(f"Current AgentID from factory: {agent_id}")
    return TestAgent(description="Test agent")

async def main() -> None:
    # Create a SingleThreadedAgentRuntime instance.
    runtime = SingleThreadedAgentRuntime()
    # Start the runtime.
    runtime.start()
    # Register the agent type with a factory function.
    await runtime.register_factory("test_agent", test_agent_factory)
    # Send a message to the agent. The runtime will instantiate the agent and call the message handler.
    await runtime.send_message(TestMessage(content="Hello, world!"), AgentId("test_agent", "default"))
    # Stop the runtime.
    await runtime.stop()

asyncio.run(main())
```
*classmethod* **current_runtime** () → `AgentRuntime` [source]#

*classmethod* **current_agent_id** () → `AgentId` [source]#

*classmethod* **is_in_factory_call** () → `bool` [source]#

*class* **TopicId** (type : `str`, source : `str`) [source]#

TopicId defines the scope of a broadcast message. In essence, agent runtime implements a publish-subscribe model through its broadcast API: when publishing a message, the topic must be specified.

See here for more information: Topic

type: `str`
Type of the event that this topic_id contains. Adhere’s to the cloud event spec.
Must match the pattern: `^[w-.:=]+Z`
Learn more here: cloudevents/spec

source: `str`
Identifies the context in which an event happened. Adhere’s to the cloud event spec.
Learn more here: cloudevents/spec

*classmethod* **from_str** (topic_id : `str`) → `Self` [source]#
Convert a string of the format `type/source` into a TopicId

*class* **Subscription** (*args*, ***kwargs*) [source]#
Bases: `Protocol`
Subscriptions define the topics that an agent is interested in.

*property* **id**: `str`
Get the ID of the subscription.
Implementations should return a unique ID for the subscription. Usually this is a UUID.
Returns :
*   **str** – ID of the subscription.

**is_match** (topic_id : `TopicId`) → `bool` [source]#
Check if a given topic_id matches the subscription.

Parameters :
*   **topic_id** (`TopicId`) – TopicId to check.
Returns :
*   **bool** – True if the topic_id matches the subscription, False otherwise.

**map_to_agent** (topic_id : `TopicId`) → `AgentId` [source]#
Map a topic_id to an agent. Should only be called if `is_match` returns True for the given topic_id.
Parameters :
*   **topic_id** (`TopicId`) – TopicId to map.
Returns :
*   **AgentId** – ID of the agent that should handle the topic_id.
Raises :
*   **CantHandleException** – If the subscription cannot handle the topic_id.

*class* **MessageContext** (sender : `AgentId`| `None`, topic_id : `TopicId`| `None`, is_rpc : `bool`, cancellation_token : `CancellationToken`, message_id : `str`) [source]#
Bases: `object`

sender: `AgentId`| `None`
topic_id: `TopicId`| `None`
is_rpc: `bool`
cancellation_token: `CancellationToken`
message_id: `str`

*class* **AgentType** (type : `str`) [source]#
Bases: `object`
type: `str`
String representation of this agent type.

*class* **SubscriptionInstantiationContext** [source]#
Bases: `object`

*classmethod* **agent_type** () → `AgentType` [source]#

*class* **MessageHandlerContext** [source]#
Bases: `object`

*classmethod* **agent_id** () → `AgentId` [source]#

*class* **MessageSerializer** (*args*, ***kwargs*) [source]#
Bases: `Protocol[T]`

*property* **data_content_type**: `str`
*property* **type_name**: `str`

**deserialize** (payload : `bytes`) → `T` [source]#
**serialize** (*message : T*) → `bytes` [source]#

*class* **UnknownPayload** (type_name : `str`, data_content_type : `str`, payload : `bytes`) [source]#
Bases: `object`

type_name: `str`
data_content_type: `str`
payload: `bytes`

*class* **Image** (*image : Image*) [source]#
Bases: `object`
Represents an image.
Example
Loading an image from a URL:
```python
from autogen_core import Image
from PIL import Image as PILImage
import aiohttp
import asyncio

async def from_url(url: str) -> Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.read()
            return Image.from_pil(PILImage.open(content))

image = asyncio.run(from_url("https://example.com/image"))
```
*classmethod* **from_pil** (*pil_image : Image*) → `Image` [source]#

*classmethod* **from_uri** (uri : `str`) → `Image` [source]#

*classmethod* **from_base64** (base64_str : `str`) → `Image` [source]#

**to_base64** () → `str` [source]#

*classmethod* **from_file** (file_path : `Path`) → `Image` [source]#

*property* **data_uri**: `str`

**to_openai_format** (detail : `Literal[ 'auto' , 'low' , 'high' ]` = `'auto'`) → `Dict[str, Any]` [source]#

*class* **RoutedAgent** (description : `str`) [source]#
Bases: `BaseAgent`

A base class for agents that route messages to handlers based on the type of the message and optional matching functions.
To create a routed agent, subclass this class and add message handlers as methods decorated with either event() or rpc() decorator.
Example:
```python
from dataclasses import dataclass
from autogen_core import MessageContext
from autogen_core import RoutedAgent, event, rpc

@dataclass
class Message:
    pass

@dataclass
class MessageWithContent:
    content: str

@dataclass
class Response:
    pass

class MyAgent(RoutedAgent):
    def __init__(self):
        super().__init__("MyAgent")

    @event
    async def handle_event_message(self, message: Message, ctx: MessageContext) -> None:
        assert ctx.topic_id is not None
        await self.publish_message(MessageWithContent("event handled"), ctx.topic_id)

    @rpc(match = lambda message, ctx: message.content == "special") # type: ignore
    async def handle_special_rpc_message(self, message: MessageWithContent, ctx: MessageContext) -> Response:
        return Response()
```
*async* **on_message_impl** (message : `Any`, ctx : `MessageContext`) → `Any`| `None` [source]#
Handle a message by routing it to the appropriate message handler. Do not override this method in subclasses. Instead, add message handlers as methods decorated with either the event() or rpc() decorator.

*async* **on_unhandled_message** (message : `Any`, ctx : `MessageContext`) → `None` [source]#
Called when a message is received that does not have a matching message handler. The default implementation logs an info message.

*class* **ClosureAgent** (description : `str`, closure : `Callable[ [ClosureContext, T, MessageContext] , Awaitable[Any] ]`, ***, unknown_type_policy : `Literal[ 'error' , 'warn' , 'ignore' ]` = `'warn'`) [source]#
Bases: `BaseAgent`, `ClosureContext`

*property* **metadata**: `AgentMetadata`
Metadata of the agent.

*property* **id**: `AgentId`
ID of the agent.

*property* **runtime**: `AgentRuntime`

*async* **on_message_impl** (message : `Any`, ctx : `MessageContext`) → `Any` [source]#

*async* **save_state** () → `Mapping[str, Any]` [source]#
Closure agents do not have state. So this method always returns an empty dictionary.

*async* **load_state** (state : `Mapping[str, Any]`) → `None` [source]#
Closure agents do not have state. So this method does nothing.

*async classmethod* **register_closure** (runtime : `AgentRuntime`, type : `str`, closure : `Callable[ [ClosureContext, T, MessageContext] , Awaitable[Any] ]`, ***, unknown_type_policy : `Literal[ 'error' , 'warn' , 'ignore' ]` = `'warn'`, skip_direct_message_subscription : `bool` = `False`, description : `str` = `''`, subscriptions : `Callable[ [ ] , list[Subscription] | Awaitable[list[Subscription]] ]` | `None` = `None`) → `AgentType` [source]#
The closure agent allows you to define an agent using a closure, or function without needing to define a class. It allows values to be extracted out of the runtime.

The closure can define the type of message which is expected, or `Any` can be used to accept any type of message.
Example:
```python
import asyncio
from autogen_core import SingleThreadedAgentRuntime, MessageContext, ClosureAgent, ClosureContext
from dataclasses import dataclass
from autogen_core._default_subscription import DefaultSubscription
from autogen_core._default_topic import DefaultTopicId

@dataclass
class MyMessage:
    content: str

async def main():
    queue = asyncio.Queue[MyMessage]()

    async def output_result(_ctx: ClosureContext, message: MyMessage, ctx: MessageContext) -> None:
        await queue.put(message)

    runtime = SingleThreadedAgentRuntime()
    await ClosureAgent.register_closure(
        runtime,
        "output_result",
        output_result,
        subscriptions = lambda: [DefaultSubscription()]
    )
    runtime.start()
    await runtime.publish_message(MyMessage("Hello, world!"), DefaultTopicId())
    await runtime.stop_when_idle()
    result = await queue.get()
    print(result)

asyncio.run(main())
```
Parameters :

*   **runtime** (`AgentRuntime`) – Runtime to register the agent to
*   **type** (`str`) – Agent type of registered agent
*   **closure** (`Callable[ [ClosureContext, T, MessageContext] , Awaitable[Any] ]`) – Closure to handle messages
*   **unknown_type_policy** (`Literal[ "error" , "warn" , "ignore" ]`, *optional*) – What to do if a type is encountered that does not match the closure type. Defaults to “warn”.
*   **skip_direct_message_subscription** (`bool`, *optional*) – Do not add direct message subscription for this agent. Defaults to False.
*   **description** (`str`, *optional*) – Description of what agent does. Defaults to “”.

*   **subscriptions** (`Callable[ [ ] , list[Subscription] | Awaitable[list[Subscription]] ]` | `None`, *optional*) – List of subscriptions for this closure agent. Defaults to None.
Returns :
*   **AgentType** – Type of the agent that was registered

*class* **ClosureContext** (*args*, ***kwargs*) [source]#
Bases: `Protocol`

*property* **id**: `AgentId`

*async* **send_message** (message : `Any`, recipient : `AgentId`, ***, cancellation_token : `CancellationToken`| `None` = `None`, message_id : `str`| `None` = `None`) → `Any` [source]#

*async* **publish_message** (message : `Any`, topic_id : `TopicId`, ***, cancellation_token : `CancellationToken`| `None` = `None`) → `None` [source]#

**message_handler** (func : `None`| `Callable[ [AgentT, ReceivesT, MessageContext] , Coroutine[Any, Any, ProducesT] ]` = `None`, ***, strict : `bool` = `True`, match : `None`| `Callable[ [ReceivesT, MessageContext] , bool ]` = `None`) → `Callable[ [Callable[ [AgentT, ReceivesT, MessageContext] , Coroutine[Any, Any, ProducesT] ] ] , MessageHandler[AgentT, ReceivesT, ProducesT] ]` | `MessageHandler[AgentT, ReceivesT, ProducesT]` [source]#
Decorator for generic message handlers.

Add this decorator to methods in a RoutedAgent class that are intended to handle both event and RPC messages. These methods must have a specific signature that needs to be followed for it to be valid:
*   The method must be an `async` method.
*   The method must be decorated with the `@message_handler` decorator.
*   The method must have exactly 3 arguments:
    *   `self`
    *   `message`: The message to be handled, this must be type-hinted with the message type that it is intended to handle.
    *   `ctx`: A `autogen_core.MessageContext` object.

*   The method must be type hinted with what message types it can return as a response, or it can return `None` if it does not return anything.
*   Handlers can handle more than one message type by accepting a Union of the message types. It can also return more than one message type by returning a Union of the message types.
Parameters :
*   **func** – The function to be decorated.
*   **strict** – If `True`, the handler will raise an exception if the message type or return type is not in the target types. If `False`, it will log a warning instead.

*   **match** – A function that takes the message and the context as arguments and returns a boolean. This is used for secondary routing after the message type. For handlers addressing the same message type, the match function is applied in alphabetical order of the handlers and the first matching handler will be called while the rest are skipped. If `None`, the first handler in alphabetical order matching the same message type will be called.

**event** (func : `None`| `Callable[ [AgentT, ReceivesT, MessageContext] , Coroutine[Any, Any, None] ]` = `None`, ***, strict : `bool` = `True`, match : `None`| `Callable[ [ReceivesT, MessageContext] , bool ]` = `None`) → `Callable[ [Callable[ [AgentT, ReceivesT, MessageContext] , Coroutine[Any, Any, None] ] ] , MessageHandler[AgentT, ReceivesT, None] ]` | `MessageHandler[AgentT, ReceivesT, None]` [source]#
Decorator for event message handlers.

Add this decorator to methods in a RoutedAgent class that are intended to handle event messages. These methods must have a specific signature that needs to be followed for it to be valid:
*   The method must be an `async` method.
*   The method must be decorated with the `@message_handler` decorator.
*   The method must have exactly 3 arguments:
    *   `self`
    *   `message`: The event message to be handled, this must be type-hinted with the message type that it is intended to handle.
    *   `ctx`: A `autogen_core.MessageContext` object.
*   The method must return `None`.

*   Handlers can handle more than one message type by accepting a Union of the message types.
Parameters :
*   **func** – The function to be decorated.
*   **strict** – If `True`, the handler will raise an exception if the message type is not in the target types. If `False`, it will log a warning instead.
*   **match** – A function that takes the message and the context as arguments and returns a boolean. This is used for secondary routing after the message type. For handlers addressing the same message type, the match function is applied in alphabetical order of the handlers and the first matching handler will be called while the rest are skipped. If `None`, the first handler in alphabetical order matching the same message type will be called.

**rpc** (func : `None`| `Callable[ [AgentT, ReceivesT, MessageContext] , Coroutine[Any, Any, ProducesT] ]` = `None`, ***, strict : `bool` = `True`, match : `None`| `Callable[ [ReceivesT, MessageContext] , bool ]` = `None`) → `Callable[ [Callable[ [AgentT, ReceivesT, MessageContext] , Coroutine[Any, Any, ProducesT] ] ] , MessageHandler[AgentT, ReceivesT, ProducesT] ]` | `MessageHandler[AgentT, ReceivesT, ProducesT]` [source]#
Decorator for RPC message handlers.

Add this decorator to methods in a RoutedAgent class that are intended to handle RPC messages. These methods must have a specific signature that needs to be followed for it to be valid:
*   The method must be an `async` method.
*   The method must be decorated with the `@message_handler` decorator.
*   The method must have exactly 3 arguments:
    *   `self`
    *   `message`: The message to be handled, this must be type-hinted with the message type that it is intended to handle.
    *   `ctx`: A `autogen_core.MessageContext` object.
*   The method must be type hinted with what message types it can return as a response, or it can return `None` if it does not return anything.

*   Handlers can handle more than one message type by accepting a Union of the message types. It can also return more than one message type by returning a Union of the message types.
Parameters :
*   **func** – The function to be decorated.
*   **strict** – If `True`, the handler will raise an exception if the message type or return type is not in the target types. If `False`, it will log a warning instead.
*   **match** – A function that takes the message and the context as arguments and returns a boolean. This is used for secondary routing after the message type. For handlers addressing the same message type, the match function is applied in alphabetical order of the handlers and the first matching handler will be called while the rest are skipped. If `None`, the first handler in alphabetical order matching the same message type will be called.

*class* **FunctionCall** (*id : 'str'*, *arguments : 'str'*, *name : 'str'*) [source]#
Bases: `object`

id: `str`
arguments: `str`
name: `str`

*class* **TypeSubscription** (topic_type : `str`, agent_type : `str`| `AgentType`, id : `str`| `None` = `None`) [source]#
Bases: `Subscription`
This subscription matches on topics based on the type and maps to agents using the source of the topic as the agent key.
This subscription causes each source to have its own agent instance.
Example
```python
from autogen_core import TypeSubscription
subscription = TypeSubscription(topic_type="t1", agent_type="a1")
```

In this case:
*   A topic_id with type `t1` and source `s1` will be handled by an agent of type `a1` with key `s1`
*   A topic_id with type `t1` and source `s2` will be handled by an agent of type `a1` with key `s2`.
Parameters :
*   **topic_type** (`str`) – Topic type to match against
*   **agent_type** (`str`) – Agent type to handle this subscription

*property* **id**: `str`
Get the ID of the subscription.
Implementations should return a unique ID for the subscription. Usually this is a UUID.
Returns :
*   **str** – ID of the subscription.

*property* **topic_type**: `str`
*property* **agent_type**: `str`

**is_match** (topic_id : `TopicId`) → `bool` [source]#
Check if a given topic_id matches the subscription.

Parameters :
*   **topic_id** (`TopicId`) – TopicId to check.
Returns :
*   **bool** – True if the topic_id matches the subscription, False otherwise.

**map_to_agent** (topic_id : `TopicId`) → `AgentId` [source]#
Map a topic_id to an agent. Should only be called if `is_match` returns True for the given topic_id.
Parameters :
*   **topic_id** (`TopicId`) – TopicId to map.
Returns :
*   **AgentId** – ID of the agent that should handle the topic_id.
Raises :
*   **CantHandleException** – If the subscription cannot handle the topic_id.

*class* **DefaultSubscription** (topic_type : `str` = `'default'`, agent_type : `str`| `AgentType`| `None` = `None`) [source]#
Bases: `TypeSubscription`

The default subscription is designed to be a sensible default for applications that only need global scope for agents.
This topic by default uses the “default” topic type and attempts to detect the agent type to use based on the instantiation context.
Parameters :
*   **topic_type** (`str`, *optional*) – The topic type to subscribe to. Defaults to “default”.
*   **agent_type** (`str`, *optional*) – The agent type to use for the subscription. Defaults to None, in which case it will attempt to detect the agent type based on the instantiation context.

*class* **DefaultTopicId** (type : `str` = `'default'`, source : `str`| `None` = `None`) [source]#
Bases: `TopicId`
DefaultTopicId provides a sensible default for the topic_id and source fields of a TopicId.
If created in the context of a message handler, the source will be set to the agent_id of the message handler, otherwise it will be set to “default”.
Parameters :
*   **type** (`str`, *optional*) – Topic type to publish message to. Defaults to “default”.
*   **source** (`str` | `None`, *optional*) – Topic source to publish message to. If None, the source will be set to the agent_id of the message handler if in the context of a message handler, otherwise it will be set to “default”. Defaults to None.

**default_subscription** (cls : `Type[BaseAgentType]` | `None` = `None`) → `Callable[ [Type[BaseAgentType]] , Type[BaseAgentType] ]` | `Type[BaseAgentType]` [source]#

**type_subscription** (topic_type : `str`) → `Callable[ [Type[BaseAgentType]] , Type[BaseAgentType] ]` [source]#

*class* **TypePrefixSubscription** (topic_type_prefix : `str`, agent_type : `str`| `AgentType`, id : `str`| `None` = `None`) [source]#
Bases: `Subscription`
This subscription matches on topics based on a prefix of the type and maps to agents using the source of the topic as the agent key.

This subscription causes each source to have its own agent instance.
Example
```python
from autogen_core import TypePrefixSubscription
subscription = TypePrefixSubscription(topic_type_prefix="t1", agent_type="a1")
```
In this case:
*   A topic_id with type `t1` and source `s1` will be handled by an agent of type `a1` with key `s1`
*   A topic_id with type `t1` and source `s2` will be handled by an agent of type `a1` with key `s2`.
*   A topic_id with type `t1SUFFIX` and source `s2` will be handled by an agent of type `a1` with key `s2`.

Parameters :
*   **topic_type_prefix** (`str`) – Topic type prefix to match against
*   **agent_type** (`str`) – Agent type to handle this subscription

*property* **id**: `str`
Get the ID of the subscription.
Implementations should return a unique ID for the subscription. Usually this is a UUID.
Returns :
*   **str** – ID of the subscription.

*property* **topic_type_prefix**: `str`
*property* **agent_type**: `str`

**is_match** (topic_id : `TopicId`) → `bool` [source]#
Check if a given topic_id matches the subscription.
Parameters :
*   **topic_id** (`TopicId`) – TopicId to check.

Returns :
*   **bool** – True if the topic_id matches the subscription, False otherwise.

**map_to_agent** (topic_id : `TopicId`) → `AgentId` [source]#
Map a topic_id to an agent. Should only be called if `is_match` returns True for the given topic_id.
Parameters :
*   **topic_id** (`TopicId`) – TopicId to map.
Returns :
*   **AgentId** – ID of the agent that should handle the topic_id.
Raises :
*   **CantHandleException** – If the subscription cannot handle the topic_id.

`JSON_DATA_CONTENT_TYPE` = `'application/json'`
The content type for JSON data.

`PROTOBUF_DATA_CONTENT_TYPE` = `'application/x-protobuf'`
The content type for Protobuf data.

*class* **SingleThreadedAgentRuntime** (***, intervention_handlers : `List[InterventionHandler]` | `None` = `None`, tracer_provider : `TracerProvider` | `None` = `None`, ignore_unhandled_exceptions : `bool` = `True`) [source]#
Bases: `AgentRuntime`
A single-threaded agent runtime that processes all messages using a single asyncio queue. Messages are delivered in the order they are received, and the runtime processes each message in a separate asyncio task concurrently.

Note
This runtime is suitable for development and standalone applications. It is not suitable for high-throughput or high-concurrency scenarios.
Parameters :
*   **intervention_handlers** (`List[InterventionHandler]`, *optional*) – A list of intervention handlers that can intercept messages before they are sent or published. Defaults to None.
*   **tracer_provider** (`TracerProvider`, *optional*) – The tracer provider to use for tracing. Defaults to None.
*   **ignore_unhandled_exceptions** (`bool`, *optional*) – Whether to ignore unhandled exceptions in that occur in agent event handlers. Any background exceptions will be raised on the next call to `process_next` or from an awaited `stop`, `stop_when_idle` or `stop_when`. Note, this does not apply to RPC handlers. Defaults to True.

Examples
A simple example of creating a runtime, registering an agent, sending a message and stopping the runtime:
```python
import asyncio
from dataclasses import dataclass
from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler

@dataclass
class MyMessage:
    content: str

class MyAgent(RoutedAgent):
    @message_handler
    async def handle_my_message(self, message: MyMessage, ctx: MessageContext) -> None:
        print(f"Received message: {message.content}")

async def main() -> None:
    # Create a runtime and register the agent
    runtime = SingleThreadedAgentRuntime()
    await MyAgent.register(runtime, "my_agent", lambda: MyAgent("My agent"))

    # Start the runtime, send a message and stop the runtime
    runtime.start()
    await runtime.send_message(MyMessage("Hello, world!"), recipient=AgentId("my_agent", "default"))
    await runtime.stop()

asyncio.run(main())
```

An example of creating a runtime, registering an agent, publishing a message and stopping the runtime:
```python
import asyncio
from dataclasses import dataclass
from autogen_core import (
    DefaultTopicId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    default_subscription,
    message_handler,
)

@dataclass
class MyMessage:
    content: str

# The agent is subscribed to the default topic.
@default_subscription
class MyAgent(RoutedAgent):
    @message_handler
    async def handle_my_message(self, message: MyMessage, ctx: MessageContext) -> None:
        print(f"Received message: {message.content}")

async def main() -> None:
    # Create a runtime and register the agent
    runtime = SingleThreadedAgentRuntime()
    await MyAgent.register(runtime, "my_agent", lambda: MyAgent("My agent"))

    # Start the runtime.
    runtime.start()

    # Publish a message to the default topic that the agent is subscribed to.
    await runtime.publish_message(MyMessage("Hello, world!"), DefaultTopicId())

    # Wait for the message to be processed and then stop the runtime.
    await runtime.stop_when_idle()

asyncio.run(main())
```
*property* **unprocessed_messages_count**: `int`

*async* **send_message** (message : `Any`, recipient : `AgentId`, ***, sender : `AgentId`| `None` = `None`, cancellation_token : `CancellationToken`| `None` = `None`, message_id : `str`| `None` = `None`) → `Any` [source]#
Send a message to an agent and get a response.

Parameters :
*   **message** (`Any`) – The message to send.
*   **recipient** (`AgentId`) – The agent to send the message to.
*   **sender** (`AgentId` | `None`, *optional*) – Agent which sent the message. Should **only** be None if this was sent from no agent, such as directly to the runtime externally. Defaults to None.
*   **cancellation_token** (`CancellationToken` | `None`, *optional*) – Token used to cancel an in progress. Defaults to None.
Raises :
*   **CantHandleException** – If the recipient cannot handle the message.
*   **UndeliverableException** – If the message cannot be delivered.

*   **Other** – Any other exception raised by the recipient.
Returns :
*   **Any** – The response from the agent.

*async* **publish_message** (message : `Any`, topic_id : `TopicId`, ***, sender : `AgentId`| `None` = `None`, cancellation_token : `CancellationToken`| `None` = `None`, message_id : `str`| `None` = `None`) → `None` [source]#
Publish a message to all agents in the given namespace, or if no namespace is provided, the namespace of the sender.
No responses are expected from publishing.
Parameters :
*   **message** (`Any`) – The message to publish.

*   **topic_id** (`TopicId`) – The topic to publish the message to.
*   **sender** (`AgentId` | `None`, *optional*) – The agent which sent the message. Defaults to None.
*   **cancellation_token** (`CancellationToken` | `None`, *optional*) – Token used to cancel an in progress. Defaults to None.
*   **message_id** (`str` | `None`, *optional*) – The message id. If None, a new message id will be generated. Defaults to None. This message id must be unique. and is recommended to be a UUID.
Raises :
*   **UndeliverableException** – If the message cannot be delivered.

*async* **save_state** () → `Mapping[str, Any]` [source]#
Save the state of all instantiated agents.
This method calls the save_state() method on each agent and returns a dictionary mapping agent IDs to their state.
Note
This method does not currently save the subscription state. We will add this in the future.
Returns :
*   **A dictionary mapping agent IDs to their state.**

*async* **load_state** (state : `Mapping[str, Any]`) → `None` [source]#
Load the state of all instantiated agents.
This method calls the load_state() method on each agent with the state provided in the dictionary. The keys of the dictionary are the agent IDs, and the values are the state dictionaries returned by the save_state() method.

Note
This method does not currently load the subscription state. We will add this in the future.

*async* **process_next** () → `None` [source]#
Process the next message in the queue.
If there is an unhandled exception in the background task, it will be raised here. `process_next` cannot be called again after an unhandled exception is raised.

**start** () → `None` [source]#
Start the runtime message processing loop. This runs in a background task.
Example:
```python
import asyncio
from autogen_core import SingleThreadedAgentRuntime

async def main() -> None:
    runtime = SingleThreadedAgentRuntime()
    runtime.start()
    # ... do other things ...
    await runtime.stop()

asyncio.run(main())
```
*async* **close** () → `None` [source]#
Calls stop() if applicable and the Agent.close() method on all instantiated agents

*async* **stop** () → `None` [source]#
Immediately stop the runtime message processing loop. The currently processing message will be completed, but all others following it will be discarded.

*async* **stop_when_idle** () → `None` [source]#
Stop the runtime message processing loop when there is no outstanding message being processed or queued. This is the most common way to stop the runtime.

*async* **stop_when** (condition : `Callable[ [ ] , bool ]`) → `None` [source]#
Stop the runtime message processing loop when the condition is met.

Caution
This method is not recommended to be used, and is here for legacy reasons. It will spawn a busy loop to continually check the condition. It is much more efficient to call `stop_when_idle` or `stop` instead. If you need to stop the runtime based on a condition, consider using a background task and asyncio.Event to signal when the condition is met and the background task should call stop.

*async* **agent_metadata** (agent : `AgentId`) → `AgentMetadata` [source]#
Get the metadata for an agent.
Parameters :

*   **agent** (`AgentId`) – The agent id.
Returns :
*   **AgentMetadata** – The agent metadata.

*async* **agent_save_state** (agent : `AgentId`) → `Mapping[str, Any]` [source]#
Save the state of a single agent.
The structure of the state is implementation defined and can be any JSON serializable object.
Parameters :
*   **agent** (`AgentId`) – The agent id.
Returns :
*   **Mapping[str, Any]** – The saved state.

*async* **agent_load_state** (agent : `AgentId`, state : `Mapping[str, Any]`) → `None` [source]#
Load the state of a single agent.
Parameters :

*   **agent** (`AgentId`) – The agent id.
*   **state** (`Mapping[str, Any]`) – The saved state.

*async* **register_factory** (type : `str`| `AgentType`, agent_factory : `Callable[ [ ] , T | Awaitable[T] ]`, ***, expected_class : `type[T]` | `None` = `None`) → `AgentType` [source]#
Register an agent factory with the runtime associated with a specific type. The type must be unique. This API does not add any subscriptions.
Note
This is a low level API and usually the agent class’s `register` method should be used instead, as this also handles subscriptions automatically.

Example:
```python
from dataclasses import dataclass
from autogen_core import AgentRuntime, MessageContext, RoutedAgent, event
from autogen_core.models import UserMessage

@dataclass
class MyMessage:
    content: str

class MyAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("My core agent")

    @event
    async def handler(self, message: UserMessage, context: MessageContext) -> None:
        print("Event received: ", message.content)

async def my_agent_factory():
    return MyAgent()

async def main() -> None:
    runtime: AgentRuntime = ... # type: ignore
    await runtime.register_factory("my_agent", lambda: MyAgent())

import asyncio
asyncio.run(main())
```
Parameters :

*   **type** (`str`) – The type of agent this factory creates. It is not the same as agent class name. The `type` parameter is used to differentiate between different factory functions rather than agent classes.
*   **agent_factory** (`Callable[ [ ] , T ]`) – The factory that creates the agent, where T is a concrete Agent type. Inside the factory, use `autogen_core.AgentInstantiationContext` to access variables like the current runtime and agent ID.
*   **expected_class** (`type[T]` | `None`, *optional*) – The expected class of the agent, used for runtime validation of the factory. Defaults to None. If None, no validation is performed.

*async* **register_agent_instance** (agent_instance : `Agent`, agent_id : `AgentId`) → `AgentId` [source]#
Register an agent instance with the runtime. The type may be reused, but each agent_id must be unique. All agent instances within a type must be of the same object type. This API does not add any subscriptions.
Note
This is a low level API and usually the agent class’s `register_instance` method should be used instead, as this also handles subscriptions automatically.
Example:
```python
from dataclasses import dataclass
from autogen_core import AgentId, AgentRuntime, MessageContext, RoutedAgent, event
from autogen_core.models import UserMessage

@dataclass
class MyMessage:
    content: str

class MyAgent(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("My core agent")

    @event
    async def handler(self, message: UserMessage, context: MessageContext) -> None:
        print("Event received: ", message.content)

async def main() -> None:
    runtime: AgentRuntime = ... # type: ignore
    agent = MyAgent()
    await runtime.register_agent_instance(
        agent_instance = agent,
        agent_id = AgentId(type="my_agent", key="default")
    )
import asyncio
asyncio.run(main())
```
Parameters :

*   **agent_instance** (`Agent`) – A concrete instance of the agent.
*   **agent_id** (`AgentId`) – The agent’s identifier. The agent’s type is `agent_id.type`.

*async* **try_get_underlying_agent_instance** (id : `AgentId`, type : `Type[T]` = `Agent`) → `T` [source]#
Try to get the underlying agent instance by name and namespace. This is generally discouraged (hence the long name), but can be useful in some cases.
If the underlying agent is not accessible, this will raise an exception.
Parameters :
*   **id** (`AgentId`) – The agent id.

*   **type** (`Type[T]`, *optional*) – The expected type of the agent. Defaults to Agent.
Returns :
*   **T** – The concrete agent instance.
Raises :
*   **LookupError** – If the agent is not found.
*   **NotAccessibleError** – If the agent is not accessible, for example if it is located remotely.
*   **TypeError** – If the agent is not of the expected type.

*async* **add_subscription** (subscription : `Subscription`) → `None` [source]#
Add a new subscription that the runtime should fulfill when processing published messages
Parameters :
*   **subscription** (`Subscription`) – The subscription to add

*async* **remove_subscription** (id : `str`) → `None` [source]#
Remove a subscription from the runtime
Parameters :
*   **id** (`str`) – id of the subscription to remove
Raises :
*   **LookupError** – If the subscription does not exist

*async* **get** (id_or_type : `AgentId`| `AgentType`| `str`, */*, key : `str` = `'default'`, ***, lazy : `bool` = `True`) → `AgentId` [source]#

**add_message_serializer** (serializer : `MessageSerializer[Any]` | `Sequence[MessageSerializer[Any]]`) → `None` [source]#
Add a new message serialization serializer to the runtime

Note: This will deduplicate serializers based on the type_name and data_content_type properties
Parameters :
*   **serializer** (`MessageSerializer[Any]` | `Sequence[MessageSerializer[Any]]`) – The serializer/s to add

`ROOT_LOGGER_NAME` = `'autogen_core'`
The name of the root logger.

`EVENT_LOGGER_NAME` = `'autogen_core.events'`
The name of the logger used for structured events.

`TRACE_LOGGER_NAME` = `'autogen_core.trace'`
Logger name used for developer intended trace logging. The content and format of this log should not be depended upon.

*class* **Component** [source]#
Bases: `ComponentFromConfig[ConfigT]`, `ComponentSchemaType[ConfigT]`, `Generic[ConfigT]`
To create a component class, inherit from this class for the concrete class and ComponentBase on the interface. Then implement two class variables:
*   `component_config_schema` - A Pydantic model class which represents the configuration of the component. This is also the type parameter of Component.
*   `component_type` - What is the logical type of the component.
Example:
```python
from __future__ import annotations
from pydantic import BaseModel
from autogen_core import Component

class Config(BaseModel):
    value: str

class MyComponent(Component[Config]):
    component_type = "custom"
    component_config_schema = Config

    def __init__(self, value: str):
        self.value = value

    def _to_config(self) -> Config:
        return Config(value=self.value)

    @classmethod
    def _from_config(cls, config: Config) -> MyComponent:
        return cls(value=config.value)
```
*class* **ComponentBase** [source]#
Bases: `ComponentToConfig[ConfigT]`, `ComponentLoader`, `Generic[ConfigT]`

*class* **ComponentFromConfig** [source]#
Bases: `Generic[FromConfigT]`

*classmethod* **_from_config** (*config : FromConfigT*) → `Self` [source]#
Create a new instance of the component from a configuration object.
Parameters :
*   **config** (`T`) – The configuration object.
Returns :
*   **Self** – The new instance of the component.

*classmethod* **_from_config_past_version** (config : `Dict[str, Any]`, version : `int`) → `Self` [source]#
Create a new instance of the component from a previous version of the configuration object.
This is only called when the version of the configuration object is less than the current version, since in this case the schema is not known.

Parameters :
*   **config** (`Dict[str, Any]`) – The configuration object.
*   **version** (`int`) – The version of the configuration object.
Returns :
*   **Self** – The new instance of the component.

*class* **ComponentLoader** [source]#
Bases: `object`

*classmethod* **load_component** (model : `ComponentModel`| `Dict[str, Any]`, expected : `None` = `None`) → `Self` [source]#
*classmethod* **load_component** (model : `ComponentModel`| `Dict[str, Any]`, expected : `Type[ExpectedType]`) → `ExpectedType`
Load a component from a model. Intended to be used with the return type of `autogen_core.ComponentConfig.dump_component()`.

Example
```python
from autogen_core import ComponentModel
from autogen_core.models import ChatCompletionClient

component : ComponentModel = ... # type: ignore
model_client = ChatCompletionClient.load_component(component)
```
Parameters :
*   **model** (`ComponentModel`) – The model to load the component from.
*   **model** – _description_
*   **expected** (`Type[ExpectedType]` | `None`, *optional*) – Explicit type only if used directly on ComponentLoader. Defaults to None.
Returns :
*   **Self** – The loaded component.

Raises :
*   **ValueError** – If the provider string is invalid.
*   **TypeError** – Provider is not a subclass of ComponentConfigImpl, or the expected type does not match.
Returns :
*   **Self | ExpectedType** – The loaded component.

*pydantic model* **ComponentModel** [source]#
Bases: `BaseModel`
Model class for a component. Contains all information required to instantiate a component.
Show JSON schema
```json
{
    "title": "ComponentModel",
    "description": "Model class for a component. Contains all information required to instantiate a component.",
    "type": "object",
    "properties": {
        "provider": {
            "title": "Provider",
            "type": "string"
        },
        "component_type": {
            "anyOf": [
                {
                    "enum": [
                        "model",
                        "agent",
                        "tool",
                        "termination",
                        "token_provider",
                        "workbench"
                    ],
                    "type": "string"
                },
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ],
            "default": null,
            "title": "Component Type"
        },
        "version": {
            "anyOf": [
                {
                    "type": "integer"
                },
                {
                    "type": "null"
                }
            ],
            "default": null,
            "title": "Version"
        },
        "component_version": {
            "anyOf": [
                {
                    "type": "integer"
                },
                {
                    "type": "null"
                }
            ],
            "default": null,
            "title": "Component Version"
        },
        "description": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ],
            "default": null,
            "title": "Description"
        },
        "label": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ],
            "default": null,
            "title": "Label"
        },
        "config": {
            "title": "Config",
            "type": "object"
        }
    },
    "required": [
        "provider",
        "config"
    ]
}
```

Fields :
*   `component_type` (`Literal['model', 'agent', 'tool', 'termination', 'token_provider', 'workbench'] | str | None`)
*   `component_version` (`int | None`)
*   `config` (`dict[str, Any]`)
*   `description` (`str | None`)
*   `label` (`str | None`)
*   `provider` (`str`)
*   `version` (`int | None`)

*field* **provider**: `str` [Required]
Describes how the component can be instantiated.

*field* **component_type**: `ComponentType` | `None` = `None`
Logical type of the component. If missing, the component assumes the default type of the provider.

*field* **version**: `int`| `None` = `None`
Version of the component specification. If missing, the component assumes whatever is the current version of the library used to load it. This is obviously dangerous and should be used for user authored ephmeral config. For all other configs version should be specified.

*field* **component_version**: `int`| `None` = `None`
Version of the component. If missing, the component assumes the default version of the provider.

*field* **description**: `str`| `None` = `None`
Description of the component.

*field* **label**: `str`| `None` = `None`
Human readable label for the component. If missing the component assumes the class name of the provider.

*field* **config**: `dict[str, Any]` [Required]
The schema validated config field is passed to a given class’s implmentation of `autogen_core.ComponentConfigImpl._from_config()` to create a new instance of the component class.

*class* **ComponentSchemaType** [source]#
Bases: `Generic[ConfigT]`

`component_config_schema`: `Type[ConfigT]`
The Pydantic model class which represents the configuration of the component.

`required_class_vars` = `['component_config_schema', 'component_type']`

*class* **ComponentToConfig** [source]#
Bases: `Generic[ToConfigT]`
The two methods a class must implement to be a component.
Parameters :
*   **Protocol** (`ConfigT`) – Type which derives from `pydantic.BaseModel`.

`component_type`: `ClassVar[Literal[ 'model' , 'agent' , 'tool' , 'termination' , 'token_provider' , 'workbench' ] | str]`
The logical type of the component.

`component_version`: `ClassVar[int]` = `1`
The version of the component, if schema incompatibilities are introduced this should be updated.

`component_provider_override`: `ClassVar[str|None]` = `None`
Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

`component_description`: `ClassVar[str|None]` = `None`
A description of the component. If not provided, the docstring of the class will be used.

`component_label`: `ClassVar[str|None]` = `None`
A human readable label for the component. If not provided, the component class name will be used.

`_to_config` () → `ToConfigT` [source]#
Dump the configuration that would be requite to create a new instance of a component matching the configuration of this instance.

Returns :
*   **T** – The configuration of the component.

**dump_component** () → `ComponentModel` [source]#
Dump the component to a model that can be loaded back in.
Raises :
*   **TypeError** – If the component is a local class.
Returns :
*   **ComponentModel** – The model representing the component.

**is_component_class** (cls : `type`) → `TypeGuard[Type[_ConcreteComponent[BaseModel]]]` [source]#

**is_component_instance** (cls : `Any`) → `TypeGuard[_ConcreteComponent[BaseModel]]` [source]#

*final class* **DropMessage** [source]#
Bases: `object`

Marker type for signalling that a message should be dropped by an intervention handler. The type itself should be returned from the handler.

*class* **InterventionHandler** (*args*, ***kwargs*) [source]#
Bases: `Protocol`
An intervention handler is a class that can be used to modify, log or drop messages that are being processed by the `autogen_core.base.AgentRuntime`.
The handler is called when the message is submitted to the runtime.
Currently the only runtime which supports this is the `autogen_core.base.SingleThreadedAgentRuntime`.

Note: Returning None from any of the intervention handler methods will result in a warning being issued and treated as “no change”. If you intend to drop a message, you should return DropMessage explicitly.
Example:
```python
from autogen_core import DefaultInterventionHandler, MessageContext, AgentId, SingleThreadedAgentRuntime
from dataclasses import dataclass
from typing import Any

@dataclass
class MyMessage:
    content: str

class MyInterventionHandler(DefaultInterventionHandler):
    async def on_send(self, message: Any, *, message_context: MessageContext, recipient: AgentId) -> MyMessage:
        if isinstance(message, MyMessage):
            message.content = message.content.upper()
        return message

runtime = SingleThreadedAgentRuntime(intervention_handlers=[MyInterventionHandler()])
```
*async* **on_send** (message : `Any`, ***, message_context : `MessageContext`, recipient : `AgentId`) → `Any`| `type[DropMessage]` [source]#
Called when a message is submitted to the AgentRuntime using `autogen_core.base.AgentRuntime.send_message()`.

*async* **on_publish** (message : `Any`, ***, message_context : `MessageContext`) → `Any`| `type[DropMessage]` [source]#
Called when a message is published to the AgentRuntime using `autogen_core.base.AgentRuntime.publish_message()`.

*async* **on_response** (message : `Any`, ***, sender : `AgentId`, recipient : `AgentId`| `None`) → `Any`| `type[DropMessage]` [source]#
Called when a response is received by the AgentRuntime from an Agent’s message handler returning a value.

*class* **DefaultInterventionHandler** (*args*, ***kwargs*) [source]#
Bases: `InterventionHandler`

Simple class that provides a default implementation for all intervention handler methods, that simply returns the message unchanged. Allows for easy subclassing to override only the desired methods.

*async* **on_send** (message : `Any`, ***, message_context : `MessageContext`, recipient : `AgentId`) → `Any`| `type[DropMessage]` [source]#
Called when a message is submitted to the AgentRuntime using `autogen_core.base.AgentRuntime.send_message()`.

*async* **on_publish** (message : `Any`, ***, message_context : `MessageContext`) → `Any`| `type[DropMessage]` [source]#
Called when a message is published to the AgentRuntime using `autogen_core.base.AgentRuntime.publish_message()`.

*async* **on_response** (message : `Any`, ***, sender : `AgentId`, recipient : `AgentId`| `None`) → `Any`| `type[DropMessage]` [source]#
Called when a response is received by the AgentRuntime from an Agent’s message handler returning a value.

`ComponentType`
alias of `Literal['model', 'agent', 'tool', 'termination', 'token_provider', 'workbench'] | str`
