# Selector Group Chat

`SelectorGroupChat` implements a sophisticated team collaboration mechanism where participating agents take turns broadcasting messages to all other members. What distinguishes this group chat is its reliance on a generative model, typically a Large Language Model (LLM), to intelligently select the next speaker. This model-based selection ensures dynamic and context-aware collaboration among agents.

Key features of `SelectorGroupChat` include:

*   **Model-based speaker selection**: The core mechanism for determining which agent speaks next.
*   **Configurable participant roles and descriptions**: Allows for clear definition of each agent's purpose, which the model uses for selection.
*   **Prevention of consecutive turns by the same speaker (optional)**: Provides control over agent speaking patterns.
*   **Customizable selection prompting**: Enables tailoring the prompt given to the LLM to guide speaker selection.
*   **Customizable selection function**: Offers the ability to override the default model-based selection with custom logic.
*   **Customizable candidate function**: Allows for narrowing down the pool of agents eligible for selection using a model.

**Note:** `SelectorGroupChat` is classified as a high-level API. For developers requiring more granular control and extensive customization capabilities, it is recommended to consult the Group Chat Pattern documentation within the Core API. This documentation provides the necessary insights to implement bespoke group chat logic.

### How Does it Work?

`SelectorGroupChat` functions as a group chat, sharing similarities with `RoundRobinGroupChat`, but critically differentiates itself through its model-based mechanism for selecting the subsequent speaker. Upon receiving a task via either the `run()` or `run_stream()` methods, the team initiates a structured execution process:

1.  **Contextual Analysis and Speaker Determination**: The team first analyzes the current conversation context. This analysis encompasses the entire conversation history, alongside the name and description attributes of all participating agents, to determine the most appropriate next speaker using an underlying model. By default, the system prevents the same agent from speaking consecutively, unless it is the only agent available for selection. This default behavior can be overridden by setting `allow_repeated_speaker=True`. Furthermore, developers have the option to entirely bypass the model's selection by providing a custom `selector_func`.
2.  **Response Generation and Broadcasting**: Once the next speaker is selected, the team prompts that chosen agent to provide a response. This response is then **broadcasted** to all other participants within the chat.
3.  **Termination Condition Check**: Following the message broadcast, a predefined termination condition is evaluated to ascertain whether the conversation should conclude. If the condition is not met, the entire process—starting from step 1—reiterates.
4.  **Task Result and Context Preservation**: When the conversation successfully reaches its termination condition, the team returns a `TaskResult` object, which encapsulates the complete conversation history pertinent to the task. A key feature is that the conversation context, including all participant states, is preserved within the team. This allows subsequent tasks to seamlessly continue from the state of the previous conversation. To reset the conversation context entirely, one can invoke the `reset()` method.

In the subsequent sections, we will illustrate the practical application of `SelectorGroupChat` using a simple example centered around a web search and data analysis task.

### Example: Web Search/Analysis

```python
from typing import List, Sequence
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
```


#### Agents

This system employs three distinct specialized agents, each with a defined role:

*   **Planning Agent**: This agent serves as the strategic coordinator. Its primary function is to decompose complex tasks into smaller, more manageable subtasks.
*   **Web Search Agent**: An information retrieval specialist, this agent interfaces with the `search_web_tool`.
*   **Data Analyst Agent**: This agent specializes in performing calculations and is equipped with the `percentage_change_tool`.

It is important to note that the `search_web_tool` and `percentage_change_tool` are external tools that these agents can leverage to execute their assigned tasks.

```python
# Note: This example uses mock tools instead of real APIs for demonstration purposes
def search_web_tool(query: str) -> str:
    if "2006-2007" in query:
        return """Here are the total points scored by Miami Heat players in the 2006-2007 season:
    Udonis Haslem: 844 points
    Dwayne Wade: 1397 points
    James Posey: 550 points
    ...
    """
    elif "2007-2008" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214."
    elif "2008-2009" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398."
    return "No data found."

def percentage_change_tool(start: float, end: float) -> float:
    return ((end - start) / start) * 100
```


Let’s proceed by creating these specialized agents using the `AssistantAgent` class. A crucial consideration here is the judicious selection of meaningful names and descriptions for the agents. These attributes are directly utilized by the underlying model to determine the most appropriate next speaker, thus influencing the flow and effectiveness of the group chat.

```python
model_client = OpenAIChatCompletionClient(model="gpt-4o")

planning_agent = AssistantAgent(
    "PlanningAgent",
    description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
    model_client=model_client,
    system_message="""
    You are a planning agent.
    Your job is to break down complex tasks into smaller, manageable subtasks.
    Your team members are:
    WebSearchAgent: Searches for information
    DataAnalystAgent: Performs calculations
    You only plan and delegate tasks - you do not execute them yourself.
    When assigning tasks, use this format:
    1. <agent> : <task>
    After all tasks are complete, summarize the findings and end with "TERMINATE".
    """,
)

web_search_agent = AssistantAgent(
    "WebSearchAgent",
    description="An agent for searching information on the web.",
    tools=[search_web_tool],
    model_client=model_client,
    system_message="""
    You are a web search agent.
    Your only tool is search_tool - use it to find information.
    You make only one search call at a time.
    Once you have the results, you never do calculations based on them.
    """,
)

data_analyst_agent = AssistantAgent(
    "DataAnalystAgent",
    description="An agent for performing calculations.",
    model_client=model_client,
    tools=[percentage_change_tool],
    system_message="""
    You are a data analyst.
    Given the tasks you have been assigned, you should analyze the data and provide results using the tools provided.
    If you have not seen the data, ask for it.
    """,
)
```


**Note:** By default, `AssistantAgent` returns the direct output of any tool it uses as its response. If the tool's output is not already a well-formed string in natural language, it is advisable to incorporate a reflection step within the agent. This can be achieved by setting `reflect_on_tool_use=True` when instantiating the agent. This setting enables the agent to critically evaluate the tool's output and then formulate a coherent, natural language response.

#### Workflow

The `SelectorGroupChat` initiates the process by receiving the task. Based on the comprehensive descriptions provided for each agent, it intelligently selects the most appropriate agent to handle the initial task. Typically, this responsibility falls to the Planning Agent.

