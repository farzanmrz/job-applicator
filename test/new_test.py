# loop_minimal.py

import asyncio

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination, TextMessageTermination
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_ext.models.ollama import OllamaChatCompletionClient

# === Constants ===
MODEL_ID = "llama3.2:3b-instruct-fp16"
MODEL_TEMP = 0
MODEL_SEED = 42

# === Model Client ===
model_client = OllamaChatCompletionClient(
    model=MODEL_ID, temperature=MODEL_TEMP, seed=MODEL_SEED
)

# === Agents ===
usr_admin_mgr = AssistantAgent(
    name="UsrAdminMgr",
    model_client=model_client,
    model_client_stream=False,
    system_message="""
You are the User Admin Manager.

If the user input is exactly 'q', say: GOODBYE and stop.

For any other input, reply with:
AGT_CALL UserProxyAgent
Do not explain anything else.
""",
)

user_proxy = UserProxyAgent(name="UserProxyAgent")

# === Graph Setup ===
builder = DiGraphBuilder()
builder.add_node(usr_admin_mgr).add_node(user_proxy)

# Loop: UsrAdminMgr → UserProxyAgent (if not quitting)
builder.add_edge(usr_admin_mgr, user_proxy, condition="AGT_CALL UserProxyAgent")

# Termination: when UsrAdminMgr says "GOODBYE"
termination = TextMentionTermination(text="q", sources=["UserProxyAgent"])

builder.set_entry_point(usr_admin_mgr)
graph = builder.build()

team = GraphFlow(
    participants=[usr_admin_mgr, user_proxy],
    graph=graph,
    termination_condition=termination,
)


async def main():
    async for _ in team.run_stream(task=""):  # ← start loop with blank task
        pass

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
