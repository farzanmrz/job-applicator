The provided web documentation excerpts for `autogen_agentchat.base` have been meticulously converted into a single, comprehensive markdown file, precisely mirroring the original webpage content and structure. This conversion ensures all text, explanations, code examples, and outputs are included, with an accurate representation of class and function definitions, parameters, and their intricate details. The resulting markdown is clean, well-organized, and designed to be LLM-ready, offering a complete and accessible overview of the module's components and protocols.

---

### autogen_agentchat.base

*   0.2 Docs
*   GitHub
*   Discord
*   Twitter
*   GitHub
*   Discord
*   Twitter

#### *class* AndTerminationCondition (* conditions : TerminationCondition)[source]

Bases: `TerminationCondition`, `Component[ AndTerminationConditionConfig ]`

`component_config_schema`#alias of `AndTerminationConditionConfig`

`component_provider_override`: `ClassVar [str| None *]` *= `autogen_agentchat.base.AndTerminationCondition`* #Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

`component_type *: ClassVar [ ComponentType ]*` *= `'termination'`* #The logical type of the component.

*async* reset ( ) → None[source]#Reset the termination condition.

*property* terminated: bool#Check if the termination condition has been reached

#### *class* ChatAgent ( ** args* , *** kwargs* )[source]

Bases: `ABC`, `TaskRunner`, `ComponentBase[ BaseModel ]`

Protocol for a chat agent.

*abstract async* close ( ) → None[source]#Release any resources held by the agent.

`component_type *: ClassVar [ ComponentType ]*` *= `'agent'`* #The logical type of the component.

*abstract property* description: str#The description of the agent. This is used by team to make decisions about which agents to use. The description should describe the agent’s capabilities and how to interact with it.

*abstract async* load_state (state : Mapping[str, Any *]* ) → None[source]#Restore agent from saved state

*abstract property* name: str#The name of the agent. This is used by team to uniquely identify the agent. It should be unique within the team.

*abstract async* on_messages (messages : Sequence[BaseChatMessage *]* , cancellation_token : CancellationToken) → Response[source]#Handles incoming messages and returns a response.

*abstract* on_messages_stream (messages : Sequence[BaseChatMessage *]* , cancellation_token : CancellationToken) → AsyncGenerator[BaseAgentEvent| BaseChatMessage| Response, None][source]#Handles incoming messages and returns a stream of inner messages and and the final item is the response.

*abstract async* on_pause (cancellation_token : CancellationToken) → None[source]#Called when the agent is paused. The agent may be running in `on_messages()` or `on_messages_stream()` when this method is called.

*abstract async* on_reset (cancellation_token : CancellationToken) → None[source]#Resets the agent to its initialization state.

*abstract async* on_resume (cancellation_token : CancellationToken) → None[source]#Called when the agent is resumed. The agent may be running in `on_messages()` or `on_messages_stream()` when this method is called.

*abstract property* produced_message_types: Sequence[type[BaseChatMessage *] ]* #The types of messages that the agent produces in the `Response.chat_message` field. They must be `BaseChatMessage` types.

*abstract async* save_state ( ) → Mapping[str, Any][source]#Save agent state for later restoration

#### *pydantic model* Handoff[source]

Bases: `BaseModel`

Handoff configuration.

Show JSON schema

```json
{
  "title" : "Handoff",
  "description" : "Handoff configuration.",
  "type" : "object",
  "properties" : {
    "target" : {
      "title" : "Target",
      "type" : "string"
    },
    "description" : {
      "default" : "",
      "title" : "Description",
      "type" : "string"
    },
    "name" : {
      "default" : "",
      "title" : "Name",
      "type" : "string"
    },
    "message" : {
      "default" : "",
      "title" : "Message",
      "type" : "string"
    }
  },
  "required" : [
    "target"
  ]
}
```

Fields :

*   `description` (str)
*   `message` (str)
*   `name` (str)
*   `target` (str)

Validators :

*   `set_defaults` » `all fields`

*field* description: str *= `''`* #The description of the handoff such as the condition under which it should happen and the target agent’s ability. If not provided, it is generated from the target agent’s name.

Validated by :

*   `set_defaults`

*field* message: str *= `''`* #The message to the target agent. By default, it will be the result for the handoff tool. If not provided, it is generated from the target agent’s name.

