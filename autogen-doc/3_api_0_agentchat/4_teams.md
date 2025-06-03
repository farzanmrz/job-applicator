### `autogen_agentchat.teams`

This module meticulously provides the implementation of various pre-defined multi-agent teams within the AutoGen framework. Each team is structured to inherit from the `BaseGroupChat` class, ensuring a consistent foundation for managing group interactions.

---

#### `*class* BaseGroupChat (participants : List[ChatAgent], group_chat_manager_name : str, group_chat_manager_class : type[SequentialRoutedAgent], termination_condition : TerminationCondition| None = None, max_turns : int| None = None, runtime : AgentRuntime| None = None, custom_message_types : List[type[BaseAgentEvent| BaseChatMessage]] | None = None, emit_team_events : bool = False)[source]`
Bases: `Team`, `ABC`, `ComponentBase[BaseModel]`

This serves as the foundational class for all group chat teams. To properly implement a custom group chat team, one must first create a subclass of `BaseGroupChatManager` and subsequently a subclass of `BaseGroupChat` that leverages this custom manager.

**Class Variables:**
*   `component_type : ClassVar[ComponentType] = 'team'`
    *   Defines the logical type of the component.

**Methods:**

*   `*async* load_state (state : Mapping[str, Any]) → None`
    *   **Description**: This method loads an external state, subsequently overwriting the current state of the group chat team. The loading process involves calling the `agent_load_state()` method on each participant and the group chat manager, utilizing their internal agent ID. For the expected format of the state, refer to the `save_state()` method documentation.
    *   **Parameters**:
        *   `state` (`Mapping[str, Any]`): The external state to be loaded.

*   `*async* pause () → None`
    *   **Description**: Pauses the team's participants when the team is actively running by invoking their `on_pause()` method via direct RPC calls.
    *   **Attention**: This is an experimental feature introduced in v0.4.9 and is subject to potential changes or removal in future releases. The team **must** be initialized prior to being paused. Distinct from termination, pausing the team does not cause the `run()` or `run_stream()` methods to return. It merely calls `on_pause()` on each participant; if a participant does not implement this method, it will result in a no-op.
    *   **Note**: It is the explicit responsibility of the agent class to manage the pause state and ensure that the agent can be successfully resumed later. Developers should implement the `on_pause()` method within their agent class for any custom pause behavior, as the default agent behavior is to do nothing when called.
    *   **Raises**:
        *   `RuntimeError`: If the team has not been initialized. Exceptions propagated from participants during their `on_pause` implementation will also be raised by this method.

*   `*async* reset () → None`
    *   **Description**: Resets the team and all its participants to their initial state.
    *   **Note**: The team **must** be stopped before it can be reset.
    *   **Raises**:
        *   `RuntimeError`: If the team has not been initialized or is currently running.
    *   **Example using the `RoundRobinGroupChat` team**:
        ```python
        import asyncio
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        async def main() -> None:
            model_client = OpenAIChatCompletionClient(model="gpt-4o")
            agent1 = AssistantAgent("Assistant1", model_client=model_client)
            agent2 = AssistantAgent("Assistant2", model_client=model_client)
            termination = MaxMessageTermination(3)
            team = RoundRobinGroupChat([agent1, agent2], termination_condition=termination)

            stream = team.run_stream(task="Count from 1 to 10, respond one at a time.")
            async for message in stream:
                print(message)

            # Reset the team.
            await team.reset()

            stream = team.run_stream(task="Count from 1 to 10, respond one at a time.")
            async for message in stream:
                print(message)

        asyncio.run(main())
        ```

*   `*async* resume () → None`
    *   **Description**: Resumes the team's participants when the team is running and paused by calling their `on_resume()` method via direct RPC calls.
    *   **Attention**: This is an experimental feature introduced in v0.4.9 and is subject to potential changes or removal in future releases. The team **must** be initialized prior to being resumed. Unlike termination or restarting with a new task, resuming the team does not cause the `run()` or `run_stream()` methods to return. It specifically calls `on_resume()` on each participant; if a participant does not implement this method, it will be a no-op.
    *   **Note**: It is the responsibility of the agent class to manage the resume behavior and ensure that the agent successfully continues from its paused state. Implement the `on_resume()` method in your agent class for any custom resume behavior.
    *   **Raises**:
        *   `RuntimeError`: If the team has not been initialized. Exceptions propagated from participants during their `on_resume` method implementation will also be raised by this method.

*   `*async* run (***, task : str| BaseChatMessage| Sequence[BaseChatMessage] | None = None, cancellation_token : CancellationToken| None = None) → TaskResult`
    *   **Description**: Executes the team and returns the final result. The base implementation utilizes `run_stream()` to run the team and then consolidates the final result. Once the team ceases operation, its termination condition is reset.
    *   **Parameters**:
        *   `task` (`str | BaseChatMessage | Sequence[BaseChatMessage] | None`): The task to be executed by the team. This can be provided as a string, a single `BaseChatMessage`, or a list of `BaseChatMessage` instances.
        *   `cancellation_token` (`CancellationToken | None`): An optional cancellation token designed to immediately terminate the task. Be aware that setting a cancellation token might lead to an inconsistent state for the team and may not reset the termination condition. For a graceful stop, `ExternalTermination` is recommended instead.
    *   **Returns**:
        *   `result` (`TaskResult`): The outcome of the task, encapsulated as a `TaskResult`. This result object includes the messages generated by the team and the reason for its cessation.
    *   **Example using the `RoundRobinGroupChat` team**:
        ```python
        import asyncio
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        async def main() -> None:
            model_client = OpenAIChatCompletionClient(model="gpt-4o")
            agent1 = AssistantAgent("Assistant1", model_client=model_client)
            agent2 = AssistantAgent("Assistant2", model_client=model_client)
            termination = MaxMessageTermination(3)
            team = RoundRobinGroupChat([agent1, agent2], termination_condition=termination)

            result = await team.run(task="Count from 1 to 10, respond one at a time.")
            print(result)

            # Run the team again without a task to continue the previous task.
            result = await team.run()
            print(result)

        asyncio.run(main())
        ```
    *   **Example using the `CancellationToken` to cancel the task**:
        ```python
        import asyncio
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_core import CancellationToken
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        async def main() -> None:
            model_client = OpenAIChatCompletionClient(model="gpt-4o")
            agent1 = AssistantAgent("Assistant1", model_client=model_client)
            agent2 = AssistantAgent("Assistant2", model_client=model_client)
            termination = MaxMessageTermination(3)
            team = RoundRobinGroupChat([agent1, agent2], termination_condition=termination)
            cancellation_token = CancellationToken()

            # Create a task to run the team in the background.
            run_task = asyncio.create_task(
                team.run(
                    task="Count from 1 to 10, respond one at a time.",
                    cancellation_token=cancellation_token,
                )
            )

            # Wait for 1 second and then cancel the task.
            await asyncio.sleep(1)
            cancellation_token.cancel()

            # This will raise a cancellation error.
            await run_task

        asyncio.run(main())
        ```

