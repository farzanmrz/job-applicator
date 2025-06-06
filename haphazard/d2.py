# Imports
import asyncio
import json
import os
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.ollama import OllamaChatCompletionClient

# Define Models
MODEL_ID_QWEN = "qwen3:30b-a3b"
MODEL_ID_R1 = "deepseek-r1:7b-qwen-distill-q4_K_M"
MODEL_ID_LLAMA = "llama3.2:3b-instruct-fp16"
MODEL_ID_PHI = "phi3.5:3.8b"

# Model info (kept for reference)
MODEL_INFO_QWEN = {
    "family": "unknown",
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "vision": False,
    "multiple_system_messages": False,
}


# Step 1. Agent Setup
usr_admin_mgr_client = OllamaChatCompletionClient(
    model=MODEL_ID_LLAMA, temperature=0, seed=42
)
val_usr_client = OllamaChatCompletionClient(
    model=MODEL_ID_LLAMA, temperature=0, seed=42
)

usr_admin_mgr = AssistantAgent(
    name="UsrAdminMgr",
    model_client=usr_admin_mgr_client,
    model_client_stream=True,
    system_message="""
You are the **User Admin Manager**, responsible for handling account detail lookups.

You are only allowed to do one thing:  
If the user asks to **check their account details**, you must reply exactly:  
AGT_CALL ValUsrAgt

If the user asks **anything else**, or if the intent is unclear, you must return reply exactly:
END

You must not try to help, explain, or do anything outside of this.
    """,
)


val_usr_agt = AssistantAgent(
    name="ValUsrAgt",
    model_client=val_usr_client,
    model_client_stream=True,
    system_message="""You must respond ONLY with one of these two exact words:

    - MISSING
    - VALID

    You must say nothing else. Do not respond to the user's intent. Do not explain. No punctuation. No formatting. Just one word.""",
)


# Terminator (final stop node)
terminator = AssistantAgent(
    name="TerminatorAgent",
    model_client=val_usr_client,
    model_client_stream=True,
    system_message="""
    You're just here to stop the flow. If you recieve the 'END' keyword then strictly print this for the user: 
    I am sorry — I can currently only get user info. We are working to add more features soon.
    """,
)


# Step 2: Graph and Flow Setup

# Create builder object and add agents
builder = DiGraphBuilder()
builder.add_node(usr_admin_mgr).add_node(val_usr_agt).add_node(terminator)

# Flow: UsrAdminMgr → ValUsrAgt
builder.add_edge(usr_admin_mgr, val_usr_agt, condition="AGT_CALL ValUsrAgt")
builder.add_edge(usr_admin_mgr, terminator, condition="END")

# Conditional loop: ValUsrAgt → UsrAdminMgr only if MISSING
builder.add_edge(val_usr_agt, usr_admin_mgr, condition="MISSING")

# Add edge: ValUsrAgt → Terminator if response is VALID
builder.add_edge(val_usr_agt, terminator, condition="VALID")


# Set entry point
builder.set_entry_point(usr_admin_mgr)

# Finalize the graph
graph = builder.build()

# GraphFlow team setup
team = GraphFlow(
    participants=[usr_admin_mgr, val_usr_agt, terminator],
    graph=graph,
    termination_condition=MaxMessageTermination(10),
)


# Step 3: Test Entry Point
async def main():
    # await Console(team.run_stream(task="Can I delete my account?"))

    # async for msg in team.run_stream(task="Can I delete my account?"):
    #     print(msg)

    from autogen_agentchat.messages import TextMessage

    async for msg in team.run_stream(task="delete my account"):
        if isinstance(msg, TextMessage):
            print("MATCH TEXT:", msg.content.strip())

    await usr_admin_mgr_client.close()

    await val_usr_client.close()


if __name__ == "__main__":
    asyncio.run(main())
