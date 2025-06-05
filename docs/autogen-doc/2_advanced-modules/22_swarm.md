### Swarm
Swarm implements a team in which agents can hand off tasks to other agents based on their capabilities. It is a multi-agent design pattern first introduced by OpenAI in Swarm. The key idea is to let agents delegate tasks to other agents using a special tool call, while all agents share the same message context. This enables agents to make local decisions about task planning, rather than relying on a central orchestrator such as in SelectorGroupChat.

Note
Swarm is a high-level API. If more control and customization are required and not supported by this API, the Handoff Pattern in the Core API documentation can be consulted to implement a custom version of the Swarm pattern.

#### How Does It Work?
At its core, the Swarm team functions as a group chat where agents take turns generating responses. Similar to `SelectorGroupChat` and `RoundRobinGroupChat`, participant agents broadcast their responses, ensuring all agents share the same message context.

A key differentiator from these other group chat teams is that, at each turn, the speaker agent is selected based on the most recent `HandoffMessage` within the context. This inherent design requires each agent in the team to be capable of generating `HandoffMessage` instances to signal which other agents it intends to hand off to.

For an `AssistantAgent`, the `handoffs` argument can be configured to specify which agents it is permitted to hand off to. The `Handoff` mechanism can be employed to customize both the message content and the handoff behavior.

The overall process can be summarized as follows:
*   Each agent possesses the capability to generate a `HandoffMessage` to indicate target agents for task handoff. For an `AssistantAgent`, this functionality is enabled by setting the `handoffs` argument.
*   Upon initiation of a task by the team, the initial speaker agents operate on the task and make localized decisions regarding whether to hand off and to whom.
*   When an agent generates a `HandoffMessage`, the designated receiving agent assumes the task with the same shared message context.
*   This iterative process continues until a predefined termination condition is satisfied.

Note
The `AssistantAgent` leverages the tool calling capability of the underlying model to generate handoffs. Consequently, the model in use must support tool calling. If the model is configured for parallel tool calling, multiple handoffs may be generated simultaneously, which could lead to unexpected behavior. To mitigate this, parallel tool calling can be disabled by configuring the model client. For `OpenAIChatCompletionClient` and `AzureOpenAIChatCompletionClient`, this can be achieved by setting `parallel_tool_calls=False` in their respective configurations.

In this section, two examples illustrating the utilization of the Swarm team are provided:
*   A customer support team incorporating human-in-the-loop handoff.
*   An autonomous team designed for content generation.

#### Customer Support Example
This system demonstrates a flight refund scenario involving two distinct agents:
*   **Travel Agent**: Responsible for handling general travel inquiries and coordinating refunds.
*   **Flights Refunder**: Specializes in processing flight refunds utilizing the `refund_flight` tool.

Additionally, the system is designed to allow user interaction, specifically when agents hand off the task to the "user".

##### Workflow
The workflow proceeds as follows:
*   The **Travel Agent** initiates the conversation and evaluates the user's request.
*   Based on the request:
    *   For refund-related tasks, the Travel Agent hands off the responsibility to the **Flights Refunder**.
    *   For information required from the customer, either agent has the capability to hand off to the "user".
*   The **Flights Refunder** processes refunds by invoking the `refund_flight` tool when appropriate.
*   Should an agent hand off to the "user", the team execution pauses, awaiting user input.
*   Once the user provides input, it is transmitted back to the team as a `HandoffMessage`. This message is specifically directed back to the agent that originally requested the user's input.
*   This iterative process continues until the Travel Agent determines that the task is complete and subsequently terminates the workflow.

```python
from typing import Any, Dict, List
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
```

##### Tools
```python
def refund_flight(flight_id: str) -> str:
    """Refund a flight"""
    return f"Flight {flight_id} refunded"
```