The workflow proceeds as follows:

*   The **Planning Agent** meticulously analyzes the task, breaking it down into smaller, discrete subtasks. Each subtask is then assigned to the most suitable agent, adhering to a structured format: `<agent> : <task>`.
*   Dynamically, the `SelectorGroupChat` manager leverages the ongoing conversation context and agent descriptions to select the next agent, ensuring that the assigned subtask is addressed by the correct specialist.
*   The **Web Search Agent** executes searches one at a time, meticulously storing the retrieved results within the shared conversation history for collective access.
*   The **Data Analyst** processes the accumulated information, applying available calculation tools as and when it is selected to contribute.

This dynamic workflow continues with agents being selected on an as-needed basis until one of the following conditions is met:

*   The Planning Agent conclusively determines that all subtasks have been completed and signals the termination of the conversation by sending "TERMINATE".
*   An alternative, pre-defined termination condition is triggered, such as reaching a maximum allowable number of messages within the conversation.

When defining your agents, it is crucial to include a descriptive and helpful explanation of their function. This description directly informs the selection mechanism, ensuring the correct agent is chosen for subsequent actions.

#### Termination Conditions

To effectively manage the conversation flow, we will implement two distinct termination conditions: `TextMentionTermination` and `MaxMessageTermination`. `TextMentionTermination` will cease the conversation once the Planning Agent explicitly sends the "TERMINATE" message. Concurrently, `MaxMessageTermination` will impose a hard limit of 25 messages on the conversation, serving as a safeguard against potential infinite loops.

```python
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination
```


#### Selector Prompt

The `SelectorGroupChat` utilizes a sophisticated model to intelligently select the next speaker, basing its decision on the prevailing conversation context. To ensure optimal alignment with our defined workflow, we will employ a custom selector prompt.

```python
selector_prompt = """Select an agent to perform task.
{roles}
Current conversation context:
{history}
Read the above conversation, then select an agent from  {participants}  to perform the next task.
Make sure the planner agent has assigned tasks before other agents start working.
Only select one agent.
"""
```


The selector prompt supports specific string variables that are dynamically populated to provide context to the model:

*   `{participants}`: This variable is replaced with a list of the names of all agents eligible for selection, formatted as `["<name1>", "<name2>", ...]`.
*   `{roles}`: This variable provides a newline-separated list detailing the names and descriptions of each candidate agent. The format for each line is: `"<name> : <description>"`.
*   `{history}`: This variable contains the complete conversation history, formatted as a double newline-separated sequence of names and message content. Each message adheres to the format: `"<name> : <message content>"`.

**Tip:** Strive to avoid overwhelming the model with excessive instructions within the selector prompt.

The optimal level of instruction largely hinges on the capabilities of the model you are employing. For highly capable models such as GPT-4o and its equivalents, a selector prompt can incorporate specific conditions for when each speaker should be chosen. However, for smaller models like Phi-4, it is best practice to maintain the selector prompt as concise and simple as possible, similar to the example provided above.

Generally, if you find yourself constructing numerous conditional statements for each agent within the selector prompt, it often signals that a more advanced approach is warranted. In such cases, consider either implementing a custom selection function or refactoring the task into smaller, sequential components that can be handled by distinct agents or specialized teams.

#### Running the Team

Now, let us proceed to assemble the team, integrating the agents, the predefined termination conditions, and our custom selector prompt.

```python
team = SelectorGroupChat(
    [planning_agent, web_search_agent, data_analyst_agent],
    model_client=model_client,
    termination_condition=termination,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=True,  # Allow an agent to speak multiple turns in a row.
)
```


With the team configured, we can now initiate its operation by providing a specific task: to find information about an NBA player and perform a calculation.

```python
task = "Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?"
# Use asyncio.run(...) if you are running this in a script.
await Console(team.run_stream(task=task))
```

Output:

```
---------- user ----------
Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
---------- PlanningAgent ----------
To complete this task, we need to perform the following subtasks:
1. Find out which Miami Heat player had the highest points in the 2006-2007 season.
2. Gather data on this player's total rebounds for the 2007-2008 season.
3. Gather data on this player's total rebounds for the 2008-2009 season.
4. Calculate the percentage change in the player's total rebounds between the 2007-2008 and 2008-2009 seasons.

I'll assign these tasks accordingly:
1. WebSearchAgent: Search for the Miami Heat player with the highest points in the 2006-2007 NBA season.
2. WebSearchAgent: Find the total rebounds for this player in the 2007-2008 NBA season.
3. WebSearchAgent: Find the total rebounds for this player in the 2008-2009 NBA season.
4. DataAnalystAgent: Calculate the percentage change in total rebounds from the 2007-2008 season to the 2008-2009 season for this player.
---------- WebSearchAgent ----------
[FunctionCall(id='call_89tUNHaAM0kKQYPJLleGUKK7', arguments='{"query":"Miami Heat player highest points 2006-2007 season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', name='search_web_tool', call_id='call_89tUNHaAM0kKQYPJLleGUKK7', is_error=False)]
---------- WebSearchAgent ----------
Here are the total points scored by Miami Heat players in the 2006-2007 season: Udonis Haslem: 844 points Dwayne Wade: 1397 points James Posey: 550 points ...
---------- WebSearchAgent ----------
The Miami Heat player with the highest points in the 2006-2007 season was Dwyane Wade
```


```
, with 1,397 points. Next, I will search for Dwyane Wade's total rebounds for the 2007-2008 season.
---------- WebSearchAgent ----------
[FunctionCall(id='call_RC55TkSjG3JXRuVOTPrcE1RL', arguments='{"query":"Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', name='search_web_tool', call_id='call_RC55TkSjG3JXRuVOTPrcE1RL', is_error=False)]
---------- WebSearchAgent ----------
The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.
---------- WebSearchAgent ----------
[FunctionCall(id='call_pBXoABrErDow0rZjw3tjOZol', arguments='{"query":"Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', name='search_web_tool', call_id='call_pBXoABrErDow0rZjw3tjOZol', is_error=False)]
---------- WebSearchAgent ----------
The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
---------- DataAnalystAgent ----------
[FunctionCall(id='call_qMxxXtcJsiK8KFSSCx3zm0is', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
---------- DataAnalystAgent ----------
[FunctionExecutionResult(content='85.98130841121495', name='percentage_change_tool', call_id='call_qMxxXtcJsiK8KFSSCx3zm0is', is_error=False)]
---------- DataAnalystAgent ----------
85.98130841121495
---------- PlanningAgent ----------
The player with the highest points for the Miami Heat in the 2006-2007 NBA season was Dwyane Wade, who scored 1,397 points. The percentage change in Dwyane Wade's total rebounds from 214 in the 2007-2008 season to 398 in the 2008-2009 season is approximately 85.98%. TERMINATE
TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?', type='TextMessage'), TextMessage(source='PlanningAgent', models_usage
```


