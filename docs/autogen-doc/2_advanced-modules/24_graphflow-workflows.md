# GraphFlow (Workflows)

In this section, you'll learn how to create a *multi-agent workflow* using GraphFlow, or simply "flow" for short. It uses structured execution and precisely controls how agents interact to accomplish a task.

We'll first show you how to create and run a flow. We'll then explain how to observe and debug flow behavior, and discuss important operations for managing execution.

AutoGen AgentChat provides a team for directed graph execution:

**GraphFlow:** A team that follows a DiGraph to control the execution flow between agents. Supports sequential, parallel, conditional, and looping behaviors.

**Note**
When should you use GraphFlow **?**
Use Graph when you need strict control over the order in which agents act, or when different outcomes must lead to different next steps. Start with a simple team such as `RoundRobinGroupChat` or `SelectorGroupChat` if ad-hoc conversation flow is sufficient. Transition to a structured workflow when your task requires deterministic control, conditional branching, or handling complex multi-step processes with cycles.

**Warning:** GraphFlow is an **experimental feature**. Its API, behavior, and capabilities are **subject to change** in future releases.

## Creating and Running a Flow

`DiGraphBuilder` is a fluent utility that lets you easily construct execution graphs for workflows. It supports building:

*   Sequential chains
*   Parallel fan-outs
*   Conditional branching
*   Loops with safe exit conditions

Each node in the graph represents an agent, and edges define the allowed execution paths. Edges can optionally have conditions based on agent messages.

### Sequential Flow

We will begin by creating a simple workflow where a **writer** drafts a paragraph and a **reviewer** provides feedback. This graph terminates after the reviewer comments on the writer.

**Note**
The flow automatically computes all the source and leaf nodes of the graph, and the execution starts at all the source nodes in the graph and completes execution when no nodes are left to execute.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Create an OpenAI model client
client = OpenAIChatCompletionClient(model="gpt-4.1-nano")

# Create the writer agent
writer = AssistantAgent(
    "writer", model_client=client, system_message="Draft a short paragraph on climate change."
)

# Create the reviewer agent
reviewer = AssistantAgent(
    "reviewer", model_client=client, system_message="Review the draft and suggest improvements."
)

# Build the graph
builder = DiGraphBuilder()
builder.add_node(writer).add_node(reviewer)
builder.add_edge(writer, reviewer)

# Build and validate the graph
graph = builder.build()

# Create the flow
flow = GraphFlow([writer, reviewer], graph=graph)

# Use `asyncio.run(...)` and wrap the below in a async function when running in a script.
stream = flow.run_stream(task="Write a short paragraph about climate change.")
async for event in stream:
    # type: ignore
    print(event)
# Use Console(flow.run_stream(...)) for better formatting in console.
```

```
source='user' models_usage=None metadata={} content='Write a short paragraph about climate change.' type='TextMessage'
source='writer' models_usage=RequestUsage(prompt_tokens=28, completion_tokens=95) metadata={} content='Climate change refers to long-term shifts in temperature, precipitation, and other atmospheric patterns, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These changes contribute to rising global temperatures, melting ice caps, more frequent and severe weather events, and adverse impacts on ecosystems and human communities. Addressing climate change requires global cooperation to reduce greenhouse gas emissions, transition to renewable energy sources, and implement sustainable practices to protect the planet for future generations.' type='TextMessage'
source='reviewer' models_usage=RequestUsage(prompt_tokens=127, completion_tokens=144) metadata={} content="The paragraph provides a clear overview of climate change, its causes, and its impacts. To enhance clarity and engagement, consider adding specific examples or emphasizing the urgency of action. Here's a revised version:\n\nClimate change is a long-term alteration of Earth's climate patterns caused primarily by human activities such as burning fossil fuels, deforestation, and industrial emissions. These actions increase greenhouse gases in the atmosphere, leading to rising global temperatures, melting ice caps, and more frequent extreme weather events like hurricanes and droughts. The effects threaten ecosystems, disrupt agriculture, and endanger communities worldwide. Addressing this crisis requires urgent, coordinated global efforts to reduce emissions, adopt renewable energy, and promote sustainable practices to safeguard the planet for future generations." type='TextMessage'
source='DiGraphStopAgent' models_usage=None metadata={} content='Digraph execution is complete' type='StopMessage' messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Write a short paragraph about climate change.', type='TextMessage'), TextMessage(source='writer', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=95), metadata={}, content='Climate change refers to long-term shifts in temperature, precipitation, and other atmospheric patterns, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These changes contribute to rising global temperatures, melting ice caps, more frequent and severe weather events, and adverse impacts on ecosystems and human communities. Addressing climate change requires global cooperation to reduce greenhouse gas emissions, transition to renewable energy sources, and implement sustainable practices to protect the planet for future generations.', type='TextMessage'), TextMessage(source='reviewer', models_usage=RequestUsage(prompt_tokens=127, completion_tokens=144), metadata={}, content="The paragraph provides a clear overview of climate change, its causes, and its impacts. To enhance clarity and engagement, consider adding specific examples or emphasizing the urgency of action. Here's a revised version:\n\nClimate change is a long-term alteration of Earth's climate patterns caused primarily by human activities such as burning fossil fuels, deforestation, and industrial emissions. These actions increase greenhouse gases in the atmosphere, leading to rising global temperatures, melting ice caps, and more frequent extreme weather events like hurricanes and droughts. The effects threaten ecosystems, disrupt agriculture, and endanger communities worldwide. Addressing this crisis requires urgent, coordinated global efforts to reduce emissions, adopt renewable energy, and promote sustainable practices to safeguard the planet for future generations.", type='TextMessage'), StopMessage(source='DiGraphStopAgent', models_usage=None, metadata={}, content='Digraph execution is complete', type='StopMessage')] stop_reason='Stop message received'
```


### Parallel Flow with Join

We now create a slightly more complex flow:

*   A **writer** drafts a paragraph.
*   Two **editors** independently edit for grammar and style (parallel fan-out).
*   A **final reviewer** consolidates their edits (join).

Execution starts at the **writer**, fans out to **editor1** and **editor2** simultaneously, and then both feed into the **final reviewer**.

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Create an OpenAI model client
client = OpenAIChatCompletionClient(model="gpt-4.1-nano")

# Create the writer agent
writer = AssistantAgent(
    "writer", model_client=client, system_message="Draft a short paragraph on climate change."
)

# Create two editor agents
editor1 = AssistantAgent(
    "editor1", model_client=client, system_message="Edit the paragraph for grammar."
)
editor2 = AssistantAgent(
    "editor2", model_client=client, system_message="Edit the paragraph for style."
)

# Create the final reviewer agent
final_reviewer = AssistantAgent(
    "final_reviewer",
    model_client=client,
    system_message="Consolidate the grammar and style edits into a final version.",
)

# Build the workflow graph
builder = DiGraphBuilder()
builder.add_node(writer).add_node(editor1).add_node(editor2).add_node(final_reviewer)

# Fan-out from writer to editor1 and editor2
builder.add_edge(writer, editor1)
builder.add_edge(writer, editor2)

# Fan-in both editors into final reviewer
builder.add_edge(editor1, final_reviewer)
builder.add_edge(editor2, final_reviewer)

# Build and validate the graph
graph = builder.build()

# Create the flow
flow = GraphFlow(
    participants=builder.get_participants(),
    graph=graph,
)

# Run the workflow
await Console(flow.run_stream(task="Write a short paragraph about climate change."))
```

