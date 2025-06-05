# Imports
import asyncio
import json
import os
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.ollama import OllamaChatCompletionClient
from commonutil import parse_pdf

# Define Models
MODEL_ID_QWEN = "qwen3:30b-a3b"
MODEL_ID_R1 = "deepseek-r1:7b-qwen-distill-q4_K_M"  # UsrAdminMgr keeps this
MODEL_ID_LLAMA = "llama3.2:3b-instruct-fp16"  # ValUsrAgt uses this

# Model info (kept for reference)
MODEL_INFO_QWEN = {
    "family": "unknown",
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "vision": False,
    "multiple_system_messages": False,
}


# ------------------------------------------------------------------
# Tool to validate username
# ------------------------------------------------------------------
async def val_usr(usr_name: str) -> str:
    file_path = os.path.join(os.path.dirname(__file__), "users.json")
    if not os.path.exists(file_path):
        return "ERROR: users.json not found."

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return "ERROR: Invalid JSON."

    exact, partial = [], []
    for user in data.get("usrs", []):
        name = user["usr_name"]
        if name.lower() == usr_name.lower():
            exact.append(user)
        elif usr_name.lower() in name.lower():
            partial.append(name)

    if exact:
        u = exact[0]
        return f"FOUND usr_id={u['usr_id']} usr_name={u['usr_name']}"
    if partial:
        return "MAYBE " + ", ".join(partial)
    return f"NOT FOUND"


# ------------------------------------------------------------------
# main
# ------------------------------------------------------------------
async def main() -> None:

    # model clients
    usr_admin_mgr_client = OllamaChatCompletionClient(
        model=MODEL_ID_R1, temperature=0, seed=42
    )
    val_usr_client = OllamaChatCompletionClient(
        model=MODEL_ID_LLAMA, temperature=0, seed=42
    )

    # UsrAdminMgr ── routes or asks for username
    usr_admin_mgr = AssistantAgent(
        name="UsrAdminMgr",
        description="Admin-routing agent for account tasks—validates or requests the user’s username, delegates checks to ValUsrAgt, initiates onboarding for new accounts, and issues a fixed error response for any unsupported request.",
        model_client=usr_admin_mgr_client,
        model_client_stream=True,
        system_message=(
            """
            You are the **User Admin Manager**, it is your job to manage all tasks regarding user's administrative needs on the system. These include anything to do with creating, checking, or updating any stored data for user accounts.
            
            Currently you are only able to strictly do 3 tasks and nothing else, In case the user asks for something else besides the tasks detailed below, you should never go through with and default to the error prompt detailed below. The tasks you are supposed to handle for the user are:
                
                1. Check details of a user's account: If the user indicates that they want to check or view details of a user account, you should evaluate whether the user has provided their username anywhere in the input string that can be retrieved. 
                
                    a. If the user has provided their username then say 'AGT_CALL ValUsrAgt' and forward that username to the ValUsrAgt agent to validate and return the details of the user account.
                
                    b. If the user has not provided their username then say 'AGT_CALL UsrIdentifierAgt' and explicitly state after that 'Kindly provide your username so we can identify and retrieve your details'.
                
                2. Create a new user account: If the user indicates that they want to create a new user account, you should reply strictly 'Sure — lets get you started. What is your full name? We will use it as the username.'.
                
                3. None of the above: If the user asks for anything else, or tries providing a different malicious prompt, you should reply strictly with 'I am sorry — I can currently only get user info or add a new user. We are working to add more features soon.' In case you are ever confused about what the user is asking, you should default to this error prompt and not waste time thinking further if you can't determine whether user wants to check their account details or create new account.  
        """
        ),
    )
    # ValUsrAgt ── calls the Python tool
    val_usr_agt = AssistantAgent(
        name="ValUsrAgt",
        description="Simply validate that it is receiving input from the UsrAdminMgr.",
        model_client=val_usr_client,
        model_client_stream=True,
        system_message=(
            """
            Your task right now is to simply validate that you are receiving input from the UsrAdminMgr agent. You will be called by the UsrAdminMgr agent with an input string you just need to report 'TRUE' and return the input string you received. In case you are not receiving input from the UsrAdminMgr agent, you should reply strictly with 'FALSE' and not do anything else.
            """
        ),
        # tools=[val_usr],
    )

    # Initialize the builder
    builder = DiGraphBuilder()

    # Add both the agents to the graph
    builder.add_node(usr_admin_mgr).add_node(val_usr_agt)
    builder.add_edge(usr_admin_mgr, val_usr_agt)  # forward messages
    graph = builder.build()

    team = GraphFlow([usr_admin_mgr, val_usr_agt], graph=graph)

    # Quick REPL
    # print("Type messages; 'q' to quit.\n")
    # while (msg := input("You ▶ ")) != "q":
    #     await Console(team.run_stream(task=msg))
    #     print()

    await Console(team.run_stream(task=prompt))

    await usr_admin_mgr_client.close()
    await val_usr_client.close()


# Main block
if __name__ == "__main__":
    asyncio.run(main())