```
=RequestUsage(prompt_tokens=161, completion_tokens=220), metadata={}, content="To complete this task, we need to perform the following subtasks:\n\n1. Find out which Miami Heat player had the highest points in the 2006-2007 season.\n2. Gather data on this player's total rebounds for the 2007-2008 season.\n3. Gather data on this player's total rebounds for the 2008-2009 season.\n4. Calculate the percentage change in the player's total rebounds between the 2007-2008 and 2008-2009 seasons.\n\nI'll assign these tasks accordingly:\n\n1. WebSearchAgent: Search for the Miami Heat player with the highest points in the 2006-2007 NBA season.\n2. WebSearchAgent: Find the total rebounds for this player in the 2007-2008 NBA season.\n3. WebSearchAgent: Find the total rebounds for this player in the 2008-2009 NBA season.\n4. DataAnalystAgent: Calculate the percentage change in total rebounds from the 2007-2008 season to the 2008-2009 season for this player.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=368, completion_tokens=27), metadata={}, content=[FunctionCall(id='call_89tUNHaAM0kKQYPJLleGUKK7', arguments='{"query":"Miami Heat player highest points 2006-2007 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', name='search_web_tool', call_id='call_89tUNHaAM0kKQYPJLleGUKK7', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', type='ToolCallSummaryMessage'), ThoughtEvent(source='WebSearchAgent', models_usage=None, metadata={}, content="The Miami Heat player with the highest points in the 2006-2007 season was Dwyane Wade, with 1,397 points.\n\nNext, I will search for Dwyane Wade's total rebounds for the 200
```


```
7-2008 season.", type='ThoughtEvent'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=460, completion_tokens=83), metadata={}, content=[FunctionCall(id='call_RC55TkSjG3JXRuVOTPrcE1RL', arguments='{"query":"Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', name='search_web_tool', call_id='call_RC55TkSjG3JXRuVOTPrcE1RL', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=585, completion_tokens=28), metadata={}, content=[FunctionCall(id='call_pBXoABrErDow0rZjw3tjOZol', arguments='{"query":"Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', name='search_web_tool', call_id='call_pBXoABrErDow0rZjw3tjOZol', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=496, completion_tokens=21), metadata={}, content=[FunctionCall(id='call_qMxxXtcJsiK8KFSSCx3zm0is', arguments='{"start":214,"end":398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='85.98130841121495', name='percentage_change_tool', call_id='call_qMxxXtcJsiK8KFSSCx3zm0is', is_error=Fal
```


```
se)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, metadata={}, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=528, completion_tokens=80), metadata={}, content="The player with the highest points for the Miami Heat in the 2006-2007 NBA season was Dwyane Wade, who scored 1,397 points. The percentage change in Dwyane Wade's total rebounds from 214 in the 2007-2008 season to 398 in the 2008-2009 season is approximately 85.98%.\n\nTERMINATE", type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
```


As the output clearly demonstrates, the `Web Search Agent` successfully executed the necessary searches, and the `Data Analyst Agent` diligently completed the required calculations. The outcome reveals that Dwyane Wade was indeed the Miami Heat player who achieved the highest points in the 2006-2007 season. Furthermore, his total rebounds exhibited a significant 85.98% increase between the 2007-2008 and 2008-2009 seasons.

### Custom Selector Function

Frequently, a more granular control over the agent selection process becomes desirable. To achieve this, the `selector_func` argument can be utilized to provide a custom selector function. This function overrides the default model-based selection, thereby enabling the implementation of more intricate selection logic and state-based transitions within the chat.

For instance, a common requirement might be to ensure that the Planning Agent consistently speaks immediately following any specialized agent, allowing it to promptly check the progress of the task.

**Note:** If a custom selector function returns `None`, the `SelectorGroupChat` will then revert to its default model-based selection mechanism.

```python
def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
    if messages[-1].source != planning_agent.name:
        return planning_agent.name
    return None

# Reset the previous team and run the chat again with the selector function.
await team.reset()
team = SelectorGroupChat(
    [planning_agent, web_search_agent, data_analyst_agent],
    model_client=model_client,
    termination_condition=termination,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=True,
    selector_func=selector_func,
)
await Console(team.run_stream(task=task))
```

Output:

```
---------- user ----------
Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
---------- PlanningAgent ----------
To answer this question, we need to follow these steps:
1. Identify the Miami Heat player with the highest points in the 2006-2007 season.
2. Retrieve the total rebounds of that player for the 2007-2008 and 2008-2009 seasons.
3. Calculate the percentage change in his total rebounds between the two seasons.

Let's delegate these tasks:
1. WebSearchAgent: Find the Miami Heat player with the highest points in the 2006-2007 NBA season.
2. WebSearchAgent: Retrieve the total rebounds for the identified player during the 2007-2008 NBA season.
3. WebSearchAgent: Retrieve the total rebounds for the identified player during the 2008-2009 NBA season.
4. DataAnalystAgent: Calculate the percentage change in total rebounds from the 2007-2008 and 2008-2009 seasons for the player found.
```


