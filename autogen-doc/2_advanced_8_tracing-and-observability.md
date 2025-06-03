
## Tracing and Observability

AutoGen incorporates built-in support for tracing and observability, facilitating the collection of comprehensive records pertaining to your application's execution. This feature is instrumental for debugging, performance analysis, and gaining insight into application flow. The capability is powered by the OpenTelemetry library, enabling the use of any OpenTelemetry-compatible backend for trace collection and analysis.

### Setup

To commence, the OpenTelemetry Python package must be installed via pip:

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
```


Once the SDK is installed, the most straightforward approach to setting up tracing in AutoGen involves these steps:
*   Configure an OpenTelemetry tracer provider.
*   Establish an exporter to dispatch traces to your chosen backend.
*   Connect the tracer provider to the AutoGen runtime.

### Telemetry Backend

To collect and visualize traces, a telemetry backend is required. Open-source options such as Jaeger and Zipkin are available. For demonstration purposes, Jaeger will be used as the telemetry backend.

For rapid setup, Jaeger can be run locally using Docker:

```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```


This command initiates a Jaeger instance that listens on port 16686 for the Jaeger UI and port 4317 for the OpenTelemetry collector. The Jaeger UI can be accessed at `http://localhost:16686`.

### Instrumenting an AgentChat Team

The following section demonstrates how to enable tracing with an AutoGen `GroupChat` team. The AutoGen core API runtime inherently supports OpenTelemetry, automatically logging message metadata. To begin, a tracing service will be established to instrument the AutoGen runtime.

The code for creating a team should be familiar. Notably, all AgentChat agents and teams execute using the AutoGen core API runtime. The runtime is pre-instrumented to log [runtime messaging events (metadata)](microsoft/autogen), encompassing:
*   `create`: When a message is created.
*   `send`: When a message is sent.
*   `publish`: When a message is published.
*   `receive`: When a message is received.
*   `intercept`: When a message is intercepted.
*   `process`: When a message is processed.
*   `ack`: When a message is acknowledged.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core import SingleThreadedAgentRuntime
from autogen_ext.models.openai import OpenAIChatCompletionClient
import opentelemetry.sdk.trace as trace_sdk
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

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

# Tracing setup
resource = Resource(attributes={"service.name": "autogen-agentchat-example"})
provider = trace_sdk.TracerProvider(resource=resource)
span_processor = SimpleSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317"))
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

async def main() -> None:
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

    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination

    selector_prompt = """Select an agent to perform task.
    {roles}
    Current conversation context:
    {history}
    Read the above conversation, then select an agent from {participants} to perform the next task.
    Make sure the planner agent has assigned tasks before other agents start working.
    Only select one agent.
    """

    task = "Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?"
    tracer = trace.get_tracer("autogen-test-agentchat")

    with tracer.start_as_current_span("runtime"):
        team = SelectorGroupChat(
            [planning_agent, web_search_agent, data_analyst_agent],
            model_client=model_client,
            termination_condition=termination,
            selector_prompt=selector_prompt,
            allow_repeated_speaker=True,
        )
        await Console(team.run_stream(task=task))
        await model_client.close()

