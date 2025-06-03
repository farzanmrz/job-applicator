### Installation [#](https://microsoft.github.io/autogen/docs/installation/#installation)

#### Create a Virtual Environment (optional) [#](https://microsoft.github.io/autogen/docs/installation/#create-a-virtual-environment-optional)
When installing AgentChat locally, it is highly recommended to utilize a virtual environment for the installation process. This practice is crucial as it ensures that the dependencies required for AgentChat are isolated from the rest of your system, preventing potential conflicts or pollution of your global Python environment.

To create and activate a virtual environment, use the following commands:
```bash
# On Windows, change `python3` to `python` (if `python` is Python 3).
python3 -m venv .venv
# On Windows, change `bin` to `scripts`.
source .venv/bin/activate
```
To deactivate the virtual environment later, simply execute the `deactivate` command:
```bash
deactivate
```
Alternatively, if you prefer using Conda, first ensure that Conda is installed on your system. Once Conda is available, you can create and activate a new environment for AutoGen with these commands:
```bash
conda create -n autogen python=3.12
conda activate autogen
```
To deactivate the Conda environment later, use the `conda deactivate` command:
```bash
conda deactivate
```

#### Install Using pip [#](https://microsoft.github.io/autogen/docs/installation/#install-using-pip)
To install the `autogen-agentchat` package, use pip. This method is straightforward and ensures you get the necessary components:
```bash
pip install -U "autogen-agentchat"
```
> Note: Python 3.10 or later is a prerequisite for installing and running AutoGen.

#### Install OpenAI for Model Client [#](https://microsoft.github.io/autogen/docs/installation/#install-openai-for-model-client)
To leverage the capabilities of OpenAI and Azure OpenAI models within AgentChat, specific extensions are required. Install them using pip as follows:
```bash
pip install "autogen-ext[openai]"
```
Furthermore, if your setup involves using Azure OpenAI with AAD (Azure Active Directory) authentication, an additional extension is necessary to facilitate secure access:
```bash
pip install "autogen-ext[azure]"
```

---

### Quickstart [#](https://microsoft.github.io/autogen/docs/quickstart/#quickstart)
Via AgentChat, the development of applications is streamlined through the utilization of preset agents. To illustrate this capability, the following example details the creation of a single agent specifically designed to interact with and use tools.

Initially, it is necessary to install both the AgentChat and Extension packages. This can be accomplished with a single pip command, ensuring all required dependencies are met:
```bash
pip install -U "autogen-agentchat" "autogen-ext[openai,azure]"
```
While this demonstration employs an OpenAI model, the `model_client` can be readily updated to incorporate other models or model client classes as desired, providing flexibility in model selection. For instructions on integrating Azure OpenAI models with AAD authentication, refer to the dedicated documentation. Details on using other models can be found in the "Models" section.

The following Python code demonstrates a basic implementation of an `AssistantAgent` capable of using a tool. It defines a model client, a simple weather function, and configures the agent to use this tool while streaming outputs to the console:

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Define a model client. You can use other model client that implements
# the `ChatCompletionClient` interface.
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

# Define a simple function tool that the agent can use.
# For this example, we use a fake weather tool for demonstration purposes.
async def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."

# Define an AssistantAgent with the model, tool, system message, and reflection enabled.
# The system message instructs the agent via natural language.
agent = AssistantAgent(
    name="weather_agent",
    model_client=model_client,
    tools=[get_weather],
    system_message="You are a helpful assistant.",
    reflect_on_tool_use=True,
    model_client_stream=True,  # Enable streaming tokens from the model client.
)

# Run the agent and stream the messages to the console.
async def main() -> None:
    await Console(agent.run_stream(task="What is the weather in New York?"))
    # Close the connection to the model client.
    await model_client.close()

# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
await main()
```

The execution of the above code demonstrates the agent's interaction, tool invocation, and subsequent output:
```
---------- user ----------
What is the weather in New York?
---------- weather_agent ----------
[FunctionCall(id='call_bE5CYAwB7OlOdNAyPjwOkej1', arguments='{"city":"New York"}', name='get_weather')]
---------- weather_agent ----------
[FunctionExecutionResult(content='The weather in New York is 73 degrees and Sunny.', call_id='call_bE5CYAwB7OlOdNAyPjwOkej1', is_error=False)]
---------- weather_agent ----------
The current weather in New York is 73 degrees and sunny.
```

#### What’s Next? [#](https://microsoft.github.io/autogen/docs/quickstart/#what-s-next)
Having acquired a foundational understanding of how to implement and utilize a single agent, it is highly recommended to proceed with the comprehensive tutorial. This tutorial provides an in-depth walkthrough of AgentChat's additional features and capabilities, expanding on this basic introduction.