```
---------- WebSearchAgent ----------
[FunctionCall(id='call_Pz82ndNLSV4cH0Sg6g7ArP4L', arguments='{"query":"Miami Heat player highest points 2006-2007 season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', call_id='call_Pz82ndNLSV4cH0Sg6g7ArP4L')]
---------- WebSearchAgent ----------
Here are the total points scored by Miami Heat players in the 2006-2007 season: Udonis Haslem: 844 points Dwayne Wade: 1397 points James Posey: 550 points ...
---------- PlanningAgent ----------
Great! Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season. Now, let's continue with the next tasks:
2. WebSearchAgent: Retrieve the total rebounds for Dwyane Wade during the 2007-2008 NBA season.
3. WebSearchAgent: Retrieve the total rebounds for Dwyane Wade during the 2008-2009 NBA season.
---------- WebSearchAgent ----------
[FunctionCall(id='call_3qv9so2DXFZIHtzqDIfXoFID', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool'), FunctionCall(id='call_Vh7zzzWUeiUAvaYjP0If0k1k', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_3qv9so2DXFZIHtzqDIfXoFID'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_Vh7zzzWUeiUAvaYjP0If0k1k')]
---------- WebSearchAgent ----------
The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214. The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
---------- PlanningAgent ----------
Now let's calculate the percentage change in total rebounds between the 2007-2008 and 2008-2009 seasons for Dwyane Wade.
4. DataAnalystAgent: Calculate the percentage change in total rebounds for Dwyane Wade between the 2007-2008 and 2008-2009 seasons.
```


```
---------- DataAnalystAgent ----------
[FunctionCall(id='call_FXnPSr6JVGfAWs3StIizbt2V', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
---------- DataAnalystAgent ----------
[FunctionExecutionResult(content='85.98130841121495', call_id='call_FXnPSr6JVGfAWs3StIizbt2V')]
---------- DataAnalystAgent ----------
85.98130841121495
---------- PlanningAgent ----------
Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring a total of 1397 points. The percentage change in his total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds) is approximately 86.0%. TERMINATE
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?', type='TextMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=161, completion_tokens=192), content="To answer this question, we need to follow these steps: \n\n1. Identify the Miami Heat player with the highest points in the 2006-2007 season.\n2. Retrieve the total rebounds of that player for the 2007-2008 and 2008-2009 seasons.\n3. Calculate the percentage change in his total rebounds between the two seasons.\n\nLet's delegate these tasks:\n\n1. WebSearchAgent: Find the Miami Heat player with the highest points in the 2006-2007 NBA season.\n2. WebSearchAgent: Retrieve the total rebounds for the identified player during the 2007-2008 NBA season.\n3. WebSearchAgent: Retrieve the total rebounds for the identified player during the 2008-2009 NBA season.\n4.
```


```
DataAnalystAgent: Calculate the percentage change in total rebounds between the 2007-2008 and 2008-2009 seasons for the player found.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=340, completion_tokens=27), content=[FunctionCall(id='call_Pz82ndNLSV4cH0Sg6g7ArP4L', arguments='{"query":"Miami Heat player highest points 2006-2007 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', call_id='call_Pz82ndNLSV4cH0Sg6g7ArP4L')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=420, completion_tokens=87), content="Great! Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season. Now, let's continue with the next tasks:\n\n2. WebSearchAgent: Retrieve the total rebounds for Dwyane Wade during the 2007-2008 NBA season.\n3.
```


```
WebSearchAgent: Retrieve the total rebounds for Dwyane Wade during the 2008-2009 NBA season.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=525, completion_tokens=71), content=[FunctionCall(id='call_3qv9so2DXFZIHtzqDIfXoFID', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool'), FunctionCall(id='call_Vh7zzzWUeiUAvaYjP0If0k1k', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_3qv9so2DXFZIHtzqDIfXoFID'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_Vh7zzzWUeiUAvaYjP0If0k1k')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.\nThe number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=569, completion_tokens=68), content="Now let's calculate the percentage change in total rebounds between the 2007-2008 and 2008-2009 seasons for Dwyane Wade.\n\n4.
```


```
DataAnalystAgent: Calculate the percentage change in total rebounds for Dwyane Wade between the 2007-2008 and 2008-2009 seasons.", type='TextMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=627, completion_tokens=21), content=[FunctionCall(id='call_FXnPSr6JVGfAWs3StIizbt2V', arguments='{"start":214,"end":398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, content=[FunctionExecutionResult(content='85.98130841121495', call_id='call_FXnPSr6JVGfAWs3StIizbt2V')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=659, completion_tokens=76), content='Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring a total of 1397 points. The percentage change in his total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds) is approximately 86.0%.\n\nTERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
```


From the conversation log, it is clearly observable that the Planning Agent consistently intervenes immediately after any specialized agent has spoken. This ensures regular oversight and progress checks.

**Tip:** Each participant agent typically executes only a single step per turn, whether it's running tools or generating a response. If you desire an `AssistantAgent` to persist in its actions until all necessary tools have been run (i.e., until it no longer returns a `ToolCallSummaryMessage`), you can achieve this by inspecting the last message in the conversation. If the last message is a `ToolCallSummaryMessage`, you can then instruct the agent to continue its turn.

### Custom Candidate Function

Another pertinent requirement might involve the automatic selection of the subsequent speaker from a refined, filtered list of agents. To address this, the `candidate_func` parameter can be configured with a custom candidate function. This function's purpose is to narrow down the pool of potential agents available for speaker selection during each turn of the group chat.

This capability provides the flexibility to restrict speaker selection to a predefined subset of agents following a specific agent's turn.

**Note:** The `candidate_func` is only valid and will only be evaluated if the `selector_func` parameter is not set. Furthermore, returning either `None` or an empty list (`[]`) from the custom candidate function will result in a `ValueError` being raised.

```python
def candidate_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> List[str]:
    # keep planning_agent first one to plan out the tasks
    if messages[-1].source == "user":
        return [planning_agent.name]

    # if previous agent is planning_agent and if it explicitely asks for web_search_agent
    # or data_analyst_agent or both (in-case of re-planning or re-assignment of tasks)
    # then return those specific agents
    last_message = messages[-1]
    if last_message.source == planning_agent.name:
        participants = []
        if web_search_agent.name in last_message.to_text():
            participants.append(web_search_agent.name)
        if data_analyst_agent.name in last_message.to_text():
            participants.append(data_analyst_agent.name)
        if participants:
            return participants

    # SelectorGroupChat will select from the remaining two agents.
    # we can assume that the task is finished once the web_search_agent
    # and data_analyst_agent have took their turns, thus we send
    # in planning_agent to terminate the chat
    previous_set_of_agents = set(message.source for message in messages)
    if web_search_agent.name in previous_set_of_agents and data_analyst_agent.name in previous_set_of_agents:
        return [planning_agent.name]

    # if no-conditions are met then return all the agents
    return [planning_agent.name, web_search_agent.name, data_analyst_agent.name]

# Reset the previous team and run the chat again with the selector function.
await team.reset()
team = SelectorGroupChat(
    [planning_agent, web_search_agent, data_analyst_agent],
    model_client=model_client,
    termination_condition=termination,
    candidate_func=candidate_func,
)
await Console(team.run_stream(task=task))
```