*   `*async* run_stream (***, task : str| BaseChatMessage| Sequence[BaseChatMessage] | None = None, cancellation_token : CancellationToken| None = None) → AsyncGenerator[BaseAgentEvent| BaseChatMessage| TaskResult, None]`
    *   **Description**: Executes the team and yields a stream of messages, culminating in the final `TaskResult` as the last item within the stream. Upon the team's cessation, its termination condition is reset.
    *   **Note**: Should an agent produce a `ModelClientStreamingChunkEvent`, this message will be yielded within the stream but will not be incorporated into the collection of messages.
    *   **Parameters**:
        *   `task` (`str | BaseChatMessage | Sequence[BaseChatMessage] | None`): The task to be executed by the team. This can be provided as a string, a single `BaseChatMessage`, or a list of `BaseChatMessage` instances.
        *   `cancellation_token` (`CancellationToken | None`): An optional cancellation token to immediately terminate the task. Be aware that setting a cancellation token might lead to an inconsistent state for the team and may not reset the termination condition. For a graceful stop, `ExternalTermination` is recommended instead.
    *   **Returns**:
        *   `stream` (`AsyncGenerator`): An asynchronous generator that yields `BaseAgentEvent`, `BaseChatMessage`, and finally, the `TaskResult` as the ultimate item in the stream.
    *   **Example using the `RoundRobinGroupChat` team**:
        ```python
        import asyncio
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        async def main() -> None:
            model_client = OpenAIChatCompletionClient(model="gpt-4o")
            agent1 = AssistantAgent("Assistant1", model_client=model_client)
            agent2 = AssistantAgent("Assistant2", model_client=model_client)
            termination = MaxMessageTermination(3)
            team = RoundRobinGroupChat([agent1, agent2], termination_condition=termination)

            stream = team.run_stream(task="Count from 1 to 10, respond one at a time.")
            async for message in stream:
                print(message)

            # Run the team again without a task to continue the previous task.
            stream = team.run_stream()
            async for message in stream:
                print(message)

        asyncio.run(main())
        ```
    *   **Example using the `CancellationToken` to cancel the task**:
        ```python
        import asyncio
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_agentchat.ui import Console
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_core import CancellationToken
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        async def main() -> None:
            model_client = OpenAIChatCompletionClient(model="gpt-4o")
            agent1 = AssistantAgent("Assistant1", model_client=model_client)
            agent2 = AssistantAgent("Assistant2", model_client=model_client)
            termination = MaxMessageTermination(3)
            team = RoundRobinGroupChat([agent1, agent2], termination_condition=termination)
            cancellation_token = CancellationToken()

            # Create a task to run the team in the background.
            run_task = asyncio.create_task(
                Console(
                    team.run_stream(
                        task="Count from 1 to 10, respond one at a time.",
                        cancellation_token=cancellation_token,
                    )
                )
            )

            # Wait for 1 second and then cancel the task.
            await asyncio.sleep(1)
            cancellation_token.cancel()

            # This will raise a cancellation error.
            await run_task

        asyncio.run(main())
        ```

*   `*async* save_state () → Mapping[str, Any]`
    *   **Description**: Saves the current state of the group chat team.
    *   **Details**: The state is captured by invoking the `agent_save_state()` method on each participant and the group chat manager, utilizing their internal agent ID. The returned state is presented as a nested dictionary, structured with an `agent_states` key pointing to another dictionary where agent names serve as keys and their respective states as values.
        ```json
        { "agent_states": { "agent1": ..., "agent2": ..., "RoundRobinGroupChatManager": ... } }
        ```
    *   **Note**: As of v0.4.9, the state utilizes the agent name as the key instead of the agent ID, and the `team_id` field has been removed. This modification enhances state portability across different teams and runtimes. Be advised that states saved in the old format may not be compatible with the new format in future releases.
    *   **Caution**: Invoking `save_state()` on a team while it is actively running may result in an inconsistent or unexpected state. It is strongly recommended to call this method only when the team is not running or after it has ceased operation.

---

#### `*pydantic model* DiGraph`
Bases: `BaseModel`

This Pydantic model defines a directed graph structure, encompassing nodes and edges. `GraphFlow` leverages this structure to precisely determine execution order and conditions within complex agent workflows.

**Warning**: This is an experimental feature, and its API is subject to change in future releases.

**JSON Schema**:
```json
{
   "title" : "DiGraph",
   "description" : "Defines a directed graph structure with nodes and edges.\n:class:`GraphFlow` uses this to determine execution order and conditions.\n\n.. warning::\n\n This is an experimental feature, and the API will change in the future releases.",
   "type" : "object",
   "properties" : {
      "nodes" : {
         "additionalProperties" : {
            "$ref" : "#/$defs/DiGraphNode"
         },
         "title" : "Nodes",
         "type" : "object"
      },
      "default_start_node" : {
         "anyOf" : [
            {
               "type" : "string"
            },
            {
               "type" : "null"
            }
         ],
         "default" : null,
         "title" : "Default Start Node"
      }
   },
   "$defs" : {
      "DiGraphEdge" : {
         "description" : "Represents a directed edge in a :class:`DiGraph`, with an optional execution condition.\n\n.. warning::\n\n This is an experimental feature, and the API will change in the future releases.",
         "properties" : {
            "target" : {
               "title" : "Target",
               "type" : "string"
            },
            "condition" : {
               "anyOf" : [
                  {
                     "type" : "string"
                  },
                  {
                     "type" : "null"
                  }
               ],
               "default" : null,
               "title" : "Condition"
            }
         },
         "required" : [
            "target"
         ],
         "title" : "DiGraphEdge",
         "type" : "object"
      },
      "DiGraphNode" : {
         "description" : "Represents a node (agent) in a :class:`DiGraph`, with its outgoing edges and activation type.\n\n.. warning::\n\n This is an experimental feature, and the API will change in the future releases.",
         "properties" : {
            "name" : {
               "title" : "Name",
               "type" : "string"
            },
            "edges" : {
               "default" : [],
               "items" : {
                  "$ref" : "#/$defs/DiGraphEdge"
               },
               "title" : "Edges",
               "type" : "array"
            },
            "activation" : {
               "default" : "all",
               "enum" : [
                  "all",
                  "any"
               ],
               "title" : "Activation",
               "type" : "string"
            }
         },
         "required" : [
            "name"
         ],
         "title" : "DiGraphNode",
         "type" : "object"
      }
   },
   "required" : [
      "nodes"
   ]
}
```