```
---------- TextMessage (user) ----------
Write a short paragraph about climate change.
---------- TextMessage (writer) ----------
Climate change refers to long-term shifts in weather patterns and global temperatures, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These activities increase concentrations of greenhouse gases like carbon dioxide and methane in the atmosphere, leading to global warming. The impacts of climate change include more frequent and severe weather events, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this urgent issue requires international cooperation, significant shifts toward renewable energy sources, and sustainable practices to reduce our carbon footprint and protect the planet for future generations.
---------- TextMessage (editor1) ----------
Climate change refers to long-term shifts in weather patterns and global temperatures, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These activities increase concentrations of greenhouse gases like carbon dioxide and methane in the atmosphere, leading to global warming. The impacts of climate change include more frequent and severe weather events, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this urgent issue requires international cooperation, significant shifts toward renewable energy sources, and sustainable practices to reduce our carbon footprint and protect the planet for future generations.
---------- TextMessage (editor2) ----------
Climate change involves long-term alterations in weather patterns and global temperatures, primarily caused by human activities like burning fossil fuels, deforestation, and industrial processes. These actions elevate levels of greenhouse gases such as carbon dioxide and methane, resulting in global warming. Its consequences are widespread, including more frequent and intense storms, rising sea levels, melting glaciers, and disturbances to ecosystems and agriculture. Combating this crisis demands international collaboration, a swift transition to renewable energy, and sustainable practices to cut carbon emissions, ensuring a healthier planet for future generations.
---------- TextMessage (final_reviewer) ----------
Climate change involves long-term alterations in weather patterns and global temperatures, primarily caused by human activities such as burning fossil fuels, deforestation, and industrial processes. These actions increase levels of greenhouse gases like carbon dioxide and methane, leading to global warming. Its consequences include more frequent and intense storms, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this crisis requires international collaboration, a swift transition to renewable energy, and sustainable practices to reduce carbon emissions, ensuring a healthier planet for future generations.
---------- StopMessage (DiGraphStopAgent) ----------
Digraph execution is complete
TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Write a short paragraph about climate change.', type='TextMessage'), TextMessage(source='writer', models_usage=RequestUsage(prompt_tokens=28, completion_tokens=113), metadata={}, content='Climate change refers to long-term shifts in weather patterns and global temperatures, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These activities increase concentrations of greenhouse gases like carbon dioxide and methane in the atmosphere, leading to global warming. The impacts of climate change include more frequent and severe weather events, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this urgent issue requires international cooperation, significant shifts toward renewable energy sources, and sustainable practices to reduce our carbon footprint and protect the planet for future generations.', type='TextMessage'), TextMessage(source='editor1', models_usage=RequestUsage(prompt_tokens=144, completion_tokens=113), metadata={}, content='Climate change refers to long-term shifts in weather patterns and global temperatures, largely driven by human activities such as burning fossil fuels, deforestation, and industrial processes. These activities increase concentrations of greenhouse gases like carbon dioxide and methane in the atmosphere, leading to global warming. The impacts of climate change include more frequent and severe weather events, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this urgent issue requires international cooperation, significant shifts toward renewable energy sources, and sustainable practices to reduce our carbon footprint and protect the planet for future generations.', type='TextMessage'), TextMessage(source='editor2', models_usage=RequestUsage(prompt_tokens=263, completion_tokens=107), metadata={}, content='Climate change involves long-term alterations in weather patterns and global temperatures, primarily caused by human activities like burning fossil fuels, deforestation, and industrial processes. These actions elevate levels of greenhouse gases such as carbon dioxide and methane, resulting in global warming. Its consequences are widespread, including more frequent and intense storms, rising sea levels, melting glaciers, and disturbances to ecosystems and agriculture. Combating this crisis demands international collaboration, a swift transition to renewable energy, and sustainable practices to cut carbon emissions, ensuring a healthier planet for future generations.', type='TextMessage'), TextMessage(source='final_reviewer', models_usage=RequestUsage(prompt_tokens=383, completion_tokens=104), metadata={}, content='Climate change involves long-term alterations in weather patterns and global temperatures, primarily caused by human activities such as burning fossil fuels, deforestation, and industrial processes. These actions increase levels of greenhouse gases like carbon dioxide and methane, leading to global warming. Its consequences include more frequent and intense storms, rising sea levels, melting glaciers, and disruptions to ecosystems and agriculture. Addressing this crisis requires international collaboration, a swift transition to renewable energy, and sustainable practices to reduce carbon emissions, ensuring a healthier planet for future generations.', type='TextMessage'), StopMessage(source='DiGraphStopAgent', models_usage=None, metadata={}, content='Digraph execution is complete', type='StopMessage')] stop_reason='Stop message received')
```


