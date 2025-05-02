# Core Agent Imports needed for the task
import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import Any, Dict, Optional, Type, get_type_hints

# from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pypdf import PdfReader

# Load environment variables at module level
load_dotenv()
print("Environment variables loaded.")
import openparse
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.ollama import OllamaChatCompletionClient
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TesseractCliOcrOptions,
)
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from markitdown import MarkItDown

# Define the Ollama model client
ollama_client = OllamaChatCompletionClient(model="llama3.2")
ollama_client2 = OllamaChatCompletionClient(model="llama3.2")

# Define the path to the PDF file
resume_path = "docs/resume_1pg.pdf"


# Define a simple function tool that the agent can use to extract raw text from the PDF
async def parse_pdf(file_path: str) -> str:

    # If file unavailable, return error message
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return "File invalid"

    # Parse content using docling
    parsed_content = (
        DocumentConverter().convert(file_path).document.export_to_markdown()
    )
    # print(parsed_content)
    return parsed_content

    # Basic usage example
    # return MarkItDown().convert(file_path).text_content


# Define a termination condition that stops the task if the critic approves.
terminate_message = TextMentionTermination(text="EDU DONE", sources=["edu_agent"])

# Define basic extractor agent to parse the PDF file
agt_extract = AssistantAgent(
    name="extractor_agent",
    model_client=ollama_client,
    tools=[parse_pdf],
    system_message="""You are a helpful parsing agent who will parse the full path of the provided PDF file using the parsed_pdf tool and return all the parsed text.""",
    reflect_on_tool_use=True,
)

# Define the agent to extract the education section from the PDF
agt_edu = AssistantAgent(
    name="edu_agent",
    model_client=ollama_client2,  # Using the potentially more capable llama3.2 model
    system_message="""You are an expert education extraction agent. Your task is to read the markdown-formatted text provided by the extraction agent and output a JSON array containing **every** education entry found. Do not stop after a single entry.

    Each object must include these keys exactly as named. Required fields must always be present; optional fields must be set to `"N/A"` if not found. Do not invent or assume any data.

    Field definitions:
    - `ed_lvl` (enum, required): Highest level abbreviation found:
    - HS (High School)
    - Assoc (Associate)
    - UG (Undergraduate / Bachelor)
    - PG (Postgraduate / Master)
    - PhD (Doctorate)
    - PD (Postdoctoral)
    - `ed_org` (string, required): Full name of the institution.
    - `ed_status` (enum, required): One of: Complete, Ongoing, Drop.
    - `ed_majors` (array of strings, required): List each degree title and field of study combined (e.g., “Master of Science in Artificial Intelligence and Machine Learning”). **At least one entry** must be present.
    - `ed_startdate` (string, optional): Format “MM/YY”; if only one date appears, use `"N/A"`.
    - `ed_enddate` (string, optional): Format “MM/YY”; if only one date appears, treat it as `ed_enddate`.
    - `ed_minors` (array of strings, optional): List minors if any; if none, use `[]` or `"N/A"`.
    - `ed_location` (string, optional): City, State or City, Country if specified.
    - `ed_gpa` (number, optional): GPA as a float (e.g., `3.5`), else `"N/A"`.

    Example output (fictional data) to illustrate multiple entries:
    ```json
    
    "ed_info": {
        "ed1":{
            "ed_lvl": "UG",
            "ed_org": "Valley State University",
            "ed_status": "Complete",
            "ed_majors": ["Bachelor of Science in Biology"],
            "ed_startdate": "09/11",
            "ed_enddate": "05/15",
            "ed_minors": ["Chemistry"],
            "ed_location": "Valley Town, WA",
            "ed_gpa": 3.4
        },
        "ed2":{
            "ed_lvl": "PG",
            "ed_org": "Mountain Tech College",
            "ed_status": "Ongoing",
            "ed_majors": ["Master of Engineering in Civil Engineering"],
            "ed_startdate": "08/22",
            "ed_enddate": "N/A",
            "ed_minors": ["N/A"],
            "ed_location": "Mountain City, CO",
            "ed_gpa": 3.8
        }
    }

    Return EDU DONE when you are finished.
    ```
""",
)

# Define the resume team
resume_team = RoundRobinGroupChat(
    participants=[agt_extract, agt_edu],
    termination_condition=terminate_message,
    max_turns=5,
)


# Run the agent and stream the messages to the console.
async def main() -> None:
    await resume_team.reset()
    await Console(
        resume_team.run_stream(task="Study my resume file docs/resume_1pg.pdf")
    )
    await ollama_client.close()
    await ollama_client2.close()


if __name__ == "__main__":
    asyncio.run(main())
