import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.ollama import OllamaChatCompletionClient

# Define the Ollama model identifier
MODEL_ID = "qwen3:30b-a3b"


# Supply the minimal metadata OllamaChatCompletionClient expects
model_info = {
    "family": "unknown",
    "function_calling": False,
    "json_output": False,
    "structured_output": False,
    "vision": False,
    "multiple_system_messages": False,
}


# Create one shared model client instance
client = OllamaChatCompletionClient(
    model=MODEL_ID,
    model_info=model_info,
)


# Instantiate the writer agent that drafts content
writer = AssistantAgent(
    name="writer",
    model_client=client,
    system_message="Draft a short paragraph on climate change.",
)


# Instruct the reviewer to think silently, then give visible feedback

reviewer = AssistantAgent(
    name="reviewer",
    model_client=client,
    system_message=(
        "Review the writer’s draft and suggest improvements. "
        "First think silently inside <think> ... </think>. "
        "Then, outside the think tags, write your feedback in no more than three sentences."
    ),
)


# Build a directed graph connecting writer → reviewer
builder = DiGraphBuilder()
builder.add_node(writer).add_node(reviewer)
builder.add_edge(writer, reviewer)
graph = builder.build()


# Create the GraphFlow team from the agents and graph
flow = GraphFlow(
    participants=[writer, reviewer],
    graph=graph,
)


# Define the asynchronous entry point for running the flow
async def main() -> None:

    # Stream the conversation with neat console formatting
    await Console(flow.run_stream(task="Write a short paragraph about climate change."))

    # Close the model client gracefully
    await client.close()


# Execute the async main when the script is run directly
if __name__ == "__main__":

    # Launch the event loop
    asyncio.run(main())