##### Agents
```python
model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

travel_agent = AssistantAgent(
    "travel_agent",
    model_client=model_client,
    handoffs=["flights_refunder", "user"],
    system_message="""You are a travel agent.
    The flights_refunder is in charge of refunding flights.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Use TERMINATE when the travel planning is complete.""" ,
)

flights_refunder = AssistantAgent(
    "flights_refunder",
    model_client=model_client,
    handoffs=["travel_agent", "user"],
    tools=[refund_flight],
    system_message="""You are an agent specialized in refunding flights.
    You only need flight reference numbers to refund a flight.
    You have the ability to refund a flight using the refund_flight tool.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    When the transaction is complete, handoff to the travel agent to finalize.""" ,
)

termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")

team = Swarm([travel_agent, flights_refunder], termination_condition=termination)

task = "I need to refund my flight."

async def run_team_stream() -> None:
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]
    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = input("User: ")
        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]
    # Use asyncio.run(...) if you are running this in a script.
    await run_team_stream()
    await model_client.close()
```

```
---------- user ---------- I need to refund my flight.
---------- travel_agent ---------- [FunctionCall(id='call_ZQ2rGjq4Z29pd0yP2sNcuyd2', arguments='{}', name='transfer_to_flights_refunder')] [Prompt tokens: 119, Completion tokens: 14]
---------- travel_agent ---------- [FunctionExecutionResult(content='Transferred to flights_refunder, adopting the role of flights_refunder immediately.', call_id='call_ZQ2rGjq4Z29pd0yP2sNcuyd2')]
---------- travel_agent ---------- Transferred to flights_refunder, adopting the role of flights_refunder immediately.
---------- flights_refunder ---------- Could you please provide me with the flight reference number so I can process the refund for you? [Prompt tokens: 191, Completion tokens: 20]
---------- flights_refunder ---------- [FunctionCall(id='call_1iRfzNpxTJhRTW2ww9aQJ8sK', arguments='{}', name='transfer_to_user')] [Prompt tokens: 219, Completion tokens: 11]
---------- flights_refunder ---------- [FunctionExecutionResult(content='Transferred to user, adopting the role of user immediately.', call_id='call_1iRfzNpxTJhRTW2ww9aQJ8sK')]
---------- flights_refunder ---------- Transferred to user, adopting the role of user immediately.
---------- Summary ----------
Number of messages: 8
Finish reason: Handoff to user from flights_refunder detected.
Total prompt tokens: 529
Total completion tokens: 45
Duration: 2.05 seconds
---------- user ---------- Sure, it's 507811
---------- flights_refunder ---------- [FunctionCall(id='call_UKCsoEBdflkvpuT9Bi2xlvTd', arguments='{"flight_id":"507811"}', name='refund_flight')] [Prompt tokens: 266, Completion tokens: 18]
---------- flights_refunder ---------- [FunctionExecutionResult(content='Flight 507811 refunded', call_id='call_UKCsoEBdflkvpuT9Bi2xlvTd')]
---------- flights_refunder ---------- Tool calls: refund_flight({"flight_id":"507811"}) = Flight 507811 refunded
---------- flights_refunder ---------- [FunctionCall(id='call_MQ2CXR8UhVtjNc6jG3wSQp2W', arguments='{}', name='transfer_to_travel_agent')] [Prompt tokens: 303, Completion tokens: 13]
---------- flights_refunder ---------- [FunctionExecutionResult(content='Transferred to travel_agent, adopting the role of travel_agent immediately.', call_id='call_MQ2CXR8UhVtjNc6jG3wSQp2W')]
---------- flights_refunder ---------- Transferred to travel_agent, adopting the role of travel_agent immediately.
---------- travel_agent ---------- Your flight with reference number 507811 has been successfully refunded. If you need anything else, feel free to let me know. Safe travels! TERMINATE [Prompt tokens: 272, Completion tokens: 32]
---------- Summary ----------
Number of messages: 8
Finish reason: Text 'TERMINATE' mentioned
Total prompt tokens: 841
Total completion tokens: 63
Duration: 1.64 seconds
```

#### Stock Research Example
This system is engineered to execute stock research tasks by leveraging the capabilities of four distinct agents:
*   **Planner**: Acts as the central coordinator, delegating specific tasks to specialized agents based on their expertise. The planner is responsible for ensuring efficient utilization of each agent and overseeing the entirety of the workflow.
*   **Financial Analyst**: A specialized agent whose primary role is to analyze financial metrics and stock data, utilizing tools such as `get_stock_data`.
*   **News Analyst**: An agent focused on the collection and summarization of recent news articles pertinent to the stock, employing tools such as `get_news`.
*   **Writer**: An agent assigned the task of compiling the gathered findings from both stock and news analyses into a cohesive final report.