## Message Filtering

### Execution Graph vs. Message Graph

In GraphFlow, the **execution graph** is defined using `DiGraph`, which controls the order in which agents execute. However, the execution graph does not control what messages an agent receives from other agents. By default, all messages are sent to all agents in the graph.

**Message filtering** is a separate feature that allows you to filter the messages received by each agent and limiting their model context to only the relevant information. The set of message filters defines the **message graph** in the flow.

Specifying the message graph can help with:

*   Reduce hallucinations
*   Control memory load
*   Focus agents only on relevant information

You can use `MessageFilterAgent` together with `MessageFilterConfig` and `PerSourceFilter` to define these rules.

```python
from autogen_agentchat.agents import AssistantAgent, MessageFilterAgent, MessageFilterConfig, PerSourceFilter
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Model client
client = OpenAIChatCompletionClient(model="gpt-4.1-nano")

# Create agents
researcher = AssistantAgent(
    "researcher", model_client=client, system_message="Summarize key facts about climate change."
)
analyst = AssistantAgent("analyst", model_client=client, system_message="Review the summary and suggest improvements.")
presenter = AssistantAgent(
    "presenter", model_client=client, system_message="Prepare a presentation slide based on the final summary."
)

# Apply message filtering
filtered_analyst = MessageFilterAgent(
    name="analyst",
    wrapped_agent=analyst,
    filter=MessageFilterConfig(per_source=[PerSourceFilter(source="researcher", position="last", count=1)]),
)
filtered_presenter = MessageFilterAgent(
    name="presenter",
    wrapped_agent=presenter,
    filter=MessageFilterConfig(per_source=[PerSourceFilter(source="analyst", position="last", count=1)]),
)

# Build the flow
builder = DiGraphBuilder()
builder.add_node(researcher).add_node(filtered_analyst).add_node(filtered_presenter)
builder.add_edge(researcher, filtered_analyst).add_edge(filtered_analyst, filtered_presenter)

# Create the flow
flow = GraphFlow(
    participants=builder.get_participants(),
    graph=builder.build(),
)

# Run the flow
await Console(flow.run_stream(task="Summarize key facts about climate change."))
```

```
---------- TextMessage (user) ----------
Summarize key facts about climate change.
---------- TextMessage (researcher) ----------
Certainly! Here are some key facts about climate change: 1. **Global Warming**: Earth's average surface temperature has increased significantly over the past century, primarily due to human activities. 2. **Greenhouse Gas Emissions**: The main contributors
```


```
are carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O), resulting from burning fossil fuels, deforestation, and industrial processes. 3. **Impacts on Weather and Climate**: Climate change leads to more frequent and severe heatwaves, storms, droughts, and heavy rainfall. 4. **Rising Sea Levels**: Melting polar ice caps and glaciers, along with thermal expansion of seawater, are causing sea levels to rise. 5. **Effects on Ecosystems**: Altered habitats threaten plant and animal species, leading to biodiversity loss. 6. **Human Health and Societies**: Climate change contributes to health issues, food and water insecurity, and displacement of populations. 7. **Global Response**: International efforts like the Paris Agreement aim to limit temperature rise, promote renewable energy, and reduce emissions. 8. **Urgency**: Addressing climate change requires immediate, concerted actions to mitigate further damage and adapt to changes. Let me know if you want more detailed information on any of these points! ---------- TextMessage (analyst) ---------- Your summary effectively covers the fundamental aspects of climate change and presents them clearly. Here are some suggestions to improve clarity, depth, and engagement: 1. Enhance structure with subheadings: Organize points into thematic sections (e.g., Causes, Effects, Responses) for easier navigation. 2. Add recent context or data: Incorporate the latest statistics or notable recent events to emphasize urgency. 3. Emphasize solutions: Briefly mention specific mitigation and adaptation strategies beyond international agreements. 4. Use more precise language: For example, specify the amount of temperature increase globally (~1.2°C since pre-industrial times). 5. Incorporate the importance of individual actions: Highlight how personal choices contribute to climate efforts. 6. Mention climate feedback loops: Briefly note how certain effects (like melting ice) can accelerate warming. **Improved Version:** --- **Overview of Climate Change** **Causes:** - Human activities, especially burning fossil fuels, deforestation, and industrial processes, have led to increased concentrations of greenhouse gases such as carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O)
```


```
. - Since the late 19th century, Earth's average surface temperature has risen by approximately 1.2°C, with the past decade being the warmest on record. **Impacts:** - The changing climate causes more frequent and intense heatwaves, storms, droughts, and heavy rainfall events. - Melting polar ice caps and glaciers, along with thermal expansion, are raising sea levels, threatening coastal communities. - Ecosystems are shifting, leading to habitat loss and risking biodiversity, with some species facing extinction. - Human health and societies are affected through increased heat-related illnesses, food and water insecurity, and displacement due to extreme weather events. **Global Response and Solutions:** - International agreements like the Paris Agreement aim to limit global temperature rise well below 2°C. - Strategies include transitioning to renewable energy sources, increasing energy efficiency, reforestation, and sustainable land use. - Community and individual actions—reducing carbon footprints, supporting sustainable policies, and raising awareness—are essential components. **Urgency and Call to Action:** - Immediate, coordinated efforts are critical to mitigate irreversible damage and adapt to ongoing changes. - Every sector, from government to individual, has a role to play in creating a sustainable future. --- Let me know if you'd like a more detailed explanation of any section or additional statistical data! ---------- TextMessage (presenter) ---------- **Slide Title:** **Climate Change: Causes, Impacts & Solutions** **Causes:** - Emissions from burning fossil fuels, deforestation, industrial activities - Greenhouse gases (CO₂, CH₄, N₂O) have increased significantly - Global temperature has risen by ~1.2°C since pre-industrial times **Impacts:** - More frequent heatwaves, storms, droughts, and heavy rainfall - Melting ice caps and rising sea levels threaten coastal areas - Habitat loss and decreased biodiversity - Health risks and societal disruptions **Responses & Solutions:** - International efforts like the Paris Agreement aim to limit warming - Transitioning to renewable energy, energy efficiency, reforestation - Community and individual actions: reducing carbon footprints and raising awareness **U
```


