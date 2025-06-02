# === Imports ===
import json
import os

import yaml  # Added for YAML loading
from commonutil import load_prompt_template_from_yaml
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from phoenix.otel import register as phoenix_register
from smolagents import LiteLLMModel, PromptTemplates, ToolCallingAgent, tool

# === Constants ===
USER_FILE = "users.json"
MODEL_ID = "ollama_chat/deepseek-r1:14b"
MODEL_HOST = "http://localhost:11434"
PROMPT_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "prompts", "usrval_prompt.yaml"
)

# custom_system_prompt = """You are a highly specialized user validation assistant. You MUST strictly follow the two-step process outlined below and produce JSON outputs in the exact format specified.

# **Process:**

# 1.  **Receive Username & Call `val_usr`:**
#     * When you are given a username, your immediate and ONLY first action is to call the `val_usr` tool.
#     * To do this, you MUST output a JSON object formatted EXACTLY like this:
#         `{"name": "val_usr", "arguments": {"usr_name": "THE_USERNAME_STRING"}}`
#         (Replace THE_USERNAME_STRING with the actual username you received).

# 2.  **Receive `val_usr` Result & Call `final_answer`:**
#     * After you call `val_usr`, the system will give you back a string result (e.g., "User exists. ID is 5." or "User not found. Next ID is 10."). Let's call this string the `VALIDATION_RESULT`.
#     * Your immediate and ONLY second action is to take this `VALIDATION_RESULT` and pass it to the `final_answer` tool.
#     * To do this, you MUST output a JSON object formatted EXACTLY like this:
#         `{"name": "final_answer", "arguments": {"answer": "THE_VALIDATION_RESULT"}}`
#         (Replace THE_VALIDATION_RESULT with the actual string result you received from `val_usr`).

# **CRITICAL JSON Output Format for ALL Tool Calls:**
# * Every time you decide to call a tool (`val_usr` or `final_answer`), your entire output MUST be a single JSON object.
# * This JSON object MUST have exactly two top-level keys:
#     1.  `"name"`: (string) The name of the tool you are calling.
#     2.  `"arguments"`: (object) An object containing the arguments for that tool.
# * **DO NOT** use any other top-level keys in your JSON output, such as "observation", "error", "thought", or "code".

# **Available Tools (These are the ONLY tools you can use):**

# - `val_usr`: Checks whether the given username exists in the system.
#     Takes inputs: `{'usr_name': {'type': 'string', 'description': 'The name of the user to look up.'}}`
#     Returns an output of type: `string`

# - `final_answer`: Takes the string result from 'val_usr' and provides it as the final answer for the current task.
#     Takes inputs: `{'answer': {'type': 'string', 'description': 'The string result previously obtained from the val_usr tool.'}}`
#     Returns an output of type: `string`

# Strictly adhere to this two-step process and the JSON formatting rules. Do not add extra thoughts or commentary outside of this structure if not explicitly asked.
# Now begin!
# """

# # Create the prompt_templates dictionary
# # For unused prompt types, provide empty structures to satisfy PromptTemplates typing
# custom_prompt_templates: PromptTemplates = {
#     "system_prompt": custom_system_prompt,
#     "planning": {
#         "initial_plan": "",
#         "update_plan_pre_messages": "",
#         "update_plan_post_messages": "",
#     },
#     "managed_agent": {"task": "", "report": ""},
#     "final_answer": {
#         "pre_messages": "",
#         "post_messages": "",
#     },  # Note: This is for a different 'final_answer' mechanism, not the tool.
# }


@tool
def val_usr(usr_name: str) -> str:
    """
    Checks whether the given username exists in the system.

    Args:
        usr_name: The name of the user to look up.

    Returns:
        A descriptive string indicating if the user exists and their ID,
        or that the user was not found and the next available ID.
        Example: "User exists. Assigned ID is 2." or "User not found. Next available ID is 3."
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

    loaded_prompt_templates = load_prompt_template_from_yaml("usrval_prompt.yaml")

    # Initialize telemetry for logging and observability via Phoenix
    phoenix_register(set_global_tracer_provider=True)
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
        description="Handles username-based user identification. First, use the 'val_usr' tool to check the username. Then, use the 'final_answer' tool to provide the exact result from 'val_usr'.",
        add_base_tools=True,
        prompt_templates=loaded_prompt_templates,
    )
    # print("DEBUG: Effective System Prompt Being Used by UsrValAgt:")
    # print("----------------------------------------------------")
    # print(agt_usrval.prompt_templates["system_prompt"])
    # print("----------------------------------------------------")

    # Welcome message to the user
    print(
        "Agent: Welcome! Please tell me your username to get started. Type 'q' to quit.\n"
    )

    # Begin continuous user interaction loop
    while True:

        # Prompt for user inputg
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
