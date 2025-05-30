# user_validation.py

import json
import os
from typing import Any, Dict, List, Optional

from smolagents import CodeAgent, LiteLLMModel, PromptTemplates, tool

USER_FILE = "users.json"
# Ensure users.json exists with initial content for first run:
# {
#   "usr_id_next": 1,
#   "usrs": []
# }

# --- LLM Configuration (Agent will use this) ---
OLLAMA_MODEL_ID = "ollama_chat/deepseek-r1:14b"
OLLAMA_API_BASE = "http://localhost:11434"


# --- Helper functions for file operations (internal to this module) ---
def load_usr() -> Dict[str, Any]:
    with open(USER_FILE, "r") as f:
        data = json.load(f)
    return data


def save_usr(data: Dict[str, Any]):
    with open(USER_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Tools for the UserValidationAgent ---


@tool
def get_usr(usr_name: str) -> Optional[Dict[str, Any]]:
    """
    Finds a user by exact name match (case-insensitive).
    Returns the user dictionary if found (e.g., {"usr_id": 1, "usr_name": "Test User"}), otherwise None.

    Args:
        usr_name: The name of the user to find.
    """
    data = load_usr()
    users_list = data.get("usrs", [])
    if not isinstance(users_list, list):
        users_list = []

    for user in users_list:
        if (
            isinstance(user, dict)
            and user.get("usr_name", "").lower() == usr_name.lower()
        ):
            return user
    return None


@tool
def add_usr(usr_name: str) -> Dict[str, Any]:
    """
    Adds a new user with a unique ID to users.json using "usr_id_next".
    Returns the newly created user dictionary (e.g., {"usr_id": 1, "usr_name": "New User"}).

    Args:
        usr_name: The name of the user to add.
    """
    data = load_usr()

    next_id = data.get("usr_id_next", 1)
    users_list = data.get("usrs", [])
    if not isinstance(users_list, list):
        users_list = []
        data["usrs"] = users_list

    new_user_entry = {"usr_id": next_id, "usr_name": usr_name}
    users_list.append(new_user_entry)

    data["usr_id_next"] = next_id + 1

    save_usr(data)
    return new_user_entry


# user_validation.py

import json
import os
from typing import Any, Dict, List, Optional

# Updated smolagents imports
from smolagents import (
    CodeAgent,
    FinalAnswerPromptTemplate,
    LiteLLMModel,
    ManagedAgentPromptTemplate,
    PlanningPromptTemplate,
    PromptTemplates,
    tool,
)

# ... (USER_FILE, OLLAMA_MODEL_ID, OLLAMA_API_BASE, load_usr, save_usr, get_usr, add_usr definitions remain the same) ...


# --- UserValidationAgent ---

# USER_VALIDATION_SYSTEM_PROMPT (as defined above)
USER_VALIDATION_SYSTEM_PROMPT = """You are a User Validation Agent.
Your task is to process a given username.
You must determine if a user with that name already exists.
If the user exists, you must state that the name is taken and include their usr_id.
If the user does not exist, you must add the new user and state that they have been created, including their new usr_id.
Use the `final_answer` tool to provide your conclusion.

You have access to the following tools:
- get_usr(usr_name: str) -> dict | None: Checks if a user exists by name. Returns user data if found, else None.
- add_usr(usr_name: str) -> dict: Adds a new user. Returns the new user data.

Workflow:
1. Use `get_usr` to check if the provided `usr_name` exists.
2. If the user exists (tool returns user data), your final answer should be: "User '[usr_name]' already exists with ID [usr_id]. Please use a different name."
3. If the user does not exist (tool returns None), use `add_usr` to create them. Your final answer should be: "User '[usr_name]' created successfully with ID [usr_id]."
"""

# Define all prompt template components
simplified_planning_template = PlanningPromptTemplate(
    plan="""\
You are the UserValidationAgent.
Your current task is to process a username.
Your available tools are: get_usr, add_usr, final_answer.
1. Facts Survey:
   - What is the username to process?
   - What needs to be determined about this username?
2. Plan:
   Outline a concise, step-by-step plan to validate this username using your tools and provide a final answer.
   End your plan with '\n<end_plan>'.
""",
    update_plan_pre_messages="""\
Reviewing progress on the current task.
Consider your previous actions, observations, and any known facts.
""",
    update_plan_post_messages="""\
Based on your review:
1. Updated Facts Survey:
   - What key information has been learned?
   - What still needs to be determined or done?
2. Updated Plan:
   Provide an updated, concise step-by-step plan to complete the user validation.
   Ensure your plan leads to a `final_answer`.
   End your plan with '\n<end_plan>'.
""",
)

minimal_managed_agent_template = ManagedAgentPromptTemplate(task="", report="")

simplified_final_answer_template = FinalAnswerPromptTemplate(
    pre_messages="""\
You are about to provide the final answer for the user validation task.
Review your previous steps and observations.
Summarize the outcome (e.g., was the user found, were they created, what are their details?).
""",
    post_messages="""\
Now, based on your summary, construct the precise string argument for the `final_answer()` tool, adhering to the format specified in your main system prompt's workflow instructions.
""",
)

# Create the full PromptTemplates object
custom_prompt_templates = PromptTemplates(
    system_prompt=USER_VALIDATION_SYSTEM_PROMPT,
    planning={
        "initial_plan": simplified_planning_template["plan"],
        "update_plan_pre_messages": simplified_planning_template[
            "update_plan_pre_messages"
        ],
        "update_plan_post_messages": simplified_planning_template[
            "update_plan_post_messages"
        ],
    },
    managed_agent=minimal_managed_agent_template,
    final_answer=simplified_final_answer_template,
)

# Initialize LLM for the agent
llm_for_agent = LiteLLMModel(
    model_id=OLLAMA_MODEL_ID,
    api_base=OLLAMA_API_BASE,
)

# Initialize the UserValidationAgent
user_validation_agent = CodeAgent(
    name="UserValidationAgent",
    description="Validates user names by checking existence and adding new users if they don't exist.",
    model=llm_for_agent,
    tools=[get_usr, add_usr],
    managed_agents=[],
    add_base_tools=False,
    prompt_templates=custom_prompt_templates,
    planning_interval=1,  # MAKE PLANNING ACTIVE (e.g., plan before every action step)
    max_print_outputs_length=200,  # Increased slightly from your example for better plan/thought visibility
    provide_run_summary=False,
    final_answer_checks=None,
    stream_outputs=True,
    additional_authorized_imports=[],
    verbosity_level=2,  # Keep verbosity high to see planning and final answer thoughts
    max_steps=5,  # Max 5 action steps (planning steps are separate)
    executor_type="local",
    executor_kwargs=None,
    use_structured_outputs_internally=False,
)

# --- Test Harness ---
if __name__ == "__main__":
    from openinference.instrumentation.smolagents import SmolagentsInstrumentor
    from phoenix.otel import register as phoenix_register

    phoenix_register()
    SmolagentsInstrumentor().instrument()
    print("Telemetry enabled. Ensure Phoenix server is running.")

    print(
        "--- Testing UserValidationAgent with Active Planning & Final Answer Prompts ---"
    )

    initial_state = {"usr_id_next": 1, "usrs": []}
    save_usr(initial_state)
    print(f"Initialized {USER_FILE} to: {json.dumps(initial_state, indent=2)}")

    test_names = ["Gandalf", "Frodo", "Gandalf"]

    for name_to_test in test_names:
        print(f"\n>>> Processing name: '{name_to_test}'")
        task_prompt = f"Process username: '{name_to_test}'."

        agent_response = user_validation_agent.run(
            task=task_prompt,
            stream=False,
            reset=False,
            images=None,
            additional_args=None,
            max_steps=user_validation_agent.max_steps,
        )
        print(f"Agent Response: {agent_response}")
        print(f"Current {USER_FILE} content: {json.dumps(load_usr(), indent=2)}")