Output:

```
---------- user ----------
Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
---------- PlanningAgent ----------
To answer this question, we'll break it down into two main subtasks:
1. Identify the Miami Heat player with the highest p
```


```
oints in the 2006-2007 season.
2. Calculate the percentage change in that player's total rebounds between the 2007-2008 and 2008-2009 seasons.

Let's assign these tasks:
1. WebSearchAgent: Search for the Miami Heat player with the highest points in the 2006-2007 NBA season.
2. WebSearchAgent: Find the total rebound statistics for that identified player for both the 2007-2008 and 2008-2009 NBA seasons.
3. DataAnalystAgent: Calculate the percentage change in the player's total rebounds between the 2007-2008 and 2008-2009 seasons once the data is retrieved.
---------- WebSearchAgent ----------
[FunctionCall(id='call_WtR5KTfEIxs3jIO25gjAw7dF', arguments='{"query":"Miami Heat highest points scorer 2006-2007 NBA season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', name='search_web_tool', call_id='call_WtR5KTfEIxs3jIO25gjAw7dF', is_error=False)]
---------- WebSearchAgent ----------
Here are the total points scored by Miami Heat players in the 2006-2007 season: Udonis Haslem: 844 points Dwayne Wade: 1397 points James Posey: 550 points ...
---------- DataAnalystAgent ----------
[FunctionCall(id='call_9HA3DEacUl4WuG2G2PtRkXAO', arguments='{"start": 432, "end": 527}', name='percentage_change_tool')]
---------- DataAnalystAgent ----------
[FunctionExecutionResult(content='21.99074074074074', name='percentage_change_tool', call_id='call_9HA3DEacUl4WuG2G2PtRkXAO', is_error=False)]
---------- DataAnalystAgent ----------
21.99074074074074
---------- PlanningAgent ----------
It seems we've missed some context there, so let's assign the subtasks again for clarity: Based on the search results, Dwyane Wade had the highest points for the Miami Heat in the 2006-2007 season with 1397 points. Now, let's find the necessary rebound statistics:
2. WebSearchAgent: Find Dwyane Wade's total rebound statistics for both the 2007-2008 and 2008-2009 NBA seasons.
3. DataAnalystAgent: Once the data is retrieved, calculate the percentage change in Dwyane Wade's total rebounds between the 2007-2008 and 2008-2009 seasons. ------
```


```
---- WebSearchAgent ----------
[FunctionCall(id='call_3i1wTDSjkGg6Ev8YKYWkZK55', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 NBA season"}', name='search_web_tool'), FunctionCall(id='call_NRAs6jHxXRi8zsvpW5WlHAaU', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 NBA season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', name='search_web_tool', call_id='call_3i1wTDSjkGg6Ev8YKYWkZK55', is_error=False), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', name='search_web_tool', call_id='call_NRAs6jHxXRi8zsvpW5WlHAaU', is_error=False)]
---------- WebSearchAgent ----------
The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214. The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
---------- PlanningAgent ----------
The total rebounds for Dwyane Wade in the 2007-2008 season were 214, and in the 2008-2009 season, they were 398. Now, let's calculate the percentage change.
3. DataAnalystAgent: Calculate the percentage change in Dwyane Wade's total rebounds from the 2007-2008 season to the 2008-2009 season.
---------- DataAnalystAgent ----------
[FunctionCall(id='call_XECA7ezz7VIKbf8IbZYSCSpI', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
---------- DataAnalystAgent ----------
[FunctionExecutionResult(content='85.98130841121495', name='percentage_change_tool', call_id='call_XECA7ezz7VIKbf8IbZYSCSpI', is_error=False)]
---------- DataAnalystAgent ----------
85.98130841121495
---------- PlanningAgent ----------
The Miami Heat player with the highest points in the 2006-2007 season was Dwyane Wade, with 1397 points. The percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons was approximately 85.98%. TERMINATE
TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
```


```
', type='TextMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=161, completion_tokens=169), metadata={}, content="To answer this question, we'll break it down into two main subtasks:\n\n1. Identify the Miami Heat player with the highest points in the 2006-2007 season.\n2. Calculate the percentage change in that player's total rebounds between the 2007-2008 and 2008-2009 seasons.\n\nLet's assign these tasks:\n\n1. WebSearchAgent: Search for the Miami Heat player with the highest points in the 2006-2007 NBA season.\n2. WebSearchAgent: Find the total rebound statistics for that identified player for both the 2007-2008 and 2008-2009 NBA seasons.\n3. DataAnalystAgent: Calculate the percentage change in the player's total rebounds between the 2007-2008 and 2008-2009 seasons once the data is retrieved.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=324, completion_tokens=28), metadata={}, content=[FunctionCall(id='call_WtR5KTfEIxs3jIO25gjAw7dF', arguments='{"query":"Miami Heat highest points scorer 2006-2007 NBA season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', name='search_web_tool', call_id='call_WtR5KTfEIxs3jIO25gjAw7dF', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=390, completion_tokens=37), metadata={}, content=[FunctionCall(id='call_9HA3DEacUl4WuG2G2PtRkXAO', arguments='{"start": 432, "end": 527}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, me
```