```
rgency:** - Immediate, coordinated action is essential to prevent irreversible damage - Everyone has a role in building a sustainable future ---------- StopMessage (DiGraphStopAgent) ---------- Digraph execution is complete TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Summarize key facts about climate change.', type='TextMessage'), TextMessage(source='researcher', models_usage=RequestUsage(prompt_tokens=30, completion_tokens=267), metadata={}, content="Certainly! Here are some key facts about climate change:\n\n1. **Global Warming**: Earth's average surface temperature has increased significantly over the past century, primarily due to human activities.\n2. **Greenhouse Gas Emissions**: The main contributors are carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O), resulting from burning fossil fuels, deforestation, and industrial processes.\n3. **Impacts on Weather and Climate**: Climate change leads to more frequent and severe heatwaves, storms, droughts, and heavy rainfall.\n4. **Rising Sea Levels**: Melting polar ice caps and glaciers, along with thermal expansion of seawater, are causing sea levels to rise.\n5. **Effects on Ecosystems**: Altered habitats threaten plant and animal species, leading to biodiversity loss.\n6. **Human Health and Societies**: Climate change contributes to health issues, food and water insecurity, and displacement of populations.\n7. **Global Response**: International efforts like the Paris Agreement aim to limit temperature rise, promote renewable energy, and reduce emissions.\n8. **Urgency**: Addressing climate change requires immediate, concerted actions to mitigate further damage and adapt to changes.\n\nLet me know if you want more detailed information on any of these points!", type='TextMessage'), TextMessage(source='analyst', models_usage=RequestUsage(prompt_tokens=287, completion_tokens=498), metadata={}, content="Your summary effectively covers the fundamental aspects of climate change and presents them clearly. Here are some suggestions to improve clarity, depth, and engagement:\n\n1. Enhance structure with subheadings: Organize points into thematic sections (e.g., Causes, Effects, Responses) for easier navigation.\n2
```


```
. Add recent context or data: Incorporate the latest statistics or notable recent events to emphasize urgency.\n3. Emphasize solutions: Briefly mention specific mitigation and adaptation strategies beyond international agreements.\n4. Use more precise language: For example, specify the amount of temperature increase globally (~1.2°C since pre-industrial times).\n5. Incorporate the importance of individual actions: Highlight how personal choices contribute to climate efforts.\n6. Mention climate feedback loops: Briefly note how certain effects (like melting ice) can accelerate warming.\n\n**Improved Version:**\n\n---\n\n**Overview of Climate Change**\n\n**Causes:**\n- Human activities, especially burning fossil fuels, deforestation, and industrial processes, have led to increased concentrations of greenhouse gases such as carbon dioxide (CO₂), methane (CH₄), and nitrous oxide (N₂O).\n- Since the late 19th century, Earth's average surface temperature has risen by approximately 1.2°C, with the past decade being the warmest on record.\n\n**Impacts:**\n- The changing climate causes more frequent and intense heatwaves, storms, droughts, and heavy rainfall events.\n- Melting polar ice caps and glaciers, along with thermal expansion, are raising sea levels, threatening coastal communities.\n- Ecosystems are shifting, leading to habitat loss and risking biodiversity, with some species facing extinction.\n- Human health and societies are affected through increased heat-related illnesses, food and water insecurity, and displacement due to extreme weather events.\n\n**Global Response and Solutions:**\n- International agreements like the Paris Agreement aim to limit global temperature rise well below 2°C.\n- Strategies include transitioning to renewable energy sources, increasing energy efficiency, reforestation, and sustainable land use.\n- Community and individual actions—reducing carbon footprints, supporting sustainable policies, and raising awareness—are essential components.\n\n**Urgency and Call to Action:**\n- Immediate, coordinated efforts are critical to mitigate irreversible damage and adapt to ongoing changes.\n- Every sector, from government to individual, has a role to play in creating a sustainable future.\n\n---
```


```
\nLet me know if you'd like a more detailed explanation of any section or additional statistical data!", type='TextMessage'), TextMessage(source='presenter', models_usage=RequestUsage(prompt_tokens=521, completion_tokens=192), metadata={}, content='**Slide Title:** \n**Climate Change: Causes, Impacts & Solutions**\n\n**Causes:** \n- Emissions from burning fossil fuels, deforestation, industrial activities \n- Greenhouse gases (CO₂, CH₄, N₂O) have increased significantly \n- Global temperature has risen by ~1.2°C since pre-industrial times \n\n**Impacts:** \n- More frequent heatwaves, storms, droughts, and heavy rainfall \n- Melting ice caps and rising sea levels threaten coastal areas \n- Habitat loss and decreased biodiversity \n- Health risks and societal disruptions \n\n**Responses & Solutions:** \n- International efforts like the Paris Agreement aim to limit warming \n- Transitioning to renewable energy, energy efficiency, reforestation \n- Community and individual actions: reducing carbon footprints and raising awareness \n\n**Urgency:** \n- Immediate, coordinated action is essential to prevent irreversible damage \n- Everyone has a role in building a sustainable future', type='TextMessage'), StopMessage(source='DiGraphStopAgent', models_usage=None, metadata={}, content='Digraph execution is complete', type='StopMessage')] stop_reason='Stop message received')
```


