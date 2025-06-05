### Magentic-One#

Magentic-One is a generalist multi-agent system designed for solving open-ended web and file-based tasks across a variety of domains. It signifies a substantial advancement for multi-agent systems, demonstrating competitive performance on numerous agentic benchmarks. For complete details regarding its performance, a technical report is available.

Initially released in November 2024, Magentic-One was implemented directly on the `autogen-core` library. However, it has since been ported to utilize `autogen-agentchat`, which provides a more modular and user-friendly interface.

To achieve this, the Magentic-One orchestrator, `MagenticOneGroupChat`, now functions simply as an `AgentChat` team, fully supporting all standard `AgentChat` agents and features. Correspondingly, Magentic-One’s `MultimodalWebSurfer`, `FileSurfer`, and `MagenticOneCoderAgent` agents are now broadly accessible as `AgentChat` agents, enabling their use in any `AgentChat` workflows.

Additionally, a helper class named `MagenticOne` bundles all these components together, replicating its configuration as presented in the original paper with minimal setup. Further information about Magentic-One can be found in its blog post and technical report.

### Example

An illustrative example, depicted in an accompanying figure (not provided in text source), shows the Magentic-One multi-agent team successfully completing a complex task from the GAIA benchmark. Magentic-One’s Orchestrator agent is responsible for creating a plan, delegating tasks to other agents, and meticulously tracking progress toward the goal, dynamically revising the plan as necessary. The Orchestrator possesses the capability to delegate tasks to various specialized agents: a `FileSurfer` agent for reading and handling files, a `WebSurfer` agent for operating a web browser, or a `Coder` or `Computer Terminal` agent for writing or executing code, respectively.

> **Caution**
> Using Magentic-One involves interacting with a digital world designed for humans, which inherently carries risks. To minimize these risks, the following precautions should be considered:
> *   **Use Containers**: Run all tasks within Docker containers to isolate the agents and prevent direct system attacks.
> *   **Virtual Environment**: Employ a virtual environment to execute the agents, thereby preventing them from accessing sensitive data.
> *   **Monitor Logs**: Closely monitor logs during and after execution to detect and mitigate any risky behavior.
> *   **Human Oversight**: Run examples with a human in the loop to supervise the agents and prevent unintended consequences.
> *   **Limit Access**: Restrict the agents’ access to the internet and other resources to prevent unauthorized actions.
> *   **Safeguard Data**: Ensure that the agents do not have access to sensitive data or resources that could be compromised. It is crucial not to share sensitive information with the agents. Be aware that agents may occasionally attempt risky actions, such as recruiting humans for assistance or accepting cookie agreements without direct human involvement. Always ensure agents are monitored and operate within a controlled environment to prevent unintended consequences. Moreover, it is important to be cautious that Magentic-One may be susceptible to prompt injection attacks originating from webpages.

### Getting started#

To begin using Magentic-One, install the required packages:

```bash
pip install "autogen-agentchat" "autogen-ext[magentic-one,openai]"
# If using the MultimodalWebSurfer, you also need to install playwright dependencies:
playwright install --with-deps chromium
```


If you have not already done so, it is recommended to go through the `AgentChat` tutorial to become familiar with its core concepts.

Subsequently, you can swap out a `autogen_agentchat.teams.SelectorGroupChat` with `MagenticOneGroupChat`. For example:

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
    await Console(team.run_stream(task="Provide a different proof for Fermat's Last Theorem"))
    await model_client.close()

asyncio.run(main())
```


To utilize a different model, refer to the "Models" documentation for more information.

Alternatively, you can incorporate the Magentic-One agents directly into an `AgentChat` team:

> **Caution**
> The example code provided may download files from the internet, execute code, and interact with web pages. Ensure you are operating within a safe environment before running this example code.

```python
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
# from autogen_ext.agents.file_surfer import FileSurfer
# from autogen_ext.agents.magentic_one import MagenticOneCoderAgent
# from autogen_agentchat.agents import CodeExecutorAgent
# from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    surfer = MultimodalWebSurfer(
        "WebSurfer",
        model_client=model_client,
    )
    team = MagenticOneGroupChat([surfer], model_client=model_client)
    await Console(team.run_stream(task="What is the UV index in Melbourne today?"))
    # # Note: you can also use other agents in the team
    # team = MagenticOneGroupChat([surfer, file_surfer, coder, terminal], model_client=model_client)
    # file_surfer = FileSurfer("FileSurfer",model_client=model_client)
    # coder = MagenticOneCoderAgent("Coder",model_client=model_client)
    # terminal = CodeExecutorAgent("ComputerTerminal",code_executor=LocalCommandLineCodeExecutor())