Validated by :

*   `set_defaults`

*field* name: str *= `''`* #The name of this handoff configuration. If not provided, it is generated from the target agent’s name.

Validated by :

*   `set_defaults`

*field* target: str *[Required]* #The name of the target agent to handoff to.

Validated by :

*   `set_defaults`

*validator* set_defaults *»* all fields [source]#

*property* handoff_tool: BaseTool *[ BaseModel , BaseModel ]* #Create a handoff tool from this handoff configuration.

#### *class* OrTerminationCondition (* conditions : TerminationCondition)[source]

Bases: `TerminationCondition`, `Component[ OrTerminationConditionConfig ]`

`component_config_schema`#alias of `OrTerminationConditionConfig`

`component_provider_override`: `ClassVar [str| None *]*` *= `'autogen_agentchat.base.OrTerminationCondition'`* #Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

`component_type *: ClassVar [ ComponentType ]*` *= `'termination'`* #The logical type of the component.

*async* reset ( ) → None[source]#Reset the termination condition.

*property* terminated: bool#Check if the termination condition has been reached

#### *class* Response ( *** , chat_message : BaseChatMessage, inner_messages : Sequence[BaseAgentEvent| BaseChatMessage] | None *= None* )[source]

Bases: `object`

A response from calling `ChatAgent.on_messages()`.

`chat_message`: `BaseChatMessage`#A chat message produced by the agent as the response.

`inner_messages`: `Sequence[BaseAgentEvent| BaseChatMessage] | None` *= `None`* #Inner messages produced by the agent, they can be `BaseAgentEvent` or `BaseChatMessage`.

#### *pydantic model* TaskResult[source]

Result of running a task.

Show JSON schema

```json
{
  "title" : "TaskResult",
  "description" : "Result of running a task.",
  "type" : "object",
  "properties" : {
    "messages" : {
      "items" : {
        "anyOf" : [
          {
            "$ref" : "#/$defs/BaseAgentEvent"
          },
          {
            "$ref" : "#/$defs/BaseChatMessage"
          }
        ]
      },
      "title" : "Messages",
      "type" : "array"
    },
    "stop_reason" : {
      "anyOf" : [
        {
          "type" : "string"
        },
        {
          "type" : "null"
        }
      ],
      "default" : null,
      "title" : "Stop Reason"
    }
  },
  "$defs" : {
    "BaseAgentEvent" : {
      "description" : "Base class for agent events.\n\n.. note::\n\n If you want to create a new message type for signaling observable events\n to user and application, inherit from this class.\n\nAgent events are used to signal actions and thoughts produced by agents\nand teams to user and applications. They are not used for agent-to-agent\ncommunication and are not expected to be processed by other agents.\n\nYou should override the :meth:`to_text` method if you want to provide\na custom rendering of the content.",
      "properties" : {
        "source" : {
          "title" : "Source",
          "type" : "string"
        },
        "models_usage" : {
          "anyOf" : [
            {
              "$ref" : "#/$defs/RequestUsage"
            },
            {
              "type" : "null"
            }
          ],
          "default" : null
        },
        "metadata" : {
          "additionalProperties" : {
            "type" : "string"
          },
          "default" : {},
          "title" : "Metadata",
          "type" : "object"
        }
      },
      "required" : [
        "source"
      ],
      "title" : "BaseAgentEvent",
      "type" : "object"
    },
    "BaseChatMessage" : {
      "description" : "Abstract base class for chat messages.\n\n.. note::\n\n If you want to create a new message type that is used for agent-to-agent\n communication, inherit from this class, or simply use\n :class:`StructuredMessage` if your content type is a subclass of\n Pydantic BaseModel.\n\nThis class is used for messages that are sent between agents in a chat\nconversation. Agents are expected to process the content of the\nmessage using models and return a response as another :class:`BaseChatMessage`.",
      "properties" : {
        "source" : {
          "title" : "Source",
          "type" : "string"
        },
        "models_usage" : {
          "anyOf" : [
            {
              "$ref" : "#/$defs/RequestUsage"
            },
            {
              "type" : "null"
            }
          ],
          "default" : null
        },
        "metadata" : {
          "additionalProperties" : {
            "type" : "string"
          },
          "default" : {},
          "title" : "Metadata",
          "type" : "object"
        }
      },
      "required" : [
        "source"
      ],
      "title" : "BaseChatMessage",
      "type" : "object"
    },
    "RequestUsage" : {
      "properties" : {
        "prompt_tokens" : {
          "title" : "Prompt Tokens",
          "type" : "integer"
        },
        "completion_tokens" : {
          "title" : "Completion Tokens",
          "type" : "integer"
        }
      },
      "required" : [
        "prompt_tokens",
        "completion_tokens"
      ],
      "title" : "RequestUsage",
      "type" : "object"
    }
  },
  "required" : [
    "messages"
  ]
}
```

Fields :

*   `messages` (`Sequence[autogen_agentchat.messages.BaseAgentEvent | autogen_agentchat.messages.BaseChatMessage]`)
*   `stop_reason` (`str | None`)

*field* messages: `Sequence[BaseAgentEvent| BaseChatMessage *]*` *[Required]* #Messages produced by the task.

*field* stop_reason: `str| None` *= `None`* #The reason the task stopped.

#### *class* TaskRunner ( ** args* , *** kwargs* )[source]

Bases: `Protocol`

A task runner.

*async* run ( *** , task : str| BaseChatMessage| Sequence[BaseChatMessage] | None *= None* , cancellation_token : CancellationToken| None *= None* ) → TaskResult[source]#Run the task and return the result.

The task can be a string, a single message, or a sequence of messages.
The runner is stateful and a subsequent call to this method will continue from where the previous call left off. If the task is not specified, the runner will continue with the current task.

`run_stream` ( *** , task : str| BaseChatMessage| Sequence[BaseChatMessage] | None *= None* , cancellation_token : CancellationToken| None *= None* ) → AsyncGenerator[BaseAgentEvent| BaseChatMessage| TaskResult, None][source]#Run the task and produces a stream of messages and the final result `TaskResult` as the last item in the stream.

The task can be a string, a single message, or a sequence of messages.
The runner is stateful and a subsequent call to this method will continue from where the previous call left off. If the task is not specified, the runner will continue with the current task.

#### *class* Team ( ** args* , *** kwargs* )[source]

Bases: `ABC`, `TaskRunner`, `ComponentBase[ BaseModel ]`

`component_type *: ClassVar [ ComponentType ]*` *= `'team'`* #The logical type of the component.

*abstract async* load_state (state : Mapping[str, Any *]* ) → None[source]#Load the state of the team.

*abstract async* pause ( ) → None[source]#Pause the team and all its participants. This is useful for pausing the `autogen_agentchat.base.TaskRunner.run()` or `autogen_agentchat.base.TaskRunner.run_stream()` methods from concurrently, while keeping them alive.

*abstract async* reset ( ) → None[source]#Reset the team and all its participants to its initial state.

*abstract async* resume ( ) → None[source]#Resume the team and all its participants from a pause after `pause()` was called.

*abstract async* save_state ( ) → Mapping[str, Any][source]#Save the current state of the team.

#### *exception* TerminatedException[source]

Bases: `BaseException`

#### *class* TerminationCondition[source]

Bases: `ABC`, `ComponentBase[ BaseModel ]`

A stateful condition that determines when a conversation should be terminated.
A termination condition is a callable that takes a sequence of `BaseChatMessage` objects since the last time the condition was called, and returns a `StopMessage` if the conversation should be terminated, or `None` otherwise. Once a termination condition has been reached, it must be reset before it can be used again.

Termination conditions can be combined using the AND and OR operators.

Example

```python
import asyncio
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

async def main() -> None:
    # Terminate the conversation after 10 turns or if the text "TERMINATE" is mentioned.
    cond1 = MaxMessageTermination(10) | TextMentionTermination("TERMINATE")
    # Terminate the conversation after 10 turns and if the text "TERMINATE" is mentioned.
    cond2 = MaxMessageTermination(10) & TextMentionTermination("TERMINATE")
    # ...
    # Reset the termination condition.
    await cond1.reset()
    await cond2.reset()

asyncio.run(main())
```

`component_type *: ClassVar [ ComponentType ]*` *= `'termination'`* #The logical type of the component.

*abstract async* reset ( ) → None[source]#Reset the termination condition.

*abstract property* terminated: bool#Check if the termination condition has been reached
