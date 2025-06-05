# autogen_ext.agents.file_surfer

*class* FileSurfer (name : str, model_client : ChatCompletionClient, description : str *= DEFAULT_DESCRIPTION*, base_path : str *= os.getcwd()*)
Bases: BaseChatAgent, Component[ FileSurferConfig ]

An agent, used by MagenticOne, that acts as a local file previewer. FileSurfer can open and read a variety of common file types, and can navigate the local file hierarchy.

## Installation:

```
pip install "autogen-ext[file-surfer]"
```

## Parameters:

*   **name** (*str*) – The agent’s name.
*   **model_client** (*ChatCompletionClient*) – The model to use (must be tool-use enabled).
*   **description** (*str*) – The agent’s description used by the team. Defaults to DEFAULT_DESCRIPTION.
*   **base_path** (*str*) – The base path to use for the file browser. Defaults to the current working directory.

## Constants:

`DEFAULT_DESCRIPTION` *= 'An agent that can handle local files.'*

`DEFAULT_SYSTEM_MESSAGES` *= [SystemMessage(content='\n You are a helpful AI Assistant.\n When given a user query, use available functions to help the user with their request.', type='SystemMessage')]*

## Class Methods:

### *classmethod* _from_config (*config : FileSurferConfig*) → Self

Create a new instance of the component from a configuration object.

**Parameters :**

*   **config** (*T*) – The configuration object.

**Returns :**

*   **Self** – The new instance of the component.

### _to_config () → FileSurferConfig

Dump the configuration that would be required to create a new instance of a component matching the configuration of this instance.

**Returns :**

*   **T** – The configuration of the component.

## Component Configuration and Provider:

`component_config_schema`
alias of FileSurferConfig

`component_provider_override: ClassVar [str| None]* = 'autogen_ext.agents.file_surfer.FileSurfer'*
Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

## Asynchronous Methods:

### *async* on_messages (messages : Sequence[BaseChatMessage], cancellation_token : CancellationToken) → Response

Handles incoming messages and returns a response.

**Note**
Agents are stateful and the messages passed to this method should be the new messages since the last call to this method. The agent should maintain its state between calls to this method. For example, if the agent needs to remember the previous messages to respond to the current message, it should store the previous messages in the agent state.

### *async* on_reset (cancellation_token : CancellationToken) → None

Resets the agent to its initialization state.

## Properties:

### *property* produced_message_types: Sequence[type[BaseChatMessage]]

The types of messages that the agent produces in the `Response.chat_message` field. They must be `BaseChatMessage` types.
