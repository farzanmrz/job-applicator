# Agents
Smolagents is an experimental API which is subject to change at any time. Results returned by the agents can vary as the APIs or underlying models are prone to change.

To learn more about agents and tools make sure to read the [introductory guide](../index). This page contains the API docs for the underlying classes.

[](#agents)Agents
-----------------

Our agents inherit from [MultiStepAgent](about:/docs/smolagents/v1.17.0/en/reference/agents#smolagents.MultiStepAgent), which means they can act in multiple steps, each step consisting of one thought, then one tool call and execution. Read more in [this conceptual guide](../conceptual_guides/react).

We provide two types of agents, based on the main `Agent` class.

*   [CodeAgent](about:/docs/smolagents/v1.17.0/en/reference/agents#smolagents.CodeAgent) is the default agent, it writes its tool calls in Python code.
*   [ToolCallingAgent](about:/docs/smolagents/v1.17.0/en/reference/agents#smolagents.ToolCallingAgent) writes its tool calls in JSON.

Both require arguments `model` and list of tools `tools` at initialization.

### [](#smolagents.MultiStepAgent)Classes of agents

### class smolagents.MultiStepAgent [< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L205)

[](#smolagents.MultiStepAgent)

( **tools**: `list`, **model**: `Model`, **prompt\_templates**: `smolagents.agents.PromptTemplates | None` = None, **max\_steps**: `int` = 20, **add\_base\_tools**: `bool` = False, **verbosity\_level**: `LogLevel` = <LogLevel.INFO: 1>, **grammar**: `dict\[str, str\] | None` = None, **managed\_agents**: `list | None` = None, **step\_callbacks**: `list\[collections.abc.Callable\] | None` = None, **planning\_interval**: `int | None` = None, **name**: `str | None` = None, **description**: `str | None` = None, **provide\_run\_summary**: `bool` = False, **final\_answer\_checks**: `list\[collections.abc.Callable\] | None` = None, **return\_full\_result**: `bool` = False, **logger**: `smolagents.monitoring.AgentLogger | None` = None )

Parameters

*   [](#smolagents.MultiStepAgent.tools)**tools** (`list[Tool]`) — [Tool](about:/docs/smolagents/v1.17.0/en/reference/tools#smolagents.Tool)s that the agent can use.
*   [](#smolagents.MultiStepAgent.model)**model** (`Callable[[list[dict[str, str]]], ChatMessage]`) — Model that will generate the agent’s actions.
*   [](#smolagents.MultiStepAgent.prompt_templates)**prompt\_templates** ([PromptTemplates](about:/docs/smolagents/v1.17.0/en/reference/agents#smolagents.PromptTemplates), _optional_) — Prompt templates.
*   [](#smolagents.MultiStepAgent.max_steps)**max\_steps** (`int`, default `20`) — Maximum number of steps the agent can take to solve the task.
*   [](#smolagents.MultiStepAgent.add_base_tools)**add\_base\_tools** (`bool`, default `False`) — Whether to add the base tools to the agent’s tools.
*   [](#smolagents.MultiStepAgent.verbosity_level)**verbosity\_level** (`LogLevel`, default `LogLevel.INFO`) — Level of verbosity of the agent’s logs.
*   [](#smolagents.MultiStepAgent.grammar)**grammar** (`dict[str, str]`, _optional_) — Grammar used to parse the LLM output.
    
    Deprecated in 1.17.0
    
    Parameter \`grammar\` is deprecated and will be removed in version 1.20.
    
*   [](#smolagents.MultiStepAgent.managed_agents)**managed\_agents** (`list`, _optional_) — Managed agents that the agent can call.
*   [](#smolagents.MultiStepAgent.step_callbacks)**step\_callbacks** (`list[Callable]`, _optional_) — Callbacks that will be called at each step.
*   [](#smolagents.MultiStepAgent.planning_interval)**planning\_interval** (`int`, _optional_) — Interval at which the agent will run a planning step.
*   [](#smolagents.MultiStepAgent.name)**name** (`str`, _optional_) — Necessary for a managed agent only - the name by which this agent can be called.
*   [](#smolagents.MultiStepAgent.description)**description** (`str`, _optional_) — Necessary for a managed agent only - the description of this agent.
*   [](#smolagents.MultiStepAgent.provide_run_summary)**provide\_run\_summary** (`bool`, _optional_) — Whether to provide a run summary when called as a managed agent.
*   [](#smolagents.MultiStepAgent.final_answer_checks)**final\_answer\_checks** (`list`, _optional_) — List of Callables to run before returning a final answer for checking validity.

Agent class that solves the given task step by step, using the ReAct framework: While the objective is not reached, the agent will perform a cycle of action (given by the LLM) and observation (obtained from the environment).

( **model\_output**: `str`, **split\_token**: `str` )

Parameters

*   [](#smolagents.MultiStepAgent.extract_action.model_output)**model\_output** (`str`) — Output of the LLM
*   [](#smolagents.MultiStepAgent.extract_action.split_token)**split\_token** (`str`) — Separator for the action. Should match the example in the system prompt.

Parse action from the LLM output

#### from\_dict

[](#smolagents.MultiStepAgent.from_dict)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L950)

( **agent\_dict**: `dict`, **\*\*kwargs** ) → `MultiStepAgent`

Parameters

*   [](#smolagents.MultiStepAgent.from_dict.agent_dict)**agent\_dict** (`dict[str, Any]`) — Dictionary representation of the agent.
*   [](#smolagents.MultiStepAgent.from_dict.*kwargs)\***\*kwargs** — Additional keyword arguments that will override agent\_dict values.

Instance of the agent class.

Create agent from a dictionary representation.

#### from\_folder

[](#smolagents.MultiStepAgent.from_folder)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L1047)

( folder: str | pathlib.Path \*\*kwargs )

Parameters

*   [](#smolagents.MultiStepAgent.from_folder.folder)**folder** (`str` or `Path`) — The folder where the agent is saved.
*   [](#smolagents.MultiStepAgent.from_folder.*kwargs)\***\*kwargs** — Additional keyword arguments that will be passed to the agent’s init.

Loads an agent from a local folder.

#### from\_hub

[](#smolagents.MultiStepAgent.from_hub)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L993)

( repo\_id: str token: str | None = None trust\_remote\_code: bool = False \*\*kwargs )

Parameters

*   [](#smolagents.MultiStepAgent.from_hub.repo_id)**repo\_id** (`str`) — The name of the repo on the Hub where your tool is defined.
*   [](#smolagents.MultiStepAgent.from_hub.token)**token** (`str`, _optional_) — The token to identify you on hf.co. If unset, will use the token generated when running `huggingface-cli login` (stored in `~/.huggingface`).
*   [](#smolagents.MultiStepAgent.from_hub.trust_remote_code\(bool,)**trust\_remote\_code(`bool`,** _optional_, defaults to False) — This flags marks that you understand the risk of running remote code and that you trust this tool. If not setting this to True, loading the tool from Hub will fail.
*   [](#smolagents.MultiStepAgent.from_hub.kwargs)**kwargs** (additional keyword arguments, _optional_) — Additional keyword arguments that will be split in two: all arguments relevant to the Hub (such as `cache_dir`, `revision`, `subfolder`) will be used when downloading the files for your agent, and the others will be passed along to its init.

Loads an agent defined on the Hub.

Loading a tool from the Hub means that you’ll download the tool and execute it locally. ALWAYS inspect the tool you’re downloading before loading it within your runtime, as you would do when installing a package using pip/npm/apt.

To be implemented in child classes

Interrupts the agent execution.

#### provide\_final\_answer

[](#smolagents.MultiStepAgent.provide_final_answer)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L709)

( task: str images: list\['PIL.Image.Image'\] | None = None ) → `str`

Parameters

*   [](#smolagents.MultiStepAgent.provide_final_answer.task)**task** (`str`) — Task to perform.
*   [](#smolagents.MultiStepAgent.provide_final_answer.images)**images** (`list[PIL.Image.Image]`, _optional_) — Image(s) objects.

Final answer to the task.

Provide the final answer to the task, based on the logs of the agent’s interactions.

#### push\_to\_hub

[](#smolagents.MultiStepAgent.push_to_hub)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L1079)

( repo\_id: str commit\_message: str = 'Upload agent' private: bool | None = None token: bool | str | None = None create\_pr: bool = False )

Parameters

*   [](#smolagents.MultiStepAgent.push_to_hub.repo_id)**repo\_id** (`str`) — The name of the repository you want to push to. It should contain your organization name when pushing to a given organization.
*   [](#smolagents.MultiStepAgent.push_to_hub.commit_message)**commit\_message** (`str`, _optional_, defaults to `"Upload agent"`) — Message to commit while pushing.
*   [](#smolagents.MultiStepAgent.push_to_hub.private)**private** (`bool`, _optional_, defaults to `None`) — Whether to make the repo private. If `None`, the repo will be public unless the organization’s default is private. This value is ignored if the repo already exists.
*   [](#smolagents.MultiStepAgent.push_to_hub.token)**token** (`bool` or `str`, _optional_) — The token to use as HTTP bearer authorization for remote files. If unset, will use the token generated when running `huggingface-cli login` (stored in `~/.huggingface`).
*   [](#smolagents.MultiStepAgent.push_to_hub.create_pr)**create\_pr** (`bool`, _optional_, defaults to `False`) — Whether to create a PR with the uploaded files or directly commit.

Upload the agent to the Hub.

#### replay

[](#smolagents.MultiStepAgent.replay)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L757)

( detailed: bool = False )

Parameters

*   [](#smolagents.MultiStepAgent.replay.detailed)**detailed** (bool, optional) — If True, also displays the memory at each step. Defaults to False. Careful: will increase log length exponentially. Use only for debugging.

Prints a pretty replay of the agent’s steps.

#### run

[](#smolagents.MultiStepAgent.run)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L337)

( task: str stream: bool = False reset: bool = True images: list\['PIL.Image.Image'\] | None = None additional\_args: dict | None = None max\_steps: int | None = None )

Parameters

*   [](#smolagents.MultiStepAgent.run.task)**task** (`str`) — Task to perform.
*   [](#smolagents.MultiStepAgent.run.stream)**stream** (`bool`) — Whether to run in streaming mode. If `True`, returns a generator that yields each step as it is executed. You must iterate over this generator to process the individual steps (e.g., using a for loop or `next()`). If `False`, executes all steps internally and returns only the final answer after completion.
*   [](#smolagents.MultiStepAgent.run.reset)**reset** (`bool`) — Whether to reset the conversation or keep it going from previous run.
*   [](#smolagents.MultiStepAgent.run.images)**images** (`list[PIL.Image.Image]`, _optional_) — Image(s) objects.
*   [](#smolagents.MultiStepAgent.run.additional_args)**additional\_args** (`dict`, _optional_) — Any other variables that you want to pass to the agent run, for instance images or dataframes. Give them clear names!
*   [](#smolagents.MultiStepAgent.run.max_steps)**max\_steps** (`int`, _optional_) — Maximum number of steps the agent can take to solve the task. if not provided, will use the agent’s default value.

Run the agent for the given task.

Example:

```
from smolagents import CodeAgent
agent = CodeAgent(tools=[])
agent.run("What is the result of 2 power 3.7384?")
```


#### save

[](#smolagents.MultiStepAgent.save)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L790)

( output\_dir: str | pathlib.Path relative\_path: str | None = None )

Parameters

*   [](#smolagents.MultiStepAgent.save.output_dir)**output\_dir** (`str` or `Path`) — The folder in which you want to save your agent.

Saves the relevant code files for your agent. This will copy the code of your agent in `output_dir` as well as autogenerate:

*   a `tools` folder containing the logic for each of the tools under `tools/{tool_name}.py`.
*   a `managed_agents` folder containing the logic for each of the managed agents.
*   an `agent.json` file containing a dictionary representing your agent.
*   a `prompt.yaml` file containing the prompt templates used by your agent.
*   an `app.py` file providing a UI for your agent when it is exported to a Space with `agent.push_to_hub()`
*   a `requirements.txt` containing the names of the modules used by your tool (as detected when inspecting its code)

Perform one step in the ReAct framework: the agent thinks, acts, and observes the result. Returns either None if the step is not final, or the final answer.

#### to\_dict

[](#smolagents.MultiStepAgent.to_dict)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L909)

( ) → `dict`

Dictionary representation of the agent.

Convert the agent to a dictionary representation.

Creates a rich tree visualization of the agent’s structure.

#### write\_memory\_to\_messages

[](#smolagents.MultiStepAgent.write_memory_to_messages)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L660)

( summary\_mode: bool | None = False )

Reads past llm\_outputs, actions, and observations or errors from the memory into a series of messages that can be used as input to the LLM. Adds a number of keywords (such as PLAN, error, etc) to help the LLM.

### class smolagents.CodeAgent [< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L1345)

[](#smolagents.CodeAgent)

( **tools**: `list`, **model**: `Model`, **prompt\_templates**: `smolagents.agents.PromptTemplates | None` = None, **additional\_authorized\_imports**: `list\[str\] | None` = None, **planning\_interval**: `int | None` = None, **executor\_type**: `str | None` = 'local', **executor\_kwargs**: `dict\[str, typing.Any\] | None` = None, **max\_print\_outputs\_length**: `int | None` = None, **stream\_outputs**: `bool` = False, **use\_structured\_outputs\_internally**: `bool` = False, **grammar**: `dict\[str, str\] | None` = None, **\*\*kwargs** )

Parameters

*   [](#smolagents.CodeAgent.tools)**tools** (`list[Tool]`) — [Tool](about:/docs/smolagents/v1.17.0/en/reference/tools#smolagents.Tool)s that the agent can use.
*   [](#smolagents.CodeAgent.model)**model** (`Model`) — Model that will generate the agent’s actions.
*   [](#smolagents.CodeAgent.prompt_templates)**prompt\_templates** ([PromptTemplates](about:/docs/smolagents/v1.17.0/en/reference/agents#smolagents.PromptTemplates), _optional_) — Prompt templates.
*   [](#smolagents.CodeAgent.additional_authorized_imports)**additional\_authorized\_imports** (`list[str]`, _optional_) — Additional authorized imports for the agent.
*   [](#smolagents.CodeAgent.planning_interval)**planning\_interval** (`int`, _optional_) — Interval at which the agent will run a planning step.
*   [](#smolagents.CodeAgent.executor_type)**executor\_type** (`str`, default `"local"`) — Which executor type to use between `"local"`, `"e2b"`, or `"docker"`.
*   [](#smolagents.CodeAgent.executor_kwargs)**executor\_kwargs** (`dict`, _optional_) — Additional arguments to pass to initialize the executor.
*   [](#smolagents.CodeAgent.max_print_outputs_length)**max\_print\_outputs\_length** (`int`, _optional_) — Maximum length of the print outputs.
*   [](#smolagents.CodeAgent.stream_outputs)**stream\_outputs** (`bool`, _optional_, default `False`) — Whether to stream outputs during execution.
*   [](#smolagents.CodeAgent.use_structured_outputs_internally)**use\_structured\_outputs\_internally** (`bool`, default `False`) — Whether to use structured generation at each action step: improves performance for many models.
    
    Added in 1.17.0
    
*   [](#smolagents.CodeAgent.grammar)**grammar** (`dict[str, str]`, _optional_) — Grammar used to parse the LLM output.
    
    Deprecated in 1.17.0
    
    Parameter \`grammar\` is deprecated and will be removed in version 1.20.
    
*   [](#smolagents.CodeAgent.*kwargs)\***\*kwargs** — Additional keyword arguments.

In this agent, the tool calls will be formulated by the LLM in code format, then parsed and executed.

#### from\_dict

[](#smolagents.CodeAgent.from_dict)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L1597)

( agent\_dict: dict \*\*kwargs ) → `CodeAgent`

Parameters

*   [](#smolagents.CodeAgent.from_dict.agent_dict)**agent\_dict** (`dict[str, Any]`) — Dictionary representation of the agent.
*   [](#smolagents.CodeAgent.from_dict.*kwargs)\***\*kwargs** — Additional keyword arguments that will override agent\_dict values.

Instance of the CodeAgent class.

Create CodeAgent from a dictionary representation.

### class smolagents.ToolCallingAgent [< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L1134)

[](#smolagents.ToolCallingAgent)

( **tools**: `list`, **model**: `Callable`, **prompt\_templates**: `smolagents.agents.PromptTemplates | None` = None, **planning\_interval**: `int | None` = None, **\*\*kwargs** )

Parameters

*   [](#smolagents.ToolCallingAgent.tools)**tools** (`list[Tool]`) — [Tool](about:/docs/smolagents/v1.17.0/en/reference/tools#smolagents.Tool)s that the agent can use.
*   [](#smolagents.ToolCallingAgent.model)**model** (`Callable[[list[dict[str, str]]], ChatMessage]`) — Model that will generate the agent’s actions.
*   [](#smolagents.ToolCallingAgent.prompt_templates)**prompt\_templates** ([PromptTemplates](about:/docs/smolagents/v1.17.0/en/reference/agents#smolagents.PromptTemplates), _optional_) — Prompt templates.
*   [](#smolagents.ToolCallingAgent.planning_interval)**planning\_interval** (`int`, _optional_) — Interval at which the agent will run a planning step.
*   [](#smolagents.ToolCallingAgent.*kwargs)\***\*kwargs** — Additional keyword arguments.

This agent uses JSON-like tool calls, using method `model.get_tool_call` to leverage the LLM engine’s tool calling capabilities.

#### execute\_tool\_call

[](#smolagents.ToolCallingAgent.execute_tool_call)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L1280)

( tool\_name: str arguments: dict\[str, str\] | str )

Parameters

*   [](#smolagents.ToolCallingAgent.execute_tool_call.tool_name)**tool\_name** (`str`) — Name of the tool or managed agent to execute.
*   [](#smolagents.ToolCallingAgent.execute_tool_call.arguments)**arguments** (dict\[str, str\] | str) — Arguments passed to the tool call.

Execute a tool or managed agent with the provided arguments.

The arguments are replaced with the actual values from the state if they refer to state variables.

### [](#managedagent)ManagedAgent

_This class is deprecated since 1.8.0: now you simply need to pass attributes `name` and `description` to a normal agent to make it callable by a manager agent._

### [](#smolagents.stream_to_gradio)stream\_to\_gradio

#### smolagents.stream\_to\_gradio

[](#smolagents.stream_to_gradio)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/gradio_ui.py#L244)

( agent task: str task\_images: list | None = None reset\_agent\_memory: bool = False additional\_args: dict | None = None )

Runs an agent with the given task and streams the messages from the agent as gradio ChatMessages.

### [](#smolagents.GradioUI)GradioUI

You must have `gradio` installed to use the UI. Please run `pip install smolagents[gradio]` if it’s not the case.

### class smolagents.GradioUI

[](#smolagents.GradioUI)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/gradio_ui.py#L274)

( agent: MultiStepAgent file\_upload\_folder: str | None = None )

A one-line interface to launch your agent in Gradio

#### upload\_file

[](#smolagents.GradioUI.upload_file)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/gradio_ui.py#L318)

( file file\_uploads\_log allowed\_file\_types = None )

Handle file uploads, default allowed types are .pdf, .docx, and .txt

[](#smolagents.PromptTemplates)Prompts
--------------------------------------

Prompt templates for the agent.

### class smolagents.PlanningPromptTemplate

[](#smolagents.PlanningPromptTemplate)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L116)

( )

Parameters

*   [](#smolagents.PlanningPromptTemplate.plan)**plan** (`str`) — Initial plan prompt.
*   [](#smolagents.PlanningPromptTemplate.update_plan_pre_messages)**update\_plan\_pre\_messages** (`str`) — Update plan pre-messages prompt.
*   [](#smolagents.PlanningPromptTemplate.update_plan_post_messages)**update\_plan\_post\_messages** (`str`) — Update plan post-messages prompt.

Prompt templates for the planning step.

### class smolagents.ManagedAgentPromptTemplate

[](#smolagents.ManagedAgentPromptTemplate)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L131)

( )

Parameters

*   [](#smolagents.ManagedAgentPromptTemplate.task)**task** (`str`) — Task prompt.
*   [](#smolagents.ManagedAgentPromptTemplate.report)**report** (`str`) — Report prompt.

Prompt templates for the managed agent.

### class smolagents.FinalAnswerPromptTemplate

[](#smolagents.FinalAnswerPromptTemplate)
[< source \>](https://github.com/huggingface/smolagents/blob/v1.17.0/src/smolagents/agents.py#L144)

( )

Parameters

*   [](#smolagents.FinalAnswerPromptTemplate.pre_messages)**pre\_messages** (`str`) — Pre-messages prompt.
*   [](#smolagents.FinalAnswerPromptTemplate.post_messages)**post\_messages** (`str`) — Post-messages prompt.

Prompt templates for the final answer.

[< \> Update on GitHub](https://github.com/huggingface/smolagents/blob/main/docs/source/en/reference/agents.mdx)