##### Workflow
The research process workflow is systematically structured as follows:
*   The **Planner** initiates the research process by delegating tasks to the appropriate agents in a step-by-step manner.
*   Each agent performs its assigned task autonomously and appends its work to the shared **message thread/history**. Rather than directly transmitting results back to the planner, all agents contribute to and retrieve information from this shared message history. When agents generate their work using the Large Language Model (LLM), they have access to this shared message history, which provides essential context and facilitates the tracking of the overall task's progress.
*   Upon completion of its task, an agent hands off control back to the planner.
*   This process persists until the planner ascertains that all requisite tasks have been successfully completed and subsequently decides to terminate the workflow.

##### Tools

```python
async def get_stock_data(symbol: str) -> Dict[str, Any]:
    """Get stock market data for a given symbol"""
    return {"price": 180.25, "volume": 1000000, "pe_ratio": 65.4, "market_cap": "700B"}

async def get_news(query: str) -> List[Dict[str, str]]:
    """Get recent news articles about a company"""
    return [
        {
            "title": "Tesla Expands Cybertruck Production",
            "date": "2024-03-20",
            "summary": "Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand." ,
        },
        {
            "title": "Tesla FSD Beta Shows Promise",
            "date": "2024-03-19",
            "summary": "Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features." ,
        },
        {
            "title": "Model Y Dominates Global EV Sales",
            "date": "2024-03-18",
            "summary": "Tesla's Model Y becomes best-selling electric vehicle worldwide, capturing significant market share." ,
        },
    ]

model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

planner = AssistantAgent(
    "planner",
    model_client=model_client,
    handoffs=["financial_analyst", "news_analyst", "writer"],
    system_message="""You are a research planning coordinator.
    Coordinate market research by delegating to specialized agents:
    - Financial Analyst: For stock data analysis
    - News Analyst: For news gathering and analysis
    - Writer: For compiling final report
    Always send your plan first, then handoff to appropriate agent.
    Always handoff to a single agent at a time.
    Use TERMINATE when research is complete.""" ,
)

financial_analyst = AssistantAgent(
    "financial_analyst",
    model_client=model_client,
    handoffs=["planner"],
    tools=[get_stock_data],
    system_message="""You are a financial analyst.
    Analyze stock market data using the get_stock_data tool.
    Provide insights on financial metrics.
    Always handoff back to planner when analysis is complete.""" ,
)

news_analyst = AssistantAgent(
    "news_analyst",
    model_client=model_client,
    handoffs=["planner"],
    tools=[get_news],
    system_message="""You are a news analyst.
    Gather and analyze relevant news using the get_news tool.
    Summarize key market insights from news.
    Always handoff back to planner when analysis is complete.""" ,
)

writer = AssistantAgent(
    "writer",
    model_client=model_client,
    handoffs=["planner"],
    system_message="""You are a financial report writer.
    Compile research findings into clear, concise reports.
    Always handoff back to planner when writing is complete.""" ,
)

# Define termination condition
text_termination = TextMentionTermination("TERMINATE")
termination = text_termination

research_team = Swarm(
    participants=[planner, financial_analyst, news_analyst, writer],
    termination_condition=termination
)

task = "Conduct market research for TSLA stock"

await Console(research_team.run_stream(task=task))
await model_client.close()
```