### 🔁 Advanced Example: Conditional Loop + Filtered Summary

This example demonstrates:

*   A loop between generator and reviewer (which exits when reviewer says "APPROVE")
*   A summarizer agent that only sees the first user input and the last reviewer message

```python
from autogen_agentchat.agents import AssistantAgent, MessageFilterAgent, MessageFilterConfig, PerSourceFilter
from autogen_agentchat.teams import (
    DiGraphBuilder,
    GraphFlow,
)
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

# Agents
generator = AssistantAgent("generator", model_client=model_client, system_message="Generate a list of creative ideas.")
reviewer = AssistantAgent(
    "reviewer",
    model_client=model_client,
    system_message="Review ideas and say 'REVISE' and provide feedbacks, or 'APPROVE' for final approval.",
)
summarizer_core = AssistantAgent(
    "summary",
    model_client=model_client,
    system_message="Summarize the user request and the final feedback.",
)

# Filtered summarizer
filtered_summarizer = MessageFilterAgent(
    name="summary",
    wrapped_agent=summarizer_core,
    filter=MessageFilterConfig(
        per_source=[
            PerSourceFilter(source="user", position="first", count=1),
            PerSourceFilter(source="reviewer", position="last", count=1),
        ]
    ),
)

# Build graph with conditional loop
builder = DiGraphBuilder()
builder.add_node(generator).add_node(reviewer).add_node(filtered_summarizer)
builder.add_edge(generator, reviewer)
builder.add_edge(reviewer, generator, condition="REVISE")
builder.add_edge(reviewer, filtered_summarizer, condition="APPROVE")
builder.set_entry_point(generator)  # Set entry point to generator. Required if there are no source nodes.
graph = builder.build()

# Create the flow
flow = GraphFlow(
    participants=builder.get_participants(),
    graph=graph,
)

# Run the flow and pretty print the output in the console
await Console(flow.run_stream(task="Brainstorm ways to reduce plastic waste."))
```

```
---------- TextMessage (user) ----------
Brainstorm ways to reduce plastic waste.
---------- TextMessage (generator) ----------
1. **Reusable Packaging Innovations**: Develop a subscription service that provides reusable containers for household products (like detergents, shampoos, etc.) which can be returned for refills. 2. **Biodegradable Alternatives**: Invest in research for materials that mimic plastic but break down more easily, such as mushroom mycelium, seaweed, or plant-based polymers. 3. **Community Swap Events**: Organize local events where people can swap items they no longer need, reducing the need to buy new plastic-containing products. 4. **Educational Workshops**: Host workshops in schools and communities that educate participants about the impacts of plastic waste and how to reduce it in their daily lives. 5. **Plastic Waste Upcycling**: Encourage creativity with workshops that teach people how to make art or useful items from plastic waste, such as furniture, decor, or gardening tools. 6. **Plastic-Free Challenges**: Create month-long challenges that encourage individuals and families to reduce plastic use, sharing their progress on social media to inspire others. 7. **Refill Stations**: Install public refill stations for water, cleaning supplies, and personal care products in high-footfall areas like gyms, parks, and shopping centers. 8. **Corporate Partnerships**: Collaborate with businesses to create incentives for customers to bring their own containers, such as discounts at coffee shops or grocery stores. 9. **Digital Packaging**: Explore digital solutions like smart packaging that provides all necessary product information via QR codes, reducing the need for physical packaging. 10. **Government Legislation Advocates**: Advocate for local governments to impose bans on single-use plastics and support policies that promote sustainable materials. 11. **Plastic Waste Art Competitions**: Organize contests that challenge artists to create impactful pieces from plastic waste to raise awareness and promote recycling. 12. **Sustainable School Programs**: Integrate sustainability topics within school curricula and promote student-led initiatives to reduce plastic within their institutions. 13.
```


```
**Eco-Friendly Vending Machines**: Create vending machines that dispense snacks and drinks in reusable containers, encouraging customers to return them after use. 14. **Gardening Kits with Recyclable Components**: Supply gardening starter kits that include materials like biodegradable pots and natural fertilizers, promoting a zero-waste gardening approach. 15. **DIY Personal Care Products**: Develop and disseminate DIY recipes for personal care products, such as soaps and lotions that encourage the use of bulk ingredients instead of plastic-packaged goods. 16. **Plastic Neutrality Programs**: Encourage businesses to adopt plastic neutrality programs where they balance out their plastic usage by supporting clean-up or recycling initiatives. 17. **Plastic-Free Grocery Stores**: Promote or support grocery stores that operate exclusively without plastic, offering bulk options, glass containers, or other eco-friendly packaging. 18. **Innovative Composting Solutions**: Design composting systems that make it easy for households to compost food and biodegradable materials, reducing plastic packaging associated with food waste. 19. **Mobile Apps for Plastic Waste Tracking**: Create an app that helps users track their plastic consumption and offers tips for reducing it, while also rewarding users for achievements. 20. **Public Awareness Campaigns**: Launch a campaign that creatively highlights the environmental impact of plastic waste through social media challenges and community engagement. ---------- TextMessage (reviewer) ---------- REVISE This is a comprehensive and creative list of ideas to reduce plastic waste. Here are a few feedback points to enhance the suggestions further: 1. **Reusable Packaging Innovations**: Consider adding partnerships with local retailers to encourage participation and facilitate the logistics of returning and refilling containers. 2. **Biodegradable Alternatives**: It may be useful to specify how these materials would be incorporated into existing supply chains or product lines to make the transition smoother for businesses. 3. **Community Swap Events**: Suggest including a digital platform for participants who cannot attend events to swap items online, thereby broadening the reach. 4.
```