```
tadata={}, content=[FunctionExecutionResult(content='21.99074074074074', name='percentage_change_tool', call_id='call_9HA3DEacUl4WuG2G2PtRkXAO', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, metadata={}, content='21.99074074074074', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=413, completion_tokens=137), metadata={}, content="It seems we've missed some context there, so let's assign the subtasks again for clarity:\n\nBased on the search results, Dwyane Wade had the highest points for the Miami Heat in the 2006-2007 season with 1397 points.\n\nNow, let's find the necessary rebound statistics:\n\n2. WebSearchAgent: Find Dwyane Wade's total rebound statistics for both the 2007-2008 and 2008-2009 NBA seasons.\n3. DataAnalystAgent: Once the data is retrieved, calculate the percentage change in Dwyane Wade's total rebounds between the 2007-2008 and 2008-2009 seasons.", type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=576, completion_tokens=73), metadata={}, content=[FunctionCall(id='call_3i1wTDSjkGg6Ev8YKYWkZK55', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 NBA season"}', name='search_web_tool'), FunctionCall(id='call_NRAs6jHxXRi8zsvpW5WlHAaU', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 NBA season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_3i1wTDSjkGg6Ev8YKYWkZK55'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_NRAs6jHxXRi8zsvpW5WlHAaU')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, metadata={}, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.\nThe number of total rebounds for Dwayne Wad
```


```
e in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=612, completion_tokens=84), metadata={}, content="The total rebounds for Dwyane Wade in the 2007-2008 season were 214, and in the 2008-2009 season, they were 398.\n\nNow, let's calculate the percentage change.\n\n3. DataAnalystAgent: Calculate the percentage change in Dwyane Wade's total rebounds from the 2007-2008 season to the 2008-2009 season.", type='TextMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=720, completion_tokens=21), metadata={}, content=[FunctionCall(id='call_XECA7ezz7VIKbf8IbZYSCSpI', arguments='{"start":214,"end":398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, metadata={}, content=[FunctionExecutionResult(content='85.98130841121495', call_id='call_XECA7ezz7VIKbf8IbZYSCSpI')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=718, completion_tokens=63), content='Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring a total of 1397 points. The percentage change in his total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds) is approximately 86.0%.\n\nTERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
```


From the conversation log, it is evident that the Planning Agent re-engages in the conversation once the `Web Search Agent` and `Data Analyst Agent` have completed their respective turns. It observes that the task was not concluded as expected. Consequently, it proactively re-invokes the `WebSearchAgent` to retrieve the necessary rebound values, and subsequently, calls upon the `DataAnalystAgent` to compute the percentage change.

### User Feedback

To integrate human oversight and interaction into the agent team, a `UserProxyAgent` can be incorporated. For a deeper understanding of `UserProxyAgent`'s capabilities, refer to the "Human-in-the-Loop" documentation.

To enable user feedback in the web search example, we simply add the `UserProxyAgent` to the team. Subsequently, we modify the selector function to consistently prompt for user feedback immediately after the planning agent has spoken. If the user's response contains "APPROVE" (case-insensitive), the conversation proceeds. Otherwise, the planning agent attempts to revise its plan, repeating this cycle until user approval is granted.

```python
user_proxy_agent = UserProxyAgent("UserProxyAgent", description="A proxy for the user to approve or disapprove tasks.")

def selector_func_with_user_proxy(
    messages: Sequence[BaseAgentEvent | BaseChatMessage]
) -> str | None:
    if messages[-1].source != planning_agent.name and messages[-1].source != user_proxy_agent.name:
        # Planning agent should be the first to engage when given a new task, or check progress.
        return planning_agent.name

    if messages[-1].source == planning_agent.name:
        if messages[-2].source == user_proxy_agent.name and "APPROVE" in messages[-1].content.upper():  # type: ignore
            # User has approved the plan, proceed to the next agent.
            return None
        # Use the user proxy agent to get the user's approval to proceed.
        return user_proxy_agent.name

    if messages[-1].source == user_proxy_agent.name:
        # If the user does not approve, return to the planning agent.
        if "APPROVE" not in messages[-1].content.upper():  # type: ignore
            return planning_agent.name
        return None

# Reset the previous agents and run the chat again with the user proxy agent and selector function.
await team.reset()
team = SelectorGroupChat(
    [planning_agent, web_search_agent, data_analyst_agent, user_proxy_agent],
    model_client=model_client,
    termination_condition=termination,
    selector_prompt=selector_prompt,
    selector_func=selector_func_with_user_proxy,
    allow_repeated_speaker=True,
)
await Console(team.run_stream(task=task))
```

Output:

```
---------- user ----------
Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
---------- PlanningAgent ----------
To address the user's query, we will need to perform the following tasks:
1. Identify the Miami Heat player with the highest points in the 2006-2007 season.
2. Find the total rebounds for that player in the 2007-2008 season.
3. Find the total rebounds for that player in the 2008-2009 season.
4.
```


```
Calculate the percentage change in the total rebounds between the 2007-2008 and 2008-2009 seasons. Let's assign these tasks:
1. **WebSearchAgent**: Identify the Miami Heat player with the highest points in the 2006-2007 season. (Task 2 and 3 depend on the result of Task 1. We'll proceed with Tasks 2 and 3 once Task 1 is complete.)
---------- UserProxyAgent ----------
approve
---------- WebSearchAgent ----------
[FunctionCall(id='call_0prr3fUnG5CtisUG7QeygW0w', arguments='{"query":"Miami Heat highest points scorer 2006-2007 NBA season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', call_id='call_0prr3fUnG5CtisUG7QeygW0w')]
---------- WebSearchAgent ----------
Here are the total points scored by Miami Heat players in the 2006-2007 season: Udonis Haslem: 844 points Dwayne Wade: 1397 points James Posey: 550 points ...
---------- PlanningAgent ----------
Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring 1397 points. Next, we need to find Dwyane Wade's total rebounds for the 2007-2008 and 2008-2009 seasons:
2. **WebSearchAgent**: Find Dwyane Wade's total rebounds for the 2007-2008 season.
3. **WebSearchAgent**: Find Dwyane Wade's total rebounds for the 2008-2009 season.
```


