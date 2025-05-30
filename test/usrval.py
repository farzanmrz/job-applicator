# === Imports ===
import json

from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from phoenix.otel import register as phoenix_register
from smolagents import LiteLLMModel, ToolCallingAgent, tool

# === Constants ===
USER_FILE = "users.json"
MODEL_ID = "ollama_chat/deepseek-r1:7b"
MODEL_HOST = "http://localhost:11434"


@tool
def val_usr(usr_name: str) -> str:
    """
    Checks whether the given username exists in the system.

    Args:
        usr_name: The name of the user to look up.

    Returns:
        A JSON string indicating:
        - If the user exists: {"status": true, "usr_id": <int>}
        - If not found: {"status": false, "usr_id_next": <int>}
        The name match is case-insensitive.
    """

    # Open users.json and load the data into memory
    with open(USER_FILE, "r") as f:
        data = json.load(f)

    # Extract the user list and next available ID
    usrs = data["usrs"]
    usr_id_next = data["usr_id_next"]

    # Normalize input for case-insensitive comparison
    usr_name_lower = usr_name.lower()

    # Search for the user by normalized name
    for usr in usrs:
        if usr["usr_name"].lower() == usr_name_lower:
            usr_id = usr["usr_id"]
            return f"User exists. Assigned ID is {usr_id}."

    # If not found, return the next available ID
    return f"User not found. Next available ID is {usr_id_next}."


# === Agent Chat Entry Point ===
def start_chat():

    # Initialize telemetry for logging and observability via Phoenix
    phoenix_register(set_global_tracer_provider=False)
    SmolagentsInstrumentor().instrument()

    # Configure LiteLLM model for use with a ToolCallingAgent
    llm_usrval = LiteLLMModel(
        model_id=MODEL_ID,
        api_base=MODEL_HOST,
    )

    # Instantiate the user validation agent
    agt_usrval = ToolCallingAgent(
        model=llm_usrval,
        tools=[val_usr],
        name="UsrValAgt",
        description="Handles username-based user identification and registration through simple validation and storage operations.",
    )

    # Inject tool metadata manually so the LLM knows it exists
    tool_info = f"""
    - {val_usr.name}: {val_usr.description}
        Takes inputs: {val_usr.inputs}
        Returns an output of type: {val_usr.output_type}
    """
    agt_usrval.prompt_templates["system_prompt"] += "\n\nAvailable tools:\n" + tool_info

    # Welcome message to the user
    print(
        "Agent: Welcome! Please tell me your username to get started. Type 'q' to quit.\n"
    )

    # Begin continuous user interaction loop
    while True:

        # Prompt for user input
        user_input = input("You: ").strip()

        # Terminate if user requests to quit
        if user_input.lower() == "q":
            print("Agent: Goodbye!")
            break

        # Pass the input to the agent and print its response
        response = agt_usrval.run(user_input)
        print(f"Agent: {response}\n")


# === Main Hook ===
if __name__ == "__main__":
    start_chat()
