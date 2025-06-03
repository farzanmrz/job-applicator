### autogen_agentchat.tools#

*class* **AgentTool** (agent : BaseChatAgent)[source]#
Bases: TaskRunnerTool , Component[ AgentToolConfig ]

Tool that can be used to run a task using an agent.
The tool returns the result of the task execution as a TaskResult object.

Parameters :
**agent** (*BaseChatAgent*) – The agent to be used for running the task.

Example
```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.tools import AgentTool
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4")
    writer = AssistantAgent(
        name="writer",
        description="A writer agent for generating text.",
        model_client=model_client,
        system_message="Write well.",
    )
    writer_tool = AgentTool(agent=writer)
    assistant = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[writer_tool],
        system_message="You are a helpful assistant.",
    )
    await Console(assistant.run_stream(task="Write a poem about the sea."))

asyncio.run(main())
```

*classmethod* **_from_config** (*config : AgentToolConfig*) → Self[source]#
Create a new instance of the component from a configuration object.

Parameters :
**config** (*T*) – The configuration object.

Returns :
**Self** – The new instance of the component.

**_to_config** ( ) → AgentToolConfig[source]#
Dump the configuration that would be requisite to create a new instance of a component matching the configuration of this instance.

Returns :
**T** – The configuration of the component.

**component_config_schema**#alias of AgentToolConfig

**component_provider_override**: ClassVar [str| None ] *= 'autogen_agentchat.tools.AgentTool'* #
Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.

*class* **TeamTool** (team : BaseGroupChat, name : str, description : str)[source]#
Bases: TaskRunnerTool , Component[ TeamToolConfig ]

Tool that can be used to run a task.
The tool returns the result of the task execution as a TaskResult object.

Parameters :
**team** (*BaseGroupChat*) – The team to be used for running the task.
**name** (*str*) – The name of the tool.
**description** (*str*) – The description of the tool.

*classmethod* **_from_config** (*config : TeamToolConfig*) → Self[source]#
Create a new instance of the component from a configuration object.

Parameters :
**config** (*T*) – The configuration object.

Returns :
**Self** – The new instance of the component.

**_to_config** ( ) → TeamToolConfig[source]#
Dump the configuration that would be requisite to create a new instance of a component matching the configuration of this instance.

Returns :
**T** – The configuration of the component.

**component_config_schema**#alias of TeamToolConfig

**component_provider_override**: ClassVar [str| None ] *= 'autogen_agentchat.tools.TeamTool'* #
Override the provider string for the component. This should be used to prevent internal module names being a part of the module name.