```
**Educational Workshops**: Incorporate activities or hands-on experiences to engage participants better and make the learning process more memorable. 5. **Plastic Waste Upcycling**: Perhaps develop a certification process for workshops to promote quality and attract a wider audience. 6. **Plastic-Free Challenges**: To enhance engagement, consider partnering with influencers or local businesses that could sponsor awards or prizes for participants. 7. **Refill Stations**: Investigate the feasibility and potential locations for such stations to ensure they are accessible to the public. 8. **Corporate Partnerships**: It would be beneficial to specify the types of businesses you think would be most effective partners (e.g., cafes, grocery stores). 9. **Digital Packaging**: Elaborate on the potential barriers to this approach, such as consumer access to smartphones, to provide a well-rounded view. 10. **Government Legislation Advocates**: Suggest specific legislative measures that could be advocated for, making this point more actionable. 11. **Plastic Waste Art Competitions**: Promote collaboration with local art communities or schools to engage a wider audience and increase participation. 12. **Sustainable School Programs**: Propose ways to incentivize schools to participate, perhaps through competitive grants or recognition programs. 13. **Eco-Friendly Vending Machines**: Explore potential partnerships with local food vendors to ensure a diverse and appealing selection of products. 14. **Gardening Kits with Recyclable Components**: Consider the potential market and audience for these kits, such as urban dwellers or schools, to tailor marketing strategies. 15. **DIY Personal Care Products**: Include suggestions for workshops where participants can create these products collectively, fostering community and sharing knowledge. 16. **Plastic Neutrality Programs**: Define what criteria businesses would need to meet to qualify for such a program to encourage transparent efforts. 17. **Plastic-Free Grocery Stores**: Highlight examples of existing stores operating without plastic to serve as inspiration for future initiatives. 18.
```


```
**Innovative Composting Solutions**: Provide examples of successful composting programs from other regions or communities to illustrate potential implementation. 19. **Mobile Apps for Plastic Waste Tracking**: Suggest features that would make the app engaging, such as gamification, social sharing, or integration with sustainability rewards programs. 20. **Public Awareness Campaigns**: Recommend specific themes or creative approaches that could resonate with the target audience for these campaigns. These revisions will enhance clarity, practicality, and engagement, making the ideas more actionable and impactful. ---------- TextMessage (generator) ---------- Thank you for the feedback! Here's a revised version of the list of ideas to reduce plastic waste, incorporating your suggestions for enhancement: 1. **Reusable Packaging Innovations**: Partner with local retailers to establish a robust logistics system for returning and refilling containers, ensuring widespread participation and convenience for consumers. 2. **Biodegradable Alternatives**: Identify specific strategies for incorporating biodegradable materials into existing supply chains or product lines, facilitating a smoother transition for businesses to adopt eco-friendly options. 3. **Community Swap Events**: Create a digital platform allowing individuals to swap items online, engaging those who cannot attend physical events and expanding the initiative's reach. 4. **Educational Workshops**: Integrate hands-on experiences and interactive activities to keep participants engaged and enhance retention of knowledge about reducing plastic use. 5. **Plastic Waste Upcycling**: Develop a certification process for upcycling workshops, which would promote quality standards and attract a broader audience interested in sustainable crafts. 6. **Plastic-Free Challenges**: Collaborate with local influencers or businesses to sponsor awards or prizes for challenge participants, boosting engagement and motivation. 7. **Refill Stations**: Conduct feasibility studies to identify optimal locations for refill stations (e.g., busy urban areas, shopping centers) to ensure they are accessible to the public. 8.
```


```
**Corporate Partnerships**: Target specific types of businesses as partners, such as cafes, grocery stores, and retailers, that naturally align with the initiative to promote reusable and sustainable practices. 9. **Digital Packaging**: Address potential barriers to adopting digital packaging solutions, like smartphone accessibility, to present a comprehensive view of the concept's practicality. 10. **Government Legislation Advocates**: Suggest specific legislative measures to advocate for, such as bans on single-use plastics or tax incentives for companies that commit to sustainable practices, making advocacy more actionable. 11. **Plastic Waste Art Competitions**: Collaborate with local art communities or educational institutions to organize competitions that engage a wider audience and encourage creativity while raising awareness. 12. **Sustainable School Programs**: Propose competitive grants or recognition programs to incentivize schools to adopt sustainable practices and participate in environmental initiatives. 13. **Eco-Friendly Vending Machines**: Explore partnerships with local food vendors to offer a diverse selection of products in vending machines that prioritize sustainability and convenience. 14. **Gardening Kits with Recyclable Components**: Research market segments (like urban dwellers or schools) to tailor gardening kits effectively, ensuring relevance and demand in marketing strategies. 15. **DIY Personal Care Products**: Host community workshops where participants can collaboratively create DIY products, fostering a sense of community while promoting zero waste practices. 16. **Plastic Neutrality Programs**: Define criteria that businesses must meet to qualify for plastic neutrality, ensuring transparency and encouraging meaningful participation in sustainability efforts. 17. **Plastic-Free Grocery Stores**: Highlight successful case studies of existing plastic-free grocery stores or markets to serve as models for new initiatives. 18. **Innovative Composting Solutions**: Provide examples of successful composting initiatives from other communities to illustrate best practices and potential implementations. 19.
```


