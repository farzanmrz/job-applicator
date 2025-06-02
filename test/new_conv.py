# Imports
import json

from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from phoenix.otel import register as phoenix_register
from smolagents import LiteLLMModel, ToolCallingAgent, tool

# Constants
USER_FILE = "users.json"
MODEL_ID = "ollama_chat/deepseek-r1:14b"
API_BASE = "http://localhost:11434"


@tool
def get_user_info(usr_name: str) -> str:
    """
    Checks if the user exists in users.json and returns their ID and name.

    Args:
        usr_name: The name of the user to search for (case-insensitive).

    Returns:
        A string describing whether the user was found and their ID if so.
    """
    try:
        with open(USER_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return "User data file not found. This is my final answer."
    except json.JSONDecodeError:
        return "User data file is not valid JSON. Please treat this as my final answer."

    for user in data.get("usrs", []):
        if user["usr_name"].lower() == usr_name.lower():
            return f"User found: ID={user['usr_id']}, Name={user['usr_name']}. Final answer."

    return f"No user found with name '{usr_name}'. This is the final answer."


# Test Runner Function
def run_test(task: str):
    phoenix_register()
    SmolagentsInstrumentor().instrument()

    model = LiteLLMModel(model_id=MODEL_ID, api_base=API_BASE)

    agent = ToolCallingAgent(
        tools=[get_user_info],
        model=model,
        name="user_lookup_agent",
        description="Looks up user info by name.",
        max_steps=3,
    )

    print(f"Test input: {task}")
    response = agent.run(task=task)
    print(f"Agent: {response}")


# Run with Test Inputs
if __name__ == "__main__":
    run_test("Can you find Kevin?")
    run_test("Is Farzan a user?")
    run_test("Check if Alice exists")
    run_test("Tell me about bob")
    run_test("Find Ramesh")