```
---------- UserProxyAgent ----------
approve
---------- WebSearchAgent ----------
[FunctionCall(id='call_fBZe80NaBfruOVGwRWbhXyRm', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 NBA season"}', name='search_web_tool'), FunctionCall(id='call_cURYibna4fGxySiL7IYt0c3s', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 NBA season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_fBZe80NaBfruOVGwRWbhXyRm'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_cURYibna4fGxySiL7IYt0c3s')]
---------- WebSearchAgent ----------
The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214. The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
---------- PlanningAgent ----------
Now that we have Dwyane Wade's total rebounds for both seasons, we can calculate the percentage change:
4. **DataAnalystAgent**: Calculate the percentage change in Dwyane Wade's total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds).
---------- UserProxyAgent ----------
approve
---------- DataAnalystAgent ----------
[FunctionCall(id='call_z3uog7t2x0z1Suzl5hACF9hY', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
---------- DataAnalystAgent ----------
[FunctionExecutionResult(content='85.98130841121495', call_id='call_z3uog7t2x0z1Suzl5hACF9hY')]
---------- DataAnalystAgent ----------
85.98130841121495
---------- PlanningAgent ----------
Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring 1397 points. His total rebounds increased from 214 in the 2007-2008 season to 398 in the 2008-2009 season, which is a percentage change of approximately 85.98%.
```


```
TERMINATE  TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?', type='TextMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=161, completion_tokens=166), content="To address the user's query, we will need to perform the following tasks:\n\n1. Identify the Miami Heat player with the highest points in the 2006-2007 season.\n2. Find the total rebounds for that player in the 2007-2008 season.\n3. Find the total rebounds for that player in the 2008-2009 season.\n4. Calculate the percentage change in the total rebounds between the 2007-2008 and 2008-2009 seasons.\n\nLet's assign these tasks:\n\n1. **WebSearchAgent**: Identify the Miami Heat player with the highest points in the 2006-2007 season.\n \n(Task 2 and 3 depend on the result of Task 1.
```


```
We'll proceed with Tasks 2 and 3 once Task 1 is complete.)", type='TextMessage'), UserInputRequestedEvent(source='UserProxyAgent', models_usage=None, request_id='2a433f88-f886-4b39-a078-ea1acdcb2f9d', content='', type='UserInputRequestedEvent'), TextMessage(source='UserProxyAgent', models_usage=None, content='approve', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=323, completion_tokens=28), content=[FunctionCall(id='call_0prr3fUnG5CtisUG7QeygW0w', arguments='{"query":"Miami Heat highest points scorer 2006-2007 NBA season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', call_id='call_0prr3fUnG5CtisUG7QeygW0w')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=403, completion_tokens=112), content="Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring 1397 points.\n\nNext, we need to find Dwyane Wade's total rebounds for the 2007-2008 and 2008-2009 seasons:\n\n2. **WebSearchAgent**: Find Dwyane Wade's total rebounds for the 2007-2008 season.\n3.
```


```
**WebSearchAgent**: Find Dwyane Wade's total rebounds for the 2008-2009 season.", type='TextMessage'), UserInputRequestedEvent(source='UserProxyAgent', models_usage=None, request_id='23dd4570-2391-41e9-aeea-86598499792c', content='', type='UserInputRequestedEvent'), TextMessage(source='UserProxyAgent', models_usage=None, content='approve', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=543, completion_tokens=73), content=[FunctionCall(id='call_fBZe80NaBfruOVGwRWbhXyRm', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 NBA season"}', name='search_web_tool'), FunctionCall(id='call_cURYibna4fGxySiL7IYt0c3s', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 NBA season"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_fBZe80NaBfruOVGwRWbhXyRm'), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_cURYibna4fGxySiL7IYt0c3s')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.\nThe number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=586, completion_tokens=70), content="Now that we have Dwyane Wade's total rebounds for both seasons, we can calculate the percentage change:\n\n4.
```


```
**DataAnalystAgent**: Calculate the percentage change in Dwyane Wade's total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds).", type='TextMessage'), UserInputRequestedEvent(source='UserProxyAgent', models_usage=None, request_id='e849d193-4ab3-4558-8560-7dbc062a0aee', content='', type='UserInputRequestedEvent'), TextMessage(source='UserProxyAgent', models_usage=None, content='approve', type='TextMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=655, completion_tokens=21), content=[FunctionCall(id='call_z3uog7t2x0z1Suzl5hACF9hY', arguments='{"start":214,"end":398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, content=[FunctionExecutionResult(content='85.98130841121495', call_id='call_z3uog7t2x0z1Suzl5hACF9hY')], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='PlanningAgent', models_usage=RequestUsage(prompt_tokens=687, completion_tokens=74), content='Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring 1397 points. His total rebounds increased from 214 in the 2007-2008 season to 398 in the 2008-2009 season, which is a percentage change of approximately 85.98%.\n\nTERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
```


With the integration of `UserProxyAgent`, the user's feedback is now seamlessly woven into the conversation flow. This enables the user to actively approve or reject the planning agent's decisions, ensuring direct human oversight and control.

### Using Reasoning Models

Throughout the preceding examples, we primarily utilized the `gpt-4o` model. Models such as `gpt-4o` and `gemini-1.5-flash` are highly adept at following instructions, allowing for relatively detailed directives within the team's selector prompt and the system messages of individual agents to guide their behavior.

However, when employing a reasoning model like `o3-mini`, a different approach is necessary. It is crucial to keep the selector prompt and system messages as concise and direct as possible. This is because reasoning models inherently excel at formulating their own instructions, given sufficient contextual information.

Consequently, with reasoning models, the need for a dedicated planning agent to explicitly break down tasks is often obviated, as the `SelectorGroupChat` itself, when powered by a reasoning model, can perform this planning autonomously.

In the subsequent example, we will demonstrate this by using `o3-mini` as the model for both the agents and the team. Notably, we will intentionally omit a planning agent and maintain the selector prompt and system messages with minimal instructions.

```python
model_client = OpenAIChatCompletionClient(model="o3-mini")

web_search_agent = AssistantAgent(
    "WebSearchAgent",
    description="An agent for searching information on the web.",
    tools=[search_web_tool],
    model_client=model_client,
    system_message="""Use web search tool to find information.""",
)

data_analyst_agent = AssistantAgent(
    "DataAnalystAgent",
    description="An agent for performing calculations.",
    model_client=model_client,
    tools=[percentage_change_tool],
    system_message="""Use tool to perform calculation. If you have not seen the data, ask for it.""",
)

user_proxy_agent = UserProxyAgent(
    "UserProxyAgent",
    description="A user to approve or disapprove tasks.",
)

selector_prompt = """Select an agent to perform task.
{roles}
Current conversation context:
{history}
Read the above conversation, then select an agent from  {participants}  to perform the next task.
When the task is complete, let the user approve or disapprove the task.
"""

team = SelectorGroupChat(
    [web_search_agent, data_analyst_agent, user_proxy_agent],
    model_client=model_client,
    termination_condition=termination,  # Use the same termination condition as before.
    selector_prompt=selector_prompt,
    allow_repeated_speaker=True,
)

await Console(team.run_stream(task=task))
```