```
**Mobile Apps for Plastic Waste Tracking**: Include engaging features like gamification, social sharing capabilities, and integration with local sustainability rewards programs to enhance user experience. 20. **Public Awareness Campaigns**: Recommend specific themes (e.g., ocean conservation, wildlife protection) or creative approaches (like storytelling or humor) to resonate strongly with target audiences in awareness campaigns. These revisions aim to enhance clarity, practicality, and engagement, making the ideas more actionable and impactful for addressing plastic waste reduction. ---------- TextMessage (reviewer) ---------- APPROVE This revised list is well-thought-out and addresses the feedback effectively. Each suggestion is clearer, more practical, and focused on engagement and implementation. You've introduced specific strategies, collaborative elements, and examples that can help elevate the initiatives. The points are actionable and demonstrate a comprehensive approach to tackling plastic waste. Well done! ---------- TextMessage (summary) ---------- The user requested ideas for reducing plastic waste. The final feedback expressed approval of a revised list of suggestions, highlighting that it effectively addressed the initially requested feedback. The reviewer praised the clarity, practicality, and comprehensiveness of the strategies, noting that they included actionable points and collaborative elements to enhance implementation. ---------- StopMessage (DiGraphStopAgent) ---------- Digraph execution is complete TaskResult(messages=[TextMessage(source='user', models_usage=None, metadata={}, content='Brainstorm ways to reduce plastic waste.', type='TextMessage'), TextMessage(source='generator', models_usage=RequestUsage(prompt_tokens=27, completion_tokens=661), metadata={}, content='1. **Reusable Packaging Innovations**: Develop a subscription service that provides reusable containers for household products (like detergents, shampoos, etc.) which can be returned for refills.\n\n2. **Biodegradable Alternatives**: Invest in research for materials that mimic plastic but break down more easily, such as mushroom mycelium, seaweed, or plant-based polymers.\n\n3.
```


```
**Community Swap Events**: Organize local events where people can swap items they no longer need, reducing the need to buy new plastic-containing products.\n\n4. **Educational Workshops**: Host workshops in schools and communities that educate participants about the impacts of plastic waste and how to reduce it in their daily lives.\n\n5. **Plastic Waste Upcycling**: Encourage creativity with workshops that teach people how to make art or useful items from plastic waste, such as furniture, decor, or gardening tools.\n\n6. **Plastic-Free Challenges**: Create month-long challenges that encourage individuals and families to reduce plastic use, sharing their progress on social media to inspire others.\n\n7. **Refill Stations**: Install public refill stations for water, cleaning supplies, and personal care products in high-footfall areas like gyms, parks, and shopping centers.\n\n8. **Corporate Partnerships**: Collaborate with businesses to create incentives for customers to bring their own containers, such as discounts at coffee shops or grocery stores.\n\n9. **Digital Packaging**: Explore digital solutions like smart packaging that provides all necessary product information via QR codes, reducing the need for physical packaging.\n\n10. **Government Legislation Advocates**: Advocate for local governments to impose bans on single-use plastics and support policies that promote sustainable materials.\n\n11. **Plastic Waste Art Competitions**: Organize contests that challenge artists to create impactful pieces from plastic waste to raise awareness and promote recycling.\n\n12. **Sustainable School Programs**: Integrate sustainability topics within school curricula and promote student-led initiatives to reduce plastic within their institutions.\n\n13. **Eco-Friendly Vending Machines**: Create vending machines that dispense snacks and drinks in reusable containers, encouraging customers to return them after use.\n\n14. **Gardening Kits with Recyclable Components**: Supply gardening starter kits that include materials like biodegradable pots and natural fertilizers, promoting a zero-waste gardening approach.\n\n15.
```


```
**DIY Personal Care Products**: Develop and disseminate DIY recipes for personal care products, such as soaps and lotions that encourage the use of bulk ingredients instead of plastic-packaged goods.\n\n16. **Plastic Neutrality Programs**: Encourage businesses to adopt plastic neutrality programs where they balance out their plastic usage by supporting clean-up or recycling initiatives.\n\n17. **Plastic-Free Grocery Stores**: Promote or support grocery stores that operate exclusively without plastic, offering bulk options, glass containers, or other eco-friendly packaging.\n\n18. **Innovative Composting Solutions**: Design composting systems that make it easy for households to compost food and biodegradable materials, reducing plastic packaging associated with food waste.\n\n19. **Mobile Apps for Plastic Waste Tracking**: Create an app that helps users track their plastic consumption and offers tips for reducing it, while also rewarding users for achievements.\n\n20. **Public Awareness Campaigns**: Launch a campaign that creatively highlights the environmental impact of plastic waste through social media challenges and community engagement.', type='TextMessage'), TextMessage(source='reviewer', models_usage=RequestUsage(prompt_tokens=710, completion_tokens=625), metadata={}, content='REVISE\n\nThis is a comprehensive and creative list of ideas to reduce plastic waste. Here are a few feedback points to enhance the suggestions further:\n\n1. **Reusable Packaging Innovations**: Consider adding partnerships with local retailers to encourage participation and facilitate the logistics of returning and refilling containers.\n\n2. **Biodegradable Alternatives**: It may be useful to specify how these materials would be incorporated into existing supply chains or product lines to make the transition smoother for businesses.\n\n3. **Community Swap Events**: Suggest including a digital platform for participants who cannot attend events to swap items online, thereby broadening the reach.\n\n4. **Educational Workshops**: Incorporate activities or hands-on experiences to engage participants better and make the learning process more memorable.\n\n5.
```


```
**Plastic Waste Upcycling**: Perhaps develop a certification process for workshops to promote quality and attract a wider audience.\n\n6. **Plastic-Free Challenges**: To enhance engagement, consider partnering with influencers or local businesses that could sponsor awards or prizes for participants.\n\n7. **Refill Stations**: Investigate the feasibility and potential locations for such stations to ensure they are accessible to the public.\n\n8. **Corporate Partnerships**: It would be beneficial to specify the types of businesses you think would be most effective partners (e.g., cafes, grocery stores).\n\n9. **Digital Packaging**: Elaborate on the potential barriers to this approach, such as consumer access to smartphones, to provide a well-rounded view.\n\n10. **Government Legislation Advocates**: Suggest specific legislative measures that could be advocated for, making this point more actionable.\n\n11. **Plastic Waste Art Competitions**: Promote collaboration with local art communities or schools to engage a wider audience and increase participation.\n\n12. **Sustainable School Programs**: Propose ways to incentivize schools to participate, perhaps through competitive grants or recognition programs.\n\n13. **Eco-Friendly Vending Machines**: Explore potential partnerships with local food vendors to ensure a diverse and appealing selection of products.\n\n14. **Gardening Kits with Recyclable Components**: Consider the potential market and audience for these kits, such as urban dwellers or schools, to tailor marketing strategies.\n\n15. **DIY Personal Care Products**: Include suggestions for workshops where participants can create these products collectively, fostering community and sharing knowledge.\n\n16. **Plastic Neutrality Programs**: Define what criteria businesses would need to meet to qualify for such a program to encourage transparent efforts.\n\n17. **Plastic-Free Grocery Stores**: Highlight examples of existing stores operating without plastic to serve as inspiration for future initiatives.\n\n18. **Innovative Composting Solutions**: Provide examples of successful composting programs from other regions or communities to illustrate potential implementation.\n\n19.
```