**Fields**:
*   `default_start_node` (`str | None`)
*   `nodes` (`Dict[str, autogen_agentchat.teams._group_chat._graph._digraph_group_chat.DiGraphNode]`) `[Required]`

**Methods:**
*   `get_has_cycles () → bool`
    *   **Description**: Indicates whether the graph contains at least one cycle with valid exit conditions.

*   `get_leaf_nodes () → Set[str]`
    *   **Description**: Returns nodes that possess no outgoing edges, effectively representing the final output nodes of the graph.

*   `get_parents () → Dict[str, List[str]]`
    *   **Description**: Computes and returns a mapping where each node is associated with its direct parent nodes.

*   `get_start_nodes () → Set[str]`
    *   **Description**: Returns nodes that have no incoming edges, signifying the entry points of the graph.

*   `graph_validate () → None`
    *   **Description**: Validates the graph's structural integrity and its execution rules.

*   `has_cycles_with_exit () → bool`
    *   **Description**: Checks for the presence of any cycles within the graph and verifies that each detected cycle includes at least one conditional edge.
    *   **Returns**:
        *   `bool`: `True` if there is at least one cycle and all cycles possess an exit condition. `False` if no cycles are detected.
    *   **Raises**:
        *   `ValueError`: If a cycle is detected that lacks any conditional exit edge.

*   `model_post_init (*context : Any, /) → None`
    *   **Description**: This function is intended to behave like a `BaseModel` method for initializing private attributes. It accepts `context` as an argument, mirroring the data passed by `pydantic-core` when this method is invoked.
    *   **Parameters**:
        *   `self`: The `BaseModel` instance itself.
        *   `context`: The contextual information.

---

#### `*class* DiGraphBuilder`
Bases: `object`

This class provides a fluent builder interface for constructing `DiGraph` execution graphs, which are subsequently used within `GraphFlow`.

**Warning**: This is an experimental feature, and its API is subject to change in future releases.

This utility offers a convenient, programmatic approach to building intricate graphs of agent interactions, capable of defining sophisticated execution flows such as:
*   Sequential chains
*   Parallel fan-outs
*   Conditional branching
*   Cyclic loops equipped with safe exits

Within the graph, each node distinctly represents an agent. Edges delineate the execution paths between agents and can optionally be conditioned based on message content. The builder is fully compatible with the `Graph` runner and provides support for both standard and filtered agents.

**Key Methods:**
*   `add_node(agent, activation)`: Facilitates the addition of an agent node to the graph.
*   `add_edge(source, target, condition)`: Enables the connection of two nodes, with an optional condition.
*   `add_conditional_edges(source, condition_to_target)`: Allows for the addition of multiple conditional edges originating from a single source.
*   `set_entry_point(agent)`: Defines the default start node for the graph (this is optional).
*   `build()`: Generates a validated `DiGraph` instance.
*   `get_participants()`: Returns the list of agents that have been added to the builder.

**Examples:**

*   **Sequential Flow A → B → C**:
    ```python
    >>> builder = GraphBuilder()
    >>> builder.add_node(agent_a).add_node(agent_b).add_node(agent_c)
    >>> builder.add_edge(agent_a, agent_b).add_edge(agent_b, agent_c)
    >>> team = Graph(
    ... participants = builder.get_participants(),
    ... graph = builder.build(),
    ... termination_condition = MaxMessageTermination(5),
    ... )
    ```

*   **Parallel Fan-out A → (B, C)**:
    ```python
    >>> builder = GraphBuilder()
    >>> builder.add_node(agent_a).add_node(agent_b).add_node(agent_c)
    >>> builder.add_edge(agent_a, agent_b).add_edge(agent_a, agent_c)
    ```

*   **Conditional Branching A → B (“yes”), A → C (“no”)**:
    ```python
    >>> builder = GraphBuilder()
    >>> builder.add_node(agent_a).add_node(agent_b).add_node(agent_c)
    >>> builder.add_conditional_edges(agent_a, { "yes" : agent_b, "no" : agent_c })
    ```

*   **Loop: A → B → A (“loop”), B → C (“exit”)**:
    ```python
    >>> builder = GraphBuilder()
    >>> builder.add_node(agent_a).add_node(agent_b).add_node(agent_c)
    >>> builder.add_edge(agent_a, agent_b)
    >>> builder.add_conditional_edges(agent_b, { "loop" : agent_a, "exit" : agent_c })
    ```

**Methods:**
*   `add_conditional_edges (source : str| ChatAgent, condition_to_target : Dict[str, str| ChatAgent]) → DiGraphBuilder`
    *   **Description**: Adds multiple conditional edges stemming from a source node, where the target is determined by condition strings.
    *   **Parameters**:
        *   `source` (`str | ChatAgent`): The source node (agent) from which edges originate.
        *   `condition_to_target` (`Dict[str, str | ChatAgent]`): A dictionary mapping condition strings to their respective target nodes (agents).
    *   **Returns**:
        *   `DiGraphBuilder`: The `DiGraphBuilder` instance, allowing for method chaining.

*   `add_edge (source : str| ChatAgent, target : str| ChatAgent, condition : str| None = None) → DiGraphBuilder`
    *   **Description**: Adds a directed edge connecting a source to a target node, with an optional condition.
    *   **Parameters**:
        *   `source` (`str | ChatAgent`): The source node (agent) of the edge.
        *   `target` (`str | ChatAgent`): The target node (agent) of the edge.
        *   `condition` (`str | None`, optional): An optional string condition for executing this edge. Defaults to `None` for an unconditional edge.
    *   **Returns**:
        *   `DiGraphBuilder`: The `DiGraphBuilder` instance, facilitating method chaining.

*   `add_node (agent : ChatAgent, activation : Literal['all', 'any'] = 'all') → DiGraphBuilder`
    *   **Description**: Adds a node to the graph and registers its corresponding agent.
    *   **Parameters**:
        *   `agent` (`ChatAgent`): The agent to be represented by this node.
        *   `activation` (`Literal['all', 'any']`, optional): The activation type for the node, specifying whether `all` or `any` parent nodes must complete for activation. Defaults to `all`.
    *   **Returns**:
        *   `DiGraphBuilder`: The `DiGraphBuilder` instance, enabling method chaining.

