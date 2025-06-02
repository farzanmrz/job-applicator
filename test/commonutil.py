import os

import yaml
from smolagents import PromptTemplates


def get_prompt_template(yaml_file_name: str) -> PromptTemplates:
    """
    Loads prompt templates from a YAML file and ensures it's in the required PromptTemplates format.

    Args:
        yaml_file_name: The name of the YAML file (e.g., "usrval_prompt.yaml").
                        Assumes the file is located in a 'prompts' subdirectory
                        relative to the calling script.

    Returns:
        A PromptTemplates object with system_prompt and default planning,
        managed_agent, and final_answer structures.

    Raises:
        FileNotFoundError: If the specified YAML file does not exist.
        yaml.YAMLError: If the YAML file is malformed.
        ValueError: If the loaded YAML is not a dictionary or lacks a 'system_prompt'.
    """
    prompt_file_path = os.path.join(
        os.path.dirname(__file__), "prompts", yaml_file_name
    )

    with open(prompt_file_path, "r") as f:
        loaded_prompt_templates: PromptTemplates = yaml.safe_load(f)

    if (
        not isinstance(loaded_prompt_templates, dict)
        or "system_prompt" not in loaded_prompt_templates
    ):
        raise ValueError(
            f"Prompt file {yaml_file_name} must be a dictionary containing at least a 'system_prompt' key."
        )

    # Ensure all expected keys for PromptTemplates are present, filling with defaults if necessary
    default_planning = {
        "initial_plan": "",
        "update_plan_pre_messages": "",
        "update_plan_post_messages": "",
    }
    default_managed = {"task": "", "report": ""}
    default_final_answer_summary = {"pre_messages": "", "post_messages": ""}

    loaded_prompt_templates.setdefault("planning", default_planning)
    loaded_prompt_templates.setdefault("managed_agent", default_managed)
    loaded_prompt_templates.setdefault("final_answer", default_final_answer_summary)

    return loaded_prompt_templates