```
**Mobile Apps for Plastic Waste Tracking**: Suggest features that would make the app engaging, such as gamification, social sharing, or integration with sustainability rewards programs.\n\n20. **Public Awareness Campaigns**: Recommend specific themes or creative approaches that could resonate with the target audience for these campaigns.\n\nThese revisions will enhance clarity, practicality, and engagement, making the ideas more actionable and impactful.', type='TextMessage'), TextMessage(source='generator', models_usage=RequestUsage(prompt_tokens=1322, completion_tokens=721), metadata={}, content="Thank you for the feedback! Here's a revised version of the list of ideas to reduce plastic waste, incorporating your suggestions for enhancement:\n\n1. **Reusable Packaging Innovations**: Partner with local retailers to establish a robust logistics system for returning and refilling containers, ensuring widespread participation and convenience for consumers.\n\n2. **Biodegradable Alternatives**: Identify specific strategies for incorporating biodegradable materials into existing supply chains or product lines, facilitating a smoother transition for businesses to adopt eco-friendly options.\n\n3. **Community Swap Events**: Create a digital platform allowing individuals to swap items online, engaging those who cannot attend physical events and expanding the initiative's reach.\n\n4. **Educational Workshops**: Integrate hands-on experiences and interactive activities to keep participants engaged and enhance retention of knowledge about reducing plastic use.\n\n5. **Plastic Waste Upcycling**: Develop a certification process for upcycling workshops, which would promote quality standards and attract a broader audience interested in sustainable crafts.\n\n6. **Plastic-Free Challenges**: Collaborate with local influencers or businesses to sponsor awards or prizes for challenge participants, boosting engagement and motivation.\n\n7. **Refill Stations**: Conduct feasibility studies to identify optimal locations for refill stations (e.g., busy urban areas, shopping centers) to ensure they are accessible to the public.\n\n8.
```


```
**Corporate Partnerships**: Target specific types of businesses as partners, such as cafes, grocery stores, and retailers, that naturally align with the initiative to promote reusable and sustainable practices.\n\n9. **Digital Packaging**: Address potential barriers to adopting digital packaging solutions, like smartphone accessibility, to present a comprehensive view of the concept's practicality.\n\n10. **Government Legislation Advocates**: Suggest specific legislative measures to advocate for, such as bans on single-use plastics or tax incentives for companies that commit to sustainable practices, making advocacy more actionable.\n\n11. **Plastic Waste Art Competitions**: Collaborate with local art communities or educational institutions to organize competitions that engage a wider audience and encourage creativity while raising awareness.\n\n12. **Sustainable School Programs**: Propose competitive grants or recognition programs to incentivize schools to adopt sustainable practices and participate in environmental initiatives.\n\n13. **Eco-Friendly Vending Machines**: Explore partnerships with local food vendors to offer a diverse selection of products in vending machines that prioritize sustainability and convenience.\n\n14. **Gardening Kits with Recyclable Components**: Research market segments (like urban dwellers or schools) to tailor gardening kits effectively, ensuring relevance and demand in marketing strategies.\n\n15. **DIY Personal Care Products**: Host community workshops where participants can collaboratively create DIY products, fostering a sense of community while promoting zero waste practices.\n\n16. **Plastic Neutrality Programs**: Define criteria that businesses must meet to qualify for plastic neutrality, ensuring transparency and encouraging meaningful participation in sustainability efforts.\n\n17. **Plastic-Free Grocery Stores**: Highlight successful case studies of existing plastic-free grocery stores or markets to serve as models for new initiatives.\n\n18. **Innovative Composting Solutions**: Provide examples of successful composting initiatives from other communities to illustrate best practices and potential implementations.\n\n19.
```


```
**Mobile Apps for Plastic Waste Tracking**: Include engaging features like gamification, social sharing capabilities, and integration with local sustainability rewards programs to enhance user experience.\n\n20. **Public Awareness Campaigns**: Recommend specific themes (e.g., ocean conservation, wildlife protection) or creative approaches (like storytelling or humor) to resonate strongly with target audiences in awareness campaigns.\n\nThese revisions aim to enhance clarity, practicality, and engagement, making the ideas more actionable and impactful for addressing plastic waste reduction.", type='TextMessage'), TextMessage(source='reviewer', models_usage=RequestUsage(prompt_tokens=2064, completion_tokens=68), metadata={}, content="APPROVE\n\nThis revised list is well-thought-out and addresses the feedback effectively. Each suggestion is clearer, more practical, and focused on engagement and implementation. You've introduced specific strategies, collaborative elements, and examples that can help elevate the initiatives. The points are actionable and demonstrate a comprehensive approach to tackling plastic waste. Well done!", type='TextMessage'), TextMessage(source='summary', models_usage=RequestUsage(prompt_tokens=105, completion_tokens=61), metadata={}, content='The user requested ideas for reducing plastic waste. The final feedback expressed approval of a revised list of suggestions, highlighting that it effectively addressed the initially requested feedback. The reviewer praised the clarity, practicality, and comprehensiveness of the strategies, noting that they included actionable points and collaborative elements to enhance implementation.', type='TextMessage'), StopMessage(source='DiGraphStopAgent', models_usage=None, metadata={}, content='Digraph execution is complete', type='StopMessage')] stop_reason='Stop message received')
```

---