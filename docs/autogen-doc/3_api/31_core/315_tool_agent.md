# autogen_core.tool_agent

*exception* `InvalidToolArgumentsException` (call_id : `str`, content : `str`, name : `str`)[source]#
Bases: `ToolException`

*class* `ToolAgent` (description : `str`, tools : `List`[`Tool` `*`])[source]#
Bases: `RoutedAgent`
A tool agent accepts direct messages of the type `FunctionCall`, executes the requested tool with the provided arguments, and returns the result as `FunctionExecutionResult` messages.

Parameters :
**description** (`str`) – The description of the agent.
**tools** (`List`[`Tool`]) – The list of tools that the agent can execute.

*async* `handle_function_call` (message : `FunctionCall`, ctx : `MessageContext`) `→` `FunctionExecutionResult`[source]#
Handles a `FunctionCall` message by executing the requested tool with the provided arguments.

Parameters :
**message** (`FunctionCall`) – The function call message.
**cancellation_token** (`CancellationToken`) – The cancellation token.

Returns :
**FunctionExecutionResult** – The result of the function execution.

Raises :
**ToolNotFoundException** – If the tool is not found.
**InvalidToolArgumentsException** – If the tool arguments are invalid.
**ToolExecutionException** – If the tool execution fails.

*property* `tools`: `List`[`Tool` `*`]#

*exception* `ToolException` (call_id : `str`, content : `str`, name : `str`)[source]#
Bases: `BaseException`
`call_id`: `str`#
`content`: `str`#
`name`: `str`#

*exception* `ToolExecutionException` (call_id : `str`, content : `str`, name : `str`)[source]#
Bases: `ToolException`

*exception* `ToolNotFoundException` (call_id : `str`, content : `str`, name : `str`)[source]#
Bases: `ToolException`

*async* `tool_agent_caller_loop` (caller : `BaseAgent`|`AgentRuntime`, tool_agent_id : `AgentId`, model_client : `ChatCompletionClient`, input_messages : `List`[`Annotated`[`SystemMessage`|`UserMessage`|`AssistantMessage`|`FunctionExecutionResultMessage` `*`, `FieldInfo` (`annotation` = `NoneType`, `required` = `True`, `discriminator` = `'type'`) `]]*`, tool_schema : `List`[`ToolSchema`] `|` `List`[`Tool` `*`], cancellation_token : `CancellationToken`|`None` `= `None`*, caller_source : `str` `= `'assistant'`*) `→` `List`[`Annotated`[`SystemMessage`|`UserMessage`|`AssistantMessage`|`FunctionExecutionResultMessage`, `FieldInfo` (`annotation` = `NoneType`, `required` = `True`, `discriminator` = `'type'`) `]]`[source]#
Start a caller loop for a tool agent. This function sends messages to the tool agent and the model client in an alternating fashion until the model client stops generating tool calls.

Parameters :
**tool_agent_id** (`AgentId`) – The Agent ID of the tool agent.
**input_messages** (`List`[`LLMMessage`]) – The list of input messages.
**model_client** (`ChatCompletionClient`) – The model client to use for the model API.
**tool_schema** (`List`[`Tool`|`ToolSchema`]) – The list of tools that the model can use.

Returns :
**List[LLMMessage]** – The list of output messages created in the caller loop.