Output:

```
---------- user ----------
Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
---------- WebSearchAgent ----------
[FunctionCall(id='call_hl7EP6Lp5jj5wEdxeNHTwUVG', arguments='{"query": "Who was the Miami Heat player with the highest points in the 2006-2007 season Miami Heat statistics Dwyane Wade rebounds percentage change 2007-2008 2008-2009 seasons"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', call_id='call_hl7EP6Lp5jj5wEdxeNHTwUVG', is_error=False)]
---------- WebSearchAgent
```


```
---------- Here are the total points scored by Miami Heat players in the 2006-2007 season: Udonis Haslem: 844 points Dwayne Wade: 1397 points James Posey: 550 points ...
---------- DataAnalystAgent ----------
I found that in the 2006–2007 season the player with the highest points was Dwyane Wade (with 1,397 points). Could you please provide Dwyane Wade’s total rebounds for the 2007–2008 and the 2008–2009 seasons so I can calculate the percentage change?
---------- WebSearchAgent ----------
[FunctionCall(id='call_lppGTILXDvO9waPwKO66ehK6', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 and 2008-2009 seasons for Miami Heat"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_lppGTILXDvO9waPwKO66ehK6', is_error=False)]
---------- WebSearchAgent ----------
The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.
---------- DataAnalystAgent ----------
Could you please provide Dwyane Wade’s total rebounds in the 2008-2009 season?
---------- WebSearchAgent ----------
[FunctionCall(id='call_r8DBcbJtQfdtugLtyTrqOvoK', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season Miami Heat"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_r8DBcbJtQfdtugLtyTrqOvoK', is_error=False)]
---------- WebSearchAgent ----------
The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
---------- DataAnalystAgent ----------
[FunctionCall(id='call_4jejv1wM7V1osbBCxJze8aQM', arguments='{"start": 214, "end": 398}', name='percentage_change_tool')]
---------- DataAnalystAgent ----------
[FunctionExecutionResult(content='85.98130841121495', call_id='call_4jejv1wM7V1osbBCxJze8aQM', is_error=False)]
---------- DataAnalystAgent ----------
85.98130841121495
---------- DataAnalystAgent ----------
Dwyane Wade was the Miami Heat player with the highest total points (1,397) during the 2006-2007 season. His total rebounds increased by approximately 86% from 214 in the 2
```


```
007-2008 season to 398 in the 2008-2009 season.
---------- UserProxyAgent ----------
Approve. TERMINATE
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=103, completion_tokens=384), content=[FunctionCall(id='call_hl7EP6Lp5jj5wEdxeNHTwUVG', arguments='{"query": "Who was the Miami Heat player with the highest points in the 2006-2007 season Miami Heat statistics Dwyane Wade rebounds percentage change 2007-2008 2008-2009 seasons"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', call_id='call_hl7EP6Lp5jj5wEdxeNHTwUVG', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', type='ToolCallSummaryMessage'), TextMessage(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=183, completion_tokens=1038), content='I found that in the 2006–2007 season the player with the highest points was Dwyane Wade (with 1,397 points). Could you please provide Dwyane Wade’s total rebounds for the 2007–2008 and the 2008–2009 seasons so I can calculate the percentage change?', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=299, completion_tokens=109), content=[FunctionCall(id='call_lppGTILXDvO9waPwKO66ehK6', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 and 2008-2009 seasons for Miami Heat"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, conte
```


```
nt=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', call_id='call_lppGTILXDvO9waPwKO66ehK6', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', type='ToolCallSummaryMessage'), TextMessage(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=291, completion_tokens=224), content='Could you please provide Dwyane Wade’s total rebounds in the 2008-2009 season?', type='TextMessage'), ToolCallRequestEvent(source='WebSearchAgent', models_usage=RequestUsage(prompt_tokens=401, completion_tokens=37), content=[FunctionCall(id='call_r8DBcbJtQfdtugLtyTrqOvoK', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season Miami Heat"}', name='search_web_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='WebSearchAgent', models_usage=None, content=[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', call_id='call_r8DBcbJtQfdtugLtyTrqOvoK', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='WebSearchAgent', models_usage=None, content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', type='ToolCallSummaryMessage'), ToolCallRequestEvent(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=353, completion_tokens=158), content=[FunctionCall(id='call_4jejv1wM7V1osbBCxJze8aQM', arguments='{"start": 214, "end": 398}', name='percentage_change_tool')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='DataAnalystAgent', models_usage=None, content=[FunctionExecutionResult(content='85.98130841121495', call_id='call_4jejv1wM7V1osbBCxJze8aQM', is_error=False)], type='ToolCallExecutionEvent'), ToolCallSummaryMessage(source='DataAnalystAgent', models_usage=None, content='85.98130841121495', type='ToolCallSummaryMessage'), TextMessage(source='DataAnalystAgent', models_usage=RequestUsage(prompt_tokens=394, completion_tokens=138), content='Dwyane Wade was the Miami Heat player with the highest total points (1,
```


```
397) during the 2006-2007 season. His total rebounds increased by approximately 86% from 214 in the 2007-2008 season to 398 in the 2008-2009 season.', type='TextMessage'), UserInputRequestedEvent(source='UserProxyAgent', models_usage=None, request_id='b3b05408-73fc-47d4-b832-16c9f447cd6e', content='', type='UserInputRequestedEvent'), TextMessage(source='UserProxyAgent', models_usage=None, content='Approve. TERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
```


**Tip:** For comprehensive guidance on effectively prompting reasoning models, it is recommended to consult the Azure AI Services Blog, specifically the section on "Prompt Engineering for OpenAI’s O1 and O3-mini Reasoning Models".