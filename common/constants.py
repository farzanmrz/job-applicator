# Imports
import sys
from pathlib import Path

from docling.document_converter import DocumentConverter

sys.path.insert(0, str(Path(__file__).parent.parent))

"""
Prompts
"""

# Main markdown for the resume and LinkedIn data
MD_RESUME = (
    DocumentConverter()
    .convert(Path(__file__).parent.parent / "data" / "resume" / "resume_1pg.pdf")
    .document.export_to_markdown()
)
MD_LKD = (
    DocumentConverter()
    .convert(Path(__file__).parent.parent / "data" / "lkd" / "lkd1.pdf")
    .document.export_to_markdown()
)

"""
Model Configs Setup
"""


# Creation func
def create_model_config(model_name: str) -> dict:
    config = {
        "model": model_name,
        "temperature": 0,
        "seed": 42,
    }

    # Add provider-specific info based on the model name
    if "qwen" in model_name:
        config["model_info"] = MODEL_INFO_QWEN
    elif "deepseek" in model_name:
        config["model_info"] = MODEL_INFO_DEEPSEEK

    return config


# Info
MODEL_INFO_QWEN = {
    "family": "unknown",
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "vision": False,
    "multiple_system_messages": False,
}

# Configs
qwen3_30b = create_model_config("qwen3:30b-a3b")
deepR1distill_7b = create_model_config("deepseek-r1:7b-qwen-distill-q4_K_M")
llama32fp16_3b = create_model_config("llama3.2:3b-instruct-fp16")


def main():
    """
    Main function to run the script.
    """
    print("Resume Markdown:")
    print(MD_RESUME)
    print("\nLinkedIn Markdown:")
    print(MD_LKD)


if __name__ == "__main__":
    main()
