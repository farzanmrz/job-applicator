import asyncio
import json
import os

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


# Define a custom input function to enhance user experience
def custom_input(prompt: str) -> str:
    return input("\nYou: ")


# Define the val_usr function
async def val_usr(usr_name: str) -> str:
    """
    Validates whether the given username exists in users.json.
    """
    file_path = os.path.join(os.path.dirname(__file__), "users.json")

    if not os.path.exists(file_path):
        return "❌ Error: users.json file not found."

    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        users = data.get("usrs", [])
        for user in users:
            if user.get("usr_name", "").lower() == usr_name.lower():
                return f"✅ Username '{usr_name}' exists with ID {user['usr_id']}.\nAPPROVE"

        return f"❌ Username '{usr_name}' does not exist in the system."

    except json.JSONDecodeError:
        return "❌ Error: Invalid JSON format in users.json."


async def main():
    # Initialize the OpenAI model client
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-2024-08-06",
        # api_key="your-api-key",  # Optional if OPENAI_API_KEY environment variable is set
    )

    # Define the system message for the assistant
    system_prompt = (
        "You are a strict assistant that waits for the user to provide their username or full name before proceeding.\n"
        "Do not initiate the conversation. Once the user provides their name, call the tool `val_usr` with the name.\n"
        "If the username is found, respond with the result and include 'APPROVE' to end the conversation.\n"
        "If the username is not found, respond with:\n"
        '"Please provide your username or full name to continue."'
    )

    # Create the assistant agent
    assistant = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[val_usr],
        system_message=system_prompt,
    )

    # Create the user proxy agent with the custom input function
    user_proxy = UserProxyAgent(name="user_proxy", input_func=custom_input)

    # Define the termination condition
    termination = TextMentionTermination("APPROVE")

    # Create the team with the assistant and user proxy agents
    team = RoundRobinGroupChat(
        [assistant, user_proxy], termination_condition=termination
    )

    # Run the conversation and stream to the console
    await Console(team.run_stream())

    # Close the model client
    await model_client.close()


# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())