asyncio.run(main())
```


Furthermore, you can use the `MagenticOne` helper class, which bundles all the agents together for simplified usage:

```python
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.teams.magentic_one import MagenticOne
from autogen_agentchat.ui import Console

async def example_usage():
    client = OpenAIChatCompletionClient(model="gpt-4o")
    m1 = MagenticOne(client=client)
    task = "Write a Python script to fetch data from an API."
    result = await Console(m1.run_stream(task=task))
    print(result)

if __name__ == "__main__":
    asyncio.run(example_usage())
```

### Architecture#

Magentic-One's operational framework is built upon a multi-agent architecture where a central `Orchestrator` agent is tasked with high-level planning, directing other agents, and diligently tracking overall task progress. The `Orchestrator` initiates its work by formulating a plan to address the given task, concurrently gathering necessary facts and educated guesses into a continuously maintained `Task Ledger`.

At each step defined within its plan, the `Orchestrator` generates a `Progress Ledger` where it conducts self-reflection on the task's advancement and verifies whether the task has been completed. If the task remains incomplete, it assigns a subtask to one of Magentic-One's other specialized agents. Once the assigned agent successfully completes its subtask, the `Orchestrator` updates the `Progress Ledger` and continues this iterative process until the primary task is fulfilled. Should the `Orchestrator` detect insufficient progress over a series of steps, it possesses the ability to update the `Task Ledger` and devise a new plan. This process is visualized as the `Orchestrator`'s work being divided into an "outer loop" for updating the `Task Ledger` and an "inner loop" for updating the `Progress Ledger`.

Overall, Magentic-One is comprised of the following key agents:

*   **Orchestrator**: This is the lead agent, singularly responsible for comprehensive task decomposition and planning. It directs other agents in the execution of subtasks, tracks the overall progress, and implements corrective actions when necessary.
*   **WebSurfer**: An LLM-based agent highly skilled in commanding and managing the state of a Chromium-based web browser. For each incoming request, the `WebSurfer` executes an action on the browser and subsequently reports on the new state of the webpage. Its action space is extensive, encompassing navigation (e.g., visiting a URL, performing a web search), web page actions (e.g., clicking and typing), and reading actions (e.g., summarizing or answering questions). The `WebSurfer` effectively performs its actions by relying on the browser's accessibility tree and employing set-of-marks prompting.
*   **FileSurfer**: An LLM-based agent capable of commanding a markdown-based file preview application to read local files of most types. The `FileSurfer` can also perform common navigation tasks, such as listing directory contents and traversing folder structures.
*   **Coder**: An LLM-based agent specifically specialized through its system prompt for writing code, analyzing information collected from other agents, or creating new artifacts.
*   **ComputerTerminal**: This agent provides the team with access to a console shell. It is within this shell that the `Coder`’s programs can be executed, and new programming libraries can be installed.

Collectively, Magentic-One’s agents furnish the `Orchestrator` with the requisite tools and capabilities to solve a wide array of open-ended problems. Furthermore, they enable the system to autonomously adapt to, and operate within, dynamic and constantly evolving web and file-system environments.

While the default multimodal LLM used for all agents is GPT-4o, Magentic-One maintains model agnosticism. This allows it to incorporate heterogeneous models to support diverse capabilities or meet varying cost requirements during task execution. For instance, it can leverage different LLMs and SLMs, along with their specialized versions, to power different agents. A strong reasoning model, such as GPT-4o, is recommended for the `Orchestrator` agent. In an alternative configuration of Magentic-One, experimentation has been conducted using OpenAI o1-preview for the `Orchestrator`'s outer loop and for the `Coder` agent, while other agents continue to use GPT-4o.