# asyncio.run(main())
await main()
```

```
---------- user ----------
Who was the Miami Heat player with the highest points in the 2006-2007 season, and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?
---------- PlanningAgent ----------
To accomplish this, we can break down the tasks as follows:
1. WebSearchAgent: Search for the Miami Heat player with the highest points during the 2006-2007 NBA season.
2. WebSearchAgent: Find the total rebounds for the identified player in both the 2007-2008 and 2008-2009 NBA seasons.
3. DataAnalystAgent: Calculate the percentage change in total rebounds for the player between the 2007-2008 and 2008-2009 seasons.
Once these tasks are complete, I will summarize the findings.
---------- WebSearchAgent ----------
[FunctionCall(id='call_PUhxZyR0CTlWCY4uwd5Zh3WO', arguments='{"query":"Miami Heat highest points scorer 2006-2007 season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='Here are the total points scored by Miami Heat players in the 2006-2007 season:\n Udonis Haslem: 844 points\n Dwayne Wade: 1397 points\n James Posey: 550 points\n ...\n ', name='search_web_tool', call_id='call_PUhxZyR0CTlWCY4uwd5Zh3WO', is_error=False)]
---------- WebSearchAgent ----------
Here are the total points scored by Miami Heat players in the 2006-2007 season: Udonis Haslem: 844 points Dwayne Wade: 1397 points James Posey: 550 points ...
---------- WebSearchAgent ----------
Dwyane Wade was the Miami Heat player with the highest points in the 2006-2007 season, scoring 1,397 points. Now, let's find his total rebounds for the 2007-2008 and 2008-2009 NBA seasons.
---------- WebSearchAgent ----------
[FunctionCall(id='call_GL7KkWKj9ejIM8FfpgXe2dPk', arguments='{"query": "Dwyane Wade total rebounds 2007-2008 season"}', name='search_web_tool'), FunctionCall(id='call_X81huZoiA30zIjSAIDgb8ebe', arguments='{"query": "Dwyane Wade total rebounds 2008-2009 season"}', name='search_web_tool')]
---------- WebSearchAgent ----------
[FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214.', name='search_web_tool', call_id='call_GL7KkWKj9ejIM8FfpgXe2dPk', is_error=False), FunctionExecutionResult(content='The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.', name='search_web_tool', call_id='call_X81huZoiA30zIjSAIDgb8ebe', is_error=False)]
---------- WebSearchAgent ----------
The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214. The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398.
---------- DataAnalystAgent ----------
[FunctionCall(id='call_kB50RkFVqHptA7FOf0lL2RS8', arguments='{"start":214,"end":398}', name='percentage_change_tool')]
---------- DataAnalystAgent ----------
[FunctionExecutionResult(content='85.98130841121495', name='percentage_change_tool', call_id='call_kB50RkFVqHptA7FOf0lL2RS8', is_error=False)]
---------- DataAnalystAgent ----------
85.98130841121495
---------- PlanningAgent ----------
The Miami Heat player with the highest points during the 2006-2007 NBA season was Dwayne Wade, who scored 1,397 points. The percentage increase in his total rebounds from the 2007-2008 season (214 rebounds) to the 2008-2009 season (398 rebounds) was approximately 86%. TERMINATE
```


```python
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core import CancellationToken
import opentelemetry.sdk.trace as trace_sdk
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Tracing setup (if not already done)
resource = Resource(attributes={"service.name": "autogen-agentchat-round-robin-example"})
provider = trace_sdk.TracerProvider(resource=resource)
span_processor = SimpleSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317"))
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

async def run_agents() -> None:
    # Create an OpenAI model client.
    model_client = OpenAIChatCompletionClient(model="gpt-4o-2024-08-06")

    # Create the primary agent.
    primary_agent = AssistantAgent(
        "primary_agent",
        model_client=model_client,
        system_message="You are a helpful AI assistant.",
    )

    # Create the critic agent.
    critic_agent = AssistantAgent(
        "critic_agent",
        model_client=model_client,
        system_message="Provide constructive feedback. Respond with 'APPROVE' to when your feedbacks are addressed.",
    )

    # Define a termination condition that stops the task if the critic approves.
    text_termination = TextMentionTermination("APPROVE")

    tracer = trace.get_tracer("autogen-test-agentchat")

    with tracer.start_as_current_span("runtime_round_robin_events"):
        team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)
        response_stream = team.run_stream(task="Write a 2 line haiku about the fall season")

        # Asynchronous iteration over the stream
        async for response in response_stream:
            # Check if the response is a TaskResult (final result of the run)
            if not isinstance(response, TaskResult):
                # Print the agent's message
                print(f"\n-- {response.source} -- : {response.to_text()}")
                # Add span for agent messages
                with tracer.start_as_current_span(f"agent_message.{response.source}") as message_span:
                    message_span.set_attribute("agent.name", response.source)
                    message_span.set_attribute("message.content", response.to_text())
                # Original print for direct console output
                print(f"{response.source}: {response.to_text()}")

    await model_client.close()

await run_agents()
```

```
-- primary_agent -- : Leaves cascade like gold, Whispering winds cool the earth.
primary_agent: Leaves cascade like gold, Whispering winds cool the earth.
-- critic_agent -- : Your haiku beautifully captures the essence of the fall season with vivid imagery. However, it appears to have six syllables in the second line, which should traditionally be five. Here's a revised version keeping the 5-7-5 syllable structure: Leaves cascade like gold, Whispering winds cool the air. Please adjust the second line to reflect a five-syllable count. Thank you!
critic_agent: Your haiku beautifully captures the essence of the fall season with vivid imagery. However, it appears to have six syllables in the second line, which should traditionally be five. Here's a revised version keeping the 5-7-5 syllable structure: Leaves cascade like gold, Whispering winds cool the air. Please adjust the second line to reflect a five-syllable count. Thank you!
-- primary_agent -- : Leaves cascade like gold, Whispering winds cool the air.
primary_agent: Leaves cascade like gold, Whispering winds cool the air.
-- critic_agent -- : APPROVE
critic_agent: APPROVE
```