```
---------- user ---------- Conduct market research for TSLA stock
---------- planner ---------- [FunctionCall(id='call_BX5QaRuhmB8CxTsBlqCUIXPb', arguments='{}', name='transfer_to_financial_analyst')] [Prompt tokens: 169, Completion tokens: 166]
---------- planner ---------- [FunctionExecutionResult(content='Transferred to financial_analyst, adopting the role of financial_analyst immediately.', call_id='call_BX5QaRuhmB8CxTsBlqCUIXPb')]
---------- planner ---------- Transferred to financial_analyst, adopting the role of financial_analyst immediately.
---------- financial_analyst ---------- [FunctionCall(id='call_SAXy1ebtA9mnaZo4ztpD2xHA', arguments='{"symbol":"TSLA"}', name='get_stock_data')] [Prompt tokens: 136, Completion tokens: 16]
---------- financial_analyst ---------- [FunctionExecutionResult(content="{'price': 180.25, 'volume': 1000000, 'pe_ratio': 65.4, 'market_cap': '700B'}", call_id='call_SAXy1ebtA9mnaZo4ztpD2xHA')]
---------- financial_analyst ---------- Tool calls: get_stock_data({"symbol":"TSLA"}) = {'price': 180.25, 'volume': 1000000, 'pe_ratio': 65.4, 'market_cap': '700B'}
---------- financial_analyst ---------- [FunctionCall(id='call_IsdcFUfBVmtcVzfSuwQpeAwl', arguments='{}', name='transfer_to_planner')] [Prompt tokens: 199, Completion tokens: 337]
---------- financial_analyst ---------- [FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_IsdcFUfBVmtcVzfSuwQpeAwl')]
---------- financial_analyst ---------- Transferred to planner, adopting the role of planner immediately.
---------- planner ---------- [FunctionCall(id='call_tN5goNFahrdcSfKnQqT0RONN', arguments='{}', name='transfer_to_news_analyst')] [Prompt tokens: 291, Completion tokens: 14]
---------- planner ---------- [FunctionExecutionResult(content='Transferred to news_analyst, adopting the role of news_analyst immediately.', call_id='call_tN5goNFahrdcSfKnQqT0RONN')]
---------- planner ---------- Transferred to news_analyst, adopting the role of news_analyst immediately.
---------- news_analyst ---------- [FunctionCall(id='call_Owjw6ZbiPdJgNWMHWxhCKgsp', arguments='{"query":"Tesla market news"}', name='get_news')] [Prompt tokens: 235, Completion tokens: 16]
---------- news_analyst ---------- [FunctionExecutionResult(content='[{\'title\': \'Tesla Expands Cybertruck Production\', \'date\': \'2024-03-20\', \'summary\': \'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.\'}, {\'title\': \'Tesla FSD Beta Shows Promise\', \'date\': \'2024-03-19\', \'summary\': \'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.\'}, {\'title\': \'Model Y Dominates Global EV Sales\', \'date\': \'2024-03-18\', \'summary\': "Tesla\'s Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]', call_id='call_Owjw6ZbiPdJgNWMHWxhCKgsp')]
---------- news_analyst ---------- Tool calls: get_news({"query":"Tesla market news"}) = [{'title': 'Tesla Expands Cybertruck Production', 'date': '2024-03-20', 'summary': 'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.'}, {'title': 'Tesla FSD Beta Shows Promise', 'date': '2024-03-19', 'summary': 'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.'}, {'title': 'Model Y Dominates Global EV Sales', 'date': '2024-03-18', 'summary': "Tesla's Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]
---------- news_analyst ---------- Here are some of the key market insights regarding Tesla (TSLA):

1.  **Expansion in Cybertruck Production**: Tesla has increased its Cybertruck production capacity at the Gigafactory in Texas to meet the high demand. This move might positively impact Tesla's revenues if the demand for the Cybertruck continues to grow.

2.  **Advancements in Full Self-Driving (FSD) Technology**: The recent beta release of Tesla's Full Self-Driving software shows significant advancements, particularly in urban navigation and safety. Progress in this area could enhance Tesla's competitive edge in the autonomous driving sector.

3.  **Dominance of Model Y in EV Sales**: Tesla's Model Y has become the best-selling electric vehicle globally, capturing a substantial market share. Such strong sales performance reinforces Tesla's leadership in the electric vehicle market.

These developments reflect Tesla's ongoing innovation and ability to capture market demand, which could positively influence its stock performance and market position.

I will now hand off back to the planner. [Prompt tokens: 398, Completion tokens: 203]
---------- news_analyst ---------- [FunctionCall(id='call_pn7y6PKsBspWA17uOh3AKNMT', arguments='{}', name='transfer_to_planner')] [Prompt tokens: 609, Completion tokens: 12]
---------- news_analyst ---------- [FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_pn7y6PKsBspWA17uOh3AKNMT')]
---------- news_analyst ---------- Transferred to planner, adopting the role of planner immediately.
---------- planner ---------- [FunctionCall(id='call_MmXyWuD2uJT64ZdVI5NfhYdX', arguments='{}', name='transfer_to_writer')] [Prompt tokens: 722, Completion tokens: 11]
---------- planner ---------- [FunctionExecutionResult(content='Transferred to writer, adopting the role of writer immediately.', call_id='call_MmXyWuD2uJT64ZdVI5NfhYdX')]
---------- planner ---------- Transferred to writer, adopting the role of writer immediately.
---------- writer ---------- [FunctionCall(id='call_Pdgu39O6GMYplBiB8jp3uyN3', arguments='{}', name='transfer_to_planner')] [Prompt tokens: 599, Completion tokens: 323]
---------- writer ---------- [FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_Pdgu39O6GMYplBiB8jp3uyN3')]
---------- writer ---------- Transferred to planner, adopting the role of planner immediately.
---------- planner ---------- TERMINATE [Prompt tokens: 772, Completion tokens: 4]
---------- Summary ----------
Number of messages: 27
Finish reason: Text 'TERMINATE' mentioned
Total prompt tokens: 4130
Total completion tokens: 1102
Duration: 17.74 seconds
TaskResult(messages=[TextMessage(source='user', models_usage=None, content='Conduct market research for TSLA stock', type='TextMessage'), ToolCallRequestEvent(source='planner', models_usage=RequestUsage(prompt_tokens=169, completion_tokens=166), content=[FunctionCall(id='call_BX5QaRuhmB8CxTsBlqCUIXPb', arguments='{}', name='transfer_to_financial_analyst')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='planner', models_usage=None, content=[FunctionExecutionResult(content='Transferred to financial_analyst, adopting the role of financial_analyst immediately.', call_id='call_BX5QaRuhmB8CxTsBlqCUIXPb')], type='ToolCallExecutionEvent'), HandoffMessage(source='planner', models_usage=None, target='financial_analyst', content='Transferred to financial_analyst, adopting the role of financial_analyst immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='financial_analyst', models_usage=RequestUsage(prompt_tokens=136, completion_tokens=16), content=[FunctionCall(id='call_SAXy1ebtA9mnaZo4ztpD2xHA', arguments='{"symbol":"TSLA"}', name='get_stock_data')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='financial_analyst', models_usage=None, content=[FunctionExecutionResult(content="{'price': 180.25, 'volume': 1000000, 'pe_ratio': 65.4, 'market_cap': '700B'}", call_id='call_SAXy1ebtA9mnaZo4ztpD2xHA')], type='ToolCallExecutionEvent'), TextMessage(source='financial_analyst', models_usage=None, content='Tool calls:\nget_stock_data({"symbol":"TSLA"}) = {\'price\': 180.25, \'volume\': 1000000, \'pe_ratio\': 65.4, \'market_cap\': \'700B\'}', type='TextMessage'), ToolCallRequestEvent(source='financial_analyst', models_usage=RequestUsage(prompt_tokens=199, completion_tokens=337), content=[FunctionCall(id='call_IsdcFUfBVmtcVzfSuwQpeAwl', arguments='{}', name='transfer_to_planner')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='financial_analyst', models_usage=None, content=[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_IsdcFUfBVmtcVzfSuwQpeAwl')], type='ToolCallExecutionEvent'), HandoffMessage(source='financial_analyst', models_usage=None, target='planner', content='Transferred to planner, adopting the role of planner immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='planner', models_usage=RequestUsage(prompt_tokens=291, completion_tokens=14), content=[FunctionCall(id='call_tN5goNFahrdcSfKnQqT0RONN', arguments='{}', name='transfer_to_news_analyst')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='planner', models_usage=None, content=[FunctionExecutionResult(content='Transferred to news_analyst, adopting the role of news_analyst immediately.', call_id='call_tN5goNFahrdcSfKnQqT0RONN')], type='ToolCallExecutionEvent'), HandoffMessage(source='planner', models_usage=None, target='news_analyst', content='Transferred to news_analyst, adopting the role of news_analyst immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='news_analyst', models_usage=RequestUsage(prompt_tokens=235, completion_tokens=16), content=[FunctionCall(id='call_Owjw6ZbiPdJgNWMHWxhCKgsp', arguments='{"query":"Tesla market news"}', name='get_news')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='news_analyst', models_usage=None, content=[FunctionExecutionResult(content='[{\'title\': \'Tesla Expands Cybertruck Production\', \'date\': \'2024-03-20\', \'summary\': \'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.\'}, {\'title\': \'Tesla FSD Beta Shows Promise\', \'date\': \'2024-03-19\', \'summary\': \'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.\'}, {\'title\': \'Model Y Dominates Global EV Sales\', \'date\': \'2024-03-18\', \'summary\': "Tesla\'s Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]', call_id='call_Owjw6ZbiPdJgNWMHWxhCKgsp')], type='ToolCallExecutionEvent'), TextMessage(source='news_analyst', models_usage=None, content='Tool calls:\nget_news({"query":"Tesla market news"}) = [{\'title\': \'Tesla Expands Cybertruck Production\', \'date\': \'2024-03-20\', \'summary\': \'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.\'}, {\'title\': \'Tesla FSD Beta Shows Promise\', \'date\ \'2024-03-19\', \'summary\': \'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.\'}, {\'title\': \'Model Y Dominates Global EV Sales\', \'date\': \'2024-03-18\', \'summary\': "Tesla\'s Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]', type='TextMessage'), TextMessage(source='news_analyst', models_usage=RequestUsage(prompt_tokens=398, completion_tokens=203), content="Here are some of the key market insights regarding Tesla (TSLA):\n\n1. **Expansion in Cybertruck Production**: Tesla has increased its Cybertruck production capacity at the Gigafactory in Texas to meet the high demand. This move might positively impact Tesla's revenues if the demand for the Cybertruck continues to grow.\n\n2. **Advancements in Full Self-Driving (FSD) Technology**: The recent beta release of Tesla's Full Self-Driving software shows significant advancements, particularly in urban navigation and safety. Progress in this area could enhance Tesla's competitive edge in the autonomous driving sector.\n\n3. **Dominance of Model Y in EV Sales**: Tesla's Model Y has become the best-selling electric vehicle globally, capturing a substantial market share. Such strong sales performance reinforces Tesla's leadership in the electric vehicle market.\n\nThese developments reflect Tesla's ongoing innovation and ability to capture market demand, which could positively influence its stock performance and market position. \n\nI will now hand off back to the planner.", type='TextMessage'), ToolCallRequestEvent(source='news_analyst', models_usage=RequestUsage(prompt_tokens=609, completion_tokens=12), content=[FunctionCall(id='call_pn7y6PKsBspWA17uOh3AKNMT', arguments='{}', name='transfer_to_planner')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='news_analyst', models_usage=None, content=[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_pn7y6PKsBspWA17uOh3AKNMT')], type='ToolCallExecutionEvent'), HandoffMessage(source='news_analyst', models_usage=None, target='planner', content='Transferred to planner, adopting the role of planner immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='planner', models_usage=RequestUsage(prompt_tokens=722, completion_tokens=11), content=[FunctionCall(id='call_MmXyWuD2uJT64ZdVI5NfhYdX', arguments='{}', name='transfer_to_writer')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='planner', models_usage=None, content=[FunctionExecutionResult(content='Transferred to writer, adopting the role of writer immediately.', call_id='call_MmXyWuD2uJT64ZdVI5NfhYdX')], type='ToolCallExecutionEvent'), HandoffMessage(source='planner', models_usage=None, target='writer', content='Transferred to writer, adopting the role of writer immediately.', type='HandoffMessage'), ToolCallRequestEvent(source='writer', models_usage=RequestUsage(prompt_tokens=599, completion_tokens=323), content=[FunctionCall(id='call_Pdgu39O6GMYplBiB8jp3uyN3', arguments='{}', name='transfer_to_planner')], type='ToolCallRequestEvent'), ToolCallExecutionEvent(source='writer', models_usage=None, content=[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_Pdgu39O6GMYplBiB8jp3uyN3')], type='ToolCallExecutionEvent'), HandoffMessage(source='writer', models_usage=None, target='planner', content='Transferred to planner, adopting the role of planner immediately.', type='HandoffMessage'), TextMessage(source='planner', models_usage=RequestUsage(prompt_tokens=772, completion_tokens=4), content='TERMINATE', type='TextMessage')], stop_reason="Text 'TERMINATE' mentioned")
```