*   `build () → DiGraph`
    *   **Description**: Constructs and validates the `DiGraph` based on the defined nodes and edges.
    *   **Returns**:
        *   `DiGraph`: The validated `DiGraph` instance.

*   `get_participants () → list[ChatAgent]`
    *   **Description**: Returns a list of the agents that have been added to the builder, maintaining their insertion order.
    *   **Returns**:
        *   `list[ChatAgent]`: A list of `ChatAgent` instances.

*   `set_entry_point (name : str| ChatAgent) → DiGraphBuilder`
    *   **Description**: Designates the default starting node for the graph.
    *   **Parameters**:
        *   `name` (`str | ChatAgent`): The name or `ChatAgent` instance representing the desired entry point node.
    *   **Returns**:
        *   `DiGraphBuilder`: The `DiGraphBuilder` instance, facilitating method chaining.

---

#### `*pydantic model* DiGraphEdge`
Bases: `BaseModel`

This Pydantic model precisely represents a directed edge within a `DiGraph`, optionally including an execution condition.

**Warning**: This is an experimental feature, and its API is subject to change in future releases.

**JSON Schema**:
```json
{
   "title" : "DiGraphEdge",
   "description" : "Represents a directed edge in a :class:`DiGraph`, with an optional execution condition.\n\n.. warning::\n\n This is an experimental feature, and the API will change in the future releases.",
   "type" : "object",
   "properties" : {
      "target" : {
         "title" : "Target",
         "type" : "string"
      },
      "condition" : {
         "anyOf" : [
            {
               "type" : "string"
            },
            {
               "type" : "null"
            }
         ],
         "default" : null,
         "title" : "Condition"
      }
   },
   "required" : [
      "target"
   ]
}
```

**Fields**:
*   `condition` (`str | None`)
    *   `(Experimental)`: The condition required to execute this edge. If `None`, the edge is unconditional. If a string, the edge's execution is contingent on the presence of that string within the last agent chat message. **NOTE**: This is an experimental feature and is slated for future modification to enable more precise specification of branching conditions, similar to the `TerminationCondition` class.
*   `target` (`str`) `[Required]`

---

#### `*pydantic model* DiGraphNode`
Bases: `BaseModel`

This Pydantic model accurately represents a node (agent) within a `DiGraph`, defining its outgoing edges and its activation type.

**Warning**: This is an experimental feature, and its API is subject to change in future releases.

**JSON Schema**:
```json
{
   "title" : "DiGraphNode",
   "description" : "Represents a node (agent) in a :class:`DiGraph`, with its outgoing edges and activation type.\n\n.. warning::\n\n This is an experimental feature, and the API will change in the future releases.",
   "type" : "object",
   "properties" : {
      "name" : {
         "title" : "Name",
         "type" : "string"
      },
      "edges" : {
         "default" : [],
         "items" : {
            "$ref" : "#/$defs/DiGraphEdge"
         },
         "title" : "Edges",
         "type" : "array"
      },
      "activation" : {
         "default" : "all",
         "enum" : [
            "all",
            "any"
         ],
         "title" : "Activation",
         "type" : "string"
      }
   },
   "$defs" : {
      "DiGraphEdge" : {
         "description" : "Represents a directed edge in a :class:`DiGraph`, with an optional execution condition.\n\n.. warning::\n\n This is an experimental feature, and the API will change in the future releases.",
         "properties" : {
            "target" : {
               "title" : "Target",
               "type" : "string"
            },
            "condition" : {
               "anyOf" : [
                  {
                     "type" : "string"
                  },
                  {
                     "type" : "null"
                  }
               ],
               "default" : null,
               "title" : "Condition"
            }
         },
         "required" : [
            "target"
         ],
         "title" : "DiGraphEdge",
         "type" : "object"
      }
   },
   "required" : [
      "name"
   ]
}
```

**Fields**:
*   `activation` (`Literal['all', 'any']`)
*   `edges` (`List[DiGraphEdge]`)
*   `name` (`str`) `[Required]`

---

#### `*class* GraphFlow (participants : List[ChatAgent], graph : DiGraph, termination_condition : TerminationCondition| None = None, max_turns : int| None = None, runtime : AgentRuntime| None = None, custom_message_types : List[type[BaseAgentEvent| BaseChatMessage]] | None = None)[source]`
Bases: `BaseGroupChat`, `Component[GraphFlowConfig]`

This team orchestrates a group chat by adhering to a Directed Graph execution pattern.

**Warning**: This is an experimental feature, and its API is subject to change in future releases.

This group chat dynamically executes agents based on a directed graph (`DiGraph`) structure, enabling the construction of sophisticated workflows that include sequential execution, parallel fan-out, conditional branching, join patterns, and iterative loops with explicit exit conditions. The execution order is meticulously determined by the edges defined within the `DiGraph`. Each node within the graph directly corresponds to an agent, while edges define the flow of messages between these agents. Nodes offer configurable activation settings:
*   **All** parent nodes must complete (activation=”all”) – This is the default setting.
*   **Any** parent node completes (activation=”any”).

Conditional branching is robustly supported through the use of edge conditions, where the subsequent agent(s) are intelligently selected based on content found in the chat history. Loops are permissible, provided there is a defined condition that will eventually facilitate an exit from the loop.

**Note**: To effortlessly construct a `DiGraph`, developers are encouraged to utilize the `DiGraphBuilder` class. It offers a fluent API for adding nodes and edges, specifying entry points, and validating the graph's structure. The `GraphFlow` class is specifically engineered to be leveraged in conjunction with `DiGraphBuilder` for crafting intricate workflows.

**Parameters**:
*   `participants` (`List[ChatAgent]`): A list of the participants within the group chat.
*   `termination_condition` (`TerminationCondition | optional`): The condition that dictates when the chat should terminate.
*   `max_turns` (`int | optional`): The maximum allowed number of turns before termination is forcibly applied.
*   `graph` (`DiGraph`): The directed execution graph that precisely defines the flow and conditions for nodes.

**Raises**:
*   `ValueError`: If participant names are not unique, or if the graph validation process fails (e.g., due to cycles lacking an exit condition).

**Examples**:

*   **Sequential Flow: A → B → C**
    ```python
    import asyncio
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    async def main():
        # Initialize agents with OpenAI model clients.
        model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
        agent_a = AssistantAgent("A", model_client=model_client, system_message="You are a helpful assistant.")
        agent_b = AssistantAgent("B", model_client=model_client, system_message="Translate input to Chinese.")
        agent_c = AssistantAgent("C", model_client=model_client, system_message="Translate input to English.")

        # Create a directed graph with sequential flow A -> B -> C.
        builder = DiGraphBuilder()
        builder.add_node(agent_a).add_node(agent_b).add_node(agent_c)
        builder.add_edge(agent_a, agent_b).add_edge(agent_b, agent_c)
        graph = builder.build()

        # Create a GraphFlow team with the directed graph.
        team = GraphFlow(
            participants=[agent_a, agent_b, agent_c],
            graph=graph,
            termination_condition=MaxMessageTermination(5),
        )

        # Run the team and print the events.
        async for event in team.run_stream(task="Write a short story about a cat."):
            print(event)

    asyncio.run(main())
    ```

*   **Parallel Fan-out: A → (B, C)**
    ```python
    import asyncio
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    async def main():
        # Initialize agents with OpenAI model clients.
        model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
        agent_a = AssistantAgent("A", model_client=model_client, system_message="You are a helpful assistant.")
        agent_b = AssistantAgent("B", model_client=model_client, system_message="Translate input to Chinese.")
        agent_c = AssistantAgent("C", model_client=model_client, system_message="Translate input to Japanese.")

        # Create a directed graph with fan-out flow A -> (B, C).
        builder = DiGraphBuilder()
        builder.add_node(agent_a).add_node(agent_b).add_node(agent_c)
        builder.add_edge(agent_a, agent_b).add_edge(agent_a, agent_c)
        graph = builder.build()

        # Create a GraphFlow team with the directed graph.
        team = GraphFlow(
            participants=[agent_a, agent_b, agent_c],
            graph=graph,
            termination_condition=MaxMessageTermination(5),
        )

        # Run the team and print the events.
        async for event in team.run_stream(task="Write a short story about a cat."):
            print(event)

    asyncio.run(main())
    ```

*   **Conditional Branching: A → B (if ‘yes’) or C (if ‘no’)**
    ```python
    import asyncio
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    async def main():
        # Initialize agents with OpenAI model clients.
        model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
        agent_a = AssistantAgent(
            "A",
            model_client=model_client,
            system_message="Detect if the input is in Chinese. If it is, say 'yes', else say 'no', and nothing else.",
        )
        agent_b = AssistantAgent("B", model_client=model_client, system_message="Translate input to English.")
        agent_c = AssistantAgent("C", model_client=model_client, system_message="Translate input to Chinese.")

        # Create a directed graph with conditional branching flow A -> B ("yes"), A -> C ("no").
        builder = DiGraphBuilder()
        builder.add_node(agent_a).add_node(agent_b).add_node(agent_c)
        builder.add_edge(agent_a, agent_b, condition="yes")
        builder.add_edge(agent_a, agent_c, condition="no")
        graph = builder.build()

        # Create a GraphFlow team with the directed graph.
        team = GraphFlow(
            participants=[agent_a, agent_b, agent_c],
            graph=graph,
            termination_condition=MaxMessageTermination(5),
        )

        # Run the team and print the events.
        async for event in team.run_stream(task="AutoGen is a framework for building AI agents."):
            print(event)

    asyncio.run(main())
    ```

*   **Loop with exit condition: A → B → C (if ‘APPROVE’) or A (if ‘REJECT’)**
    ```python
    import asyncio
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import MaxMessageTermination
    from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    async def main():
        # Initialize agents with OpenAI model clients.
        model_client = OpenAIChatCompletionClient(model="gpt-4.1")
        agent_a = AssistantAgent(
            "A",
            model_client=model_client,
            system_message="You are a helpful assistant.",
        )
        agent_b = AssistantAgent(
            "B",
            model_client=model_client,
            system_message="Provide feedback on the input, if your feedback has been addressed, "
            "say 'APPROVE', else say 'REJECT' and provide a reason.",
        )
        agent_c = AssistantAgent(
            "C",
            model_client=model_client,
            system_message="Translate the final product to Korean."
        )

        # Create a loop graph with conditional exit: A -> B -> C ("APPROVE"), B -> A ("REJECT").
        builder = DiGraphBuilder()
        builder.add_node(agent_a).add_node(agent_b).add_node(agent_c)
        builder.add_edge(agent_a, agent_b)
        builder.add_conditional_edges(agent_b, {"APPROVE": agent_c, "REJECT": agent_a})
        builder.set_entry_point(agent_a)
        graph = builder.build()

        # Create a GraphFlow team with the directed graph.
        team = GraphFlow(
            participants=[agent_a, agent_b, agent_c],
            graph=graph,
            termination_condition=MaxMessageTermination(20),  # Max 20 messages to avoid infinite loop.
        )

        # Run the team and print the events.
        async for event in team.run_stream(task="Write a short poem about AI Agents."):
            print(event)

    asyncio.run(main())
    ```

**Class Variables:**
*   `component_config_schema`: Alias of `GraphFlowConfig`.
*   `component_provider_override: ClassVar[str| None] = 'autogen_agentchat.teams.GraphFlow'`
    *   Overrides the provider string for the component, preventing internal module names from becoming part of the module name.

---

#### `*class* MagenticOneGroupChat (participants : List[ChatAgent], model_client : ChatCompletionClient, ***, termination_condition : TerminationCondition| None = None, max_turns : int| None = 20, runtime : AgentRuntime| None = None, max_stalls : int = 3, final_answer_prompt : str = ORCHESTRATOR_FINAL_ANSWER_PROMPT, custom_message_types : List[type[BaseAgentEvent| BaseChatMessage]] | None = None, emit_team_events : bool = False)[source]`
Bases: `BaseGroupChat`, `Component[MagenticOneGroupChatConfig]`

This team orchestrates a group chat where participants are managed by the `MagenticOneOrchestrator`. The orchestrator adeptly handles the conversation flow, ensuring the task's efficient completion by meticulously managing the interactions among participants. The orchestrator is founded on the Magentic-One architecture, a generalist multi-agent system designed for solving complex tasks (refer to the citations below).

**Parameters**:
*   `participants` (`List[ChatAgent]`): The collection of agents participating in the group chat.
*   `model_client` (`ChatCompletionClient`): The model client designated for generating responses.
*   `termination_condition` (`TerminationCondition | optional`): The condition for the group chat's termination. Defaults to `None`. Without a specific termination condition, the group chat will proceed based on the orchestrator's inherent logic or until the `max_turns` limit is reached.
*   `max_turns` (`int | optional`): The maximum number of turns permitted in the group chat before it halts. Defaults to `20`.
*   `max_stalls` (`int | optional`): The maximum number of allowed stalls before a re-planning action is initiated. Defaults to `3`.
*   `final_answer_prompt` (`str | optional`): The LLM prompt employed to generate the conclusive answer or response from the team's transcript. A sensible default prompt is provided, particularly suitable for GPT-4o class models.
*   `custom_message_types` (`List[type[BaseAgentEvent | BaseChatMessage]] | optional`): A list detailing any custom message types that will be used within the group chat. If agents are configured to produce or utilize custom message types, they must be specified here. Ensure these custom message types are subclasses of `BaseAgentEvent` or `BaseChatMessage`.
*   `emit_team_events` (`bool | optional`): A flag indicating whether team events should be emitted via `BaseGroupChat.run_stream()`. Defaults to `False`.

**Raises**:
*   `ValueError`: Occurs in the orchestration logic if the progress ledger lacks required keys or if the selected next speaker is not valid.

**Examples**:

*   **MagenticOneGroupChat with one assistant agent**:
    ```python
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import MagenticOneGroupChat
    from autogen_agentchat.ui import Console

    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
        assistant = AssistantAgent(
            "Assistant",
            model_client=model_client,
        )
        team = MagenticOneGroupChat([assistant], model_client=model_client)
        await Console(team.run_stream(task="Provide a different proof to Fermat last theorem"))

    asyncio.run(main())
    ```

**References**:
If you utilize the `MagenticOneGroupChat` in your work, please cite the following paper:
```
@article { fourney2024magentic ,
    title = {Magentic-one: A generalist multi-agent system for solving complex tasks} ,
    author = {Fourney, Adam and Bansal, Gagan and Mozannar, Hussein and Tan, Cheng and Salinas, Eduardo and Niedtner, Friederike and Proebsting, Grace and Bassman, Griffin and Gerrits, Jack and Alber, Jacob and others} ,
    journal = {arXiv preprint arXiv:2411.04468} ,
    year = {2024}
}
```

**Methods:**
*   `*classmethod* _from_config (*config : MagenticOneGroupChatConfig) → Self`
    *   **Description**: Creates a new instance of the component directly from a configuration object.
    *   **Parameters**:
        *   `config` (`T`): The configuration object.
    *   **Returns**:
        *   `Self`: The newly created instance of the component.

*   `_to_config () → MagenticOneGroupChatConfig`
    *   **Description**: Dumps the configuration necessary to instantiate a new component instance matching the current instance's configuration.
    *   **Returns**:
        *   `T`: The configuration of the component.

**Class Variables:**
*   `component_config_schema`: Alias of `MagenticOneGroupChatConfig`.
*   `component_provider_override: ClassVar[str| None] = 'autogen_agentchat.teams.MagenticOneGroupChat'`
    *   Overrides the provider string for the component, preventing internal module names from becoming part of the module name.

---

#### `*class* RoundRobinGroupChat (participants : List[ChatAgent], termination_condition : TerminationCondition| None = None, max_turns : int| None = None, runtime : AgentRuntime| None = None, custom_message_types : List[type[BaseAgentEvent| BaseChatMessage]] | None = None, emit_team_events : bool = False)[source]`
Bases: `BaseGroupChat`, `Component[RoundRobinGroupChatConfig]`

This team effectively manages a group chat where participants take turns in a strict round-robin fashion, each publishing a message to all members. Should the team comprise only a single participant, that participant will naturally be the sole speaker.

**Parameters**:
*   `participants` (`List[BaseChatAgent]`): The collection of agents participating in the group chat.
*   `termination_condition` (`TerminationCondition | optional`): The condition that dictates the group chat's termination. Defaults to `None`. Without a specified termination condition, the group chat will continue indefinitely.
*   `max_turns` (`int | optional`): The maximum number of turns allowed in the group chat before it halts. Defaults to `None`, implying no upper limit.
*   `custom_message_types` (`List[type[BaseAgentEvent | BaseChatMessage]] | optional`): A list detailing any custom message types that will be used within the group chat. If agents are configured to produce or utilize custom message types, they must be specified here. Ensure these custom message types are subclasses of `BaseAgentEvent` or `BaseChatMessage`.
*   `emit_team_events` (`bool | optional`): A flag indicating whether team events should be emitted via `BaseGroupChat.run_stream()`. Defaults to `False`.

**Raises**:
*   `ValueError`: If no participants are provided, or if participant names are not unique.

**Examples**:

*   **A team with one participant with tools**:
    ```python
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.ui import Console

    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")

        async def get_weather(location: str) -> str:
            return f"The weather in {location} is sunny."

        assistant = AssistantAgent(
            "Assistant",
            model_client=model_client,
            tools=[get_weather],
        )
        termination = TextMentionTermination("TERMINATE")
        team = RoundRobinGroupChat([assistant], termination_condition=termination)
        await Console(team.run_stream(task="What's the weather in New York?"))

    asyncio.run(main())
    ```

*   **A team with multiple participants**:
    ```python
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.ui import Console

    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
        agent1 = AssistantAgent("Assistant1", model_client=model_client)
        agent2 = AssistantAgent("Assistant2", model_client=model_client)
        termination = TextMentionTermination("TERMINATE")
        team = RoundRobinGroupChat([agent1, agent2], termination_condition=termination)
        await Console(team.run_stream(task="Tell me some jokes."))

    asyncio.run(main())
    ```

**Methods:**
*   `*classmethod* _from_config (*config : RoundRobinGroupChatConfig) → Self`
    *   **Description**: Creates a new instance of the component directly from a configuration object.
    *   **Parameters**:
        *   `config` (`T`): The configuration object.
    *   **Returns**:
        *   `Self`: The newly created instance of the component.

*   `_to_config () → RoundRobinGroupChatConfig`
    *   **Description**: Dumps the configuration necessary to instantiate a new component instance matching the current instance's configuration.
    *   **Returns**:
        *   `T`: The configuration of the component.

**Class Variables:**
*   `component_config_schema`: Alias of `RoundRobinGroupChatConfig`.
*   `component_provider_override: ClassVar[str| None] = 'autogen_agentchat.teams.RoundRobinGroupChat'`
    *   Overrides the provider string for the component, preventing internal module names from becoming part of the module name.

---

#### `*class* SelectorGroupChat (participants : List[ChatAgent], model_client : ChatCompletionClient, ***, termination_condition : TerminationCondition| None = None, max_turns : int| None = None, runtime : AgentRuntime| None = None, selector_prompt : str = 'You are in a role play game. The following roles are available:\n{roles}.\nRead the following conversation. Then select the next role from {participants} to play. Only return the role.\n\n{history}\n\nRead the above conversation. Then select the next role from {participants} to play. Only return the role.\n', allow_repeated_speaker : bool = False, max_selector_attempts : int = 3, selector_func : Callable[[Sequence[BaseAgentEvent| BaseChatMessage]], str| None] | Callable[[Sequence[BaseAgentEvent| BaseChatMessage]], Awaitable[str| None]] | None = None, candidate_func : Callable[[Sequence[BaseAgentEvent| BaseChatMessage]], List[str]] | Callable[[Sequence[BaseAgentEvent| BaseChatMessage]], Awaitable[List[str]]] | None = None, custom_message_types : List[type[BaseAgentEvent| BaseChatMessage]] | None = None, emit_team_events : bool = False, model_client_streaming : bool = False, model_context : ChatCompletionContext| None = None)[source]`
Bases: `BaseGroupChat`, `Component[SelectorGroupChatConfig]`

This group chat team facilitates participants taking turns to publish messages to all, employing a `ChatCompletion` model to intelligently select the next speaker after each message.

**Parameters**:
*   `participants` (`List[ChatAgent]`): The collection of agents participating in the group chat. Participant names must be unique, and there must be at least two participants.
*   `model_client` (`ChatCompletionClient`): The `ChatCompletion` model client utilized for selecting the subsequent speaker.
*   `termination_condition` (`TerminationCondition | optional`): The condition that dictates the group chat's termination. Defaults to `None`. Without a specified termination condition, the group chat will continue indefinitely.
*   `max_turns` (`int | optional`): The maximum number of turns allowed in the group chat before it halts. Defaults to `None`, implying no upper limit.
*   `selector_prompt` (`str | optional`): The prompt template employed for selecting the next speaker. Available fields for templating include: `{roles}`, `{participants}`, and `{history}`.
    *   `{participants}`: Represents the names of candidate speakers, formatted as `["<name1>", "<name2>", ...] `.
    *   `{roles}`: Presents a newline-separated list of candidate agent names and their descriptions, with each line formatted as: `"<name> : <description>"`.
    *   `{history}`: Contains the conversation history, formatted as double newline-separated blocks of names and message content, with each message structured as: `"<name> : <message content>"`.
*   `allow_repeated_speaker` (`bool | optional`): Determines whether the previous speaker should be included in the list of candidates for selection in the next turn. Defaults to `False`. A warning will be logged if the model nonetheless selects the previous speaker.
*   `max_selector_attempts` (`int | optional`): The maximum number of attempts the model will make to select a speaker. Defaults to `3`. If the model fails to select a speaker after this maximum number of attempts, the previous speaker will be used if available; otherwise, the first participant in the list will be chosen.
*   `selector_func` (`Callable[[Sequence[BaseAgentEvent | BaseChatMessage]], str | None] | Callable[[Sequence[BaseAgentEvent | BaseChatMessage]], Awaitable[str | None]] | optional`): A custom function that accepts the conversation history and returns the name of the next speaker. If provided, this function overrides the model's speaker selection mechanism. If the function returns `None`, the model will then be used for speaker selection.
*   `candidate_func` (`Callable[[Sequence[BaseAgentEvent | BaseChatMessage]], List[str]] | Callable[[Sequence[BaseAgentEvent | BaseChatMessage]], Awaitable[List[str]]] | optional`): A custom function that takes the conversation history and returns a filtered list of candidates for the next speaker selection using the model. If this function returns an empty list or `None`, `SelectorGroupChat` will raise a `ValueError`. This function is only utilized if `selector_func` is not set. The `allow_repeated_speaker` parameter will be ignored if this function is set.
*   `custom_message_types` (`List[type[BaseAgentEvent | BaseChatMessage]] | optional`): A list detailing any custom message types that will be used within the group chat. If agents are configured to produce or utilize custom message types, they must be specified here. Ensure these custom message types are subclasses of `BaseAgentEvent` or `BaseChatMessage`.
*   `emit_team_events` (`bool | optional`): A flag indicating whether team events should be emitted via `BaseGroupChat.run_stream()`. Defaults to `False`.
*   `model_client_streaming` (`bool | optional`): Determines whether streaming should be used for the model client. This feature is particularly useful for reasoning models such as QwQ. Defaults to `False`.
*   `model_context` (`ChatCompletionContext | None | optional`): The model context used for storing and retrieving `LLMMessage` instances. It can be preloaded with initial messages. Messages stored in the model context will be used for speaker selection. Initial messages will be cleared when the team is reset.

**Raises**:
*   `ValueError`: If the number of participants is less than two, or if the selector prompt is invalid.

**Examples**:

*   **A team with multiple participants**:
    ```python
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.ui import Console

    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")

        async def lookup_hotel(location: str) -> str:
            return f"Here are some hotels in {location}: hotel1, hotel2, hotel3."

        async def lookup_flight(origin: str, destination: str) -> str:
            return f"Here are some flights from {origin} to {destination}: flight1, flight2, flight3."

        async def book_trip() -> str:
            return "Your trip is booked!"

        travel_advisor = AssistantAgent(
            "Travel_Advisor",
            model_client,
            tools=[book_trip],
            description="Helps with travel planning.",
        )
        hotel_agent = AssistantAgent(
            "Hotel_Agent",
            model_client,
            tools=[lookup_hotel],
            description="Helps with hotel booking.",
        )
        flight_agent = AssistantAgent(
            "Flight_Agent",
            model_client,
            tools=[lookup_flight],
            description="Helps with flight booking.",
        )
        termination = TextMentionTermination("TERMINATE")
        team = SelectorGroupChat(
            [travel_advisor, hotel_agent, flight_agent],
            model_client=model_client,
            termination_condition=termination,
        )
        await Console(team.run_stream(task="Book a 3-day trip to new york."))

    asyncio.run(main())
    ```

*   **A team with a custom selector function**:
    ```python
    import asyncio
    from typing import Sequence
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.ui import Console
    from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage

    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")

        def check_calculation(x: int, y: int, answer: int) -> str:
            if x + y == answer:
                return "Correct!"
            else:
                return "Incorrect!"

        agent1 = AssistantAgent(
            "Agent1",
            model_client,
            description="For calculation",
            system_message="Calculate the sum of two numbers",
        )
        agent2 = AssistantAgent(
            "Agent2",
            model_client,
            tools=[check_calculation],
            description="For checking calculation",
            system_message="Check the answer and respond with 'Correct!' or 'Incorrect!'",
        )

        def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
            if len(messages) == 1 or messages[-1].to_text() == "Incorrect!":
                return "Agent1"
            if messages[-1].source == "Agent1":
                return "Agent2"
            return None

        termination = TextMentionTermination("Correct!")
        team = SelectorGroupChat(
            [agent1, agent2],
            model_client=model_client,
            selector_func=selector_func,
            termination_condition=termination,
        )
        await Console(team.run_stream(task="What is 1 + 1?"))

    asyncio.run(main())
    ```

*   **A team with custom model context**:
    ```python
    import asyncio
    from autogen_core.model_context import BufferedChatCompletionContext
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.conditions import TextMentionTermination
    from autogen_agentchat.teams import SelectorGroupChat
    from autogen_agentchat.ui import Console

    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
        model_context = BufferedChatCompletionContext(buffer_size=5)

        async def lookup_hotel(location: str) -> str:
            return f"Here are some hotels in {location}: hotel1, hotel2, hotel3."

        async def lookup_flight(origin: str, destination: str) -> str:
            return f"Here are some flights from {origin} to {destination}: flight1, flight2, flight3."

        async def book_trip() -> str:
            return "Your trip is booked!"

        travel_advisor = AssistantAgent(
            "Travel_Advisor",
            model_client,
            tools=[book_trip],
            description="Helps with travel planning.",
        )
        hotel_agent = AssistantAgent(
            "Hotel_Agent",
            model_client,
            tools=[lookup_hotel],
            description="Helps with hotel booking.",
        )
        flight_agent = AssistantAgent(
            "Flight_Agent",
            model_client,
            tools=[lookup_flight],
            description="Helps with flight booking.",
        )
        termination = TextMentionTermination("TERMINATE")
        team = SelectorGroupChat(
            [travel_advisor, hotel_agent, flight_agent],
            model_client=model_client,
            termination_condition=termination,
            model_context=model_context,
        )
        await Console(team.run_stream(task="Book a 3-day trip to new york."))

    asyncio.run(main())
    ```

**Methods:**
*   `*classmethod* _from_config (*config : SelectorGroupChatConfig) → Self`
    *   **Description**: Creates a new instance of the component directly from a configuration object.
    *   **Parameters**:
        *   `config` (`T`): The configuration object.
    *   **Returns**:
        *   `Self`: The newly created instance of the component.

*   `_to_config () → SelectorGroupChatConfig`
    *   **Description**: Dumps the configuration necessary to instantiate a new component instance matching the current instance's configuration.
    *   **Returns**:
        *   `T`: The configuration of the component.

**Class Variables:**
*   `component_config_schema`: Alias of `SelectorGroupChatConfig`.
*   `component_provider_override: ClassVar[str| None] = 'autogen_agentchat.teams.SelectorGroupChat'`
    *   Overrides the provider string for the component, preventing internal module names from becoming part of the module name.

---

#### `*class* Swarm (participants : List[ChatAgent], termination_condition : TerminationCondition| None = None, max_turns : int| None = None, runtime : AgentRuntime| None = None, custom_message_types : List[type[BaseAgentEvent| BaseChatMessage]] | None = None, emit_team_events : bool = False)[source]`
Bases: `BaseGroupChat`, `Component[SwarmConfig]`

This group chat team operates by selecting the next speaker based exclusively on a handoff message. The initial speaker is designated as the first participant in the provided list. Subsequently, the next speaker is chosen based on the `HandoffMessage` sent by the current speaker. If no handoff message is transmitted, the current speaker retains their turn.

**Parameters**:
*   `participants` (`List[ChatAgent]`): The agents engaged in the group chat. The first agent in this list serves as the initial speaker.
*   `termination_condition` (`TerminationCondition | optional`): The condition that dictates the group chat's termination. Defaults to `None`. Without a specified termination condition, the group chat will continue indefinitely.
*   `max_turns` (`int | optional`): The maximum number of turns allowed in the group chat before it halts. Defaults to `None`, implying no upper limit.
*   `custom_message_types` (`List[type[BaseAgentEvent | BaseChatMessage]] | optional`): A list detailing any custom message types that will be used within the group chat. If agents are configured to produce or utilize custom message types, they must be specified here. Ensure these custom message types are subclasses of `BaseAgentEvent` or `BaseChatMessage`.
*   `emit_team_events` (`bool | optional`): A flag indicating whether team events should be emitted via `BaseGroupChat.run_stream()`. Defaults to `False`.

**Examples**:

*   **Basic example**:
    ```python
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import Swarm
    from autogen_agentchat.conditions import MaxMessageTermination

    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
        agent1 = AssistantAgent(
            "Alice",
            model_client=model_client,
            handoffs=["Bob"],
            system_message="You are Alice and you only answer questions about yourself.",
        )
        agent2 = AssistantAgent(
            "Bob",
            model_client=model_client,
            system_message="You are Bob and your birthday is on 1st January."
        )
        termination = MaxMessageTermination(3)
        team = Swarm([agent1, agent2], termination_condition=termination)
        stream = team.run_stream(task="What is bob's birthday?")
        async for message in stream:
            print(message)

    asyncio.run(main())
    ```

*   **Using the `HandoffTermination` for human-in-the-loop handoff**:
    ```python
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import Swarm
    from autogen_agentchat.conditions import HandoffTermination, MaxMessageTermination
    from autogen_agentchat.ui import Console
    from autogen_agentchat.messages import HandoffMessage

    async def main() -> None:
        model_client = OpenAIChatCompletionClient(model="gpt-4o")
        agent = AssistantAgent(
            "Alice",
            model_client=model_client,
            handoffs=["user"],
            system_message="You are Alice and you only answer questions about yourself, ask the user for help if needed.",
        )
        termination = HandoffTermination(target="user") | MaxMessageTermination(3)
        team = Swarm([agent], termination_condition=termination)

        # Start the conversation.
        await Console(team.run_stream(task="What is bob's birthday?"))

        # Resume with user feedback.
        await Console(
            team.run_stream(
                task=HandoffMessage(source="user", target="Alice", content="Bob's birthday is on 1st January.")
            )
        )

    asyncio.run(main())
    ```

**Methods:**
*   `*classmethod* _from_config (*config : SwarmConfig) → Swarm`
    *   **Description**: Creates a new instance of the component directly from a configuration object.
    *   **Parameters**:
        *   `config` (`T`): The configuration object.
    *   **Returns**:
        *   `Self`: The newly created instance of the component.

*   `_to_config () → SwarmConfig`
    *   **Description**: Dumps the configuration necessary to instantiate a new component instance matching the current instance's configuration.
    *   **Returns**:
        *   `T`: The configuration of the component.

**Class Variables:**
*   `component_config_schema`: Alias of `SwarmConfig`.
*   `component_provider_override: ClassVar[str| None] = 'autogen_agentchat.teams.Swarm'`
    *   Overrides the provider string for the component, preventing internal module names from becoming part of the module name.