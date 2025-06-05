import asyncio
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient as set_model

# Import our custom utility for PDF parsing
from commonutil import parse_pdf
from pydantic import BaseModel


# 1. Pydantic Models and Enums for Education Extraction (copied from resume_parser2.py)
class EducationLevel(str, Enum):
    HS = "HS"
    Assoc = "Assoc"
    UG = "UG"
    PG = "PG"
    PhD = "PhD"
    PD = "PD"


class EducationStatus(str, Enum):
    Complete = "Complete"
    Ongoing = "Ongoing"
    Drop = "Drop"


class EducationContainer(BaseModel):
    class EducationAgentResponse(BaseModel):
        ed_lvl: EducationLevel
        ed_org: str
        ed_degree: str
        ed_startdate: datetime
        ed_enddate: datetime
        ed_status: EducationStatus
        ed_majors: List[str]
        ed_minors: Optional[str]
        ed_location: str
        ed_gpa: float

    education: list[EducationAgentResponse]


# 2. Model Client Definition (copied from resume_parser2.py)
qwen3moe_30b = set_model(
    model="qwen3:1.7b",
    model_info={
        "family": "unknown",
        "function_calling": True,
        "json_output": True,
        "structured_output": True,
        "vision": False,
        "multiple_system_messages": False,
    },
    temperature=0,
    seed=42,
)

# 3. Education Extractor Agent Definition (copied from resume_parser2.py)
education_extract_agt = AssistantAgent(
    name="EducationExtractAgt",
    description=(
        "Receives markdown output from ResumeParseAgt and extracts only the "
        "content relevant to the 'Education' section, presenting it exactly "
        "as it appears in the input."
    ),
    model_client=qwen3moe_30b,
    system_message="""
    You will receive a parsed resume in markdown format.

    Your task is strictly limited to extracting content specifically from the "Education" section. Ensure accuracy by adhering to these detailed guidelines:

    1. Clearly identify the "Education" heading and extract all content immediately following this heading until the next heading at the same or higher level.

    2. Extract text exactly as it appears, preserving:
    - Degree names (e.g., Bachelor of Science, Master of Science)
    - Education levels explicitly or implicitly indicated (e.g., Undergraduate, Graduate, Master's, PhD, High School, Associate Degree)
    - Dates (including start dates, end dates, graduation or expected graduation dates, or any durations provided)
    - Names and locations of educational institutions
    - Majors, minors, and GPAs if mentioned

    3. Maintain original formatting, including line breaks, punctuation, and spacing.

    4. Do NOT add any commentary, explanations, or headings of your own.

    5. If no clearly marked "Education" section exists or the section is empty, respond precisely with: "No education section found."

    Your output must strictly match the extracted text or the indicated response if absent.
    """,
    output_content_type=EducationContainer,
)


# 4. Main Asynchronous Function to run the single agent flow
async def run_education_extraction():
    print("Step 1: Parsing resume PDF to get markdown content...")
    # Use the parse_pdf function from commonutil to get the resume content
    resume_filename = "resume_1pg.pdf"  # Example resume file
    resume_markdown = parse_pdf(filename=resume_filename, is_resume=True)

    if "Error:" in resume_markdown:
        print(f"Error parsing resume PDF: {resume_markdown}")
        return

    print(
        "\nStep 2: Resume content successfully parsed. Feeding to EducationExtractAgt..."
    )
    # Prepare the user message with the parsed resume content
    user_task_message = UserMessage(content=resume_markdown)

    # Setup single-agent GraphFlow
    builder = DiGraphBuilder()
    builder.add_node(education_extract_agt)
    builder.set_entry_point(education_extract_agt)
    graph = builder.build()
    flow = GraphFlow(participants=builder.get_participants(), graph=graph)

    print("\nStep 3: Running the Education Extraction Agent...")
    # Run the flow and capture the result
    # The Console will stream the output, and the flow.run_stream returns a TaskResult
    task_result = await Console(
        flow.run_stream(task=user_task_message), output_stats=True
    )

    print("\nStep 4: Education Extraction Agent finished. Displaying output...")
    # The final message from the agent should contain the structured output
    # We need to iterate through the messages to find the last one from our agent
    extracted_education = None
    for message in task_result.messages:
        if message.source == education_extract_agt.name and isinstance(
            message.content, EducationContainer
        ):
            extracted_education = message.content
            break
        elif message.source == education_extract_agt.name and isinstance(
            message.content, str
        ):
            # Fallback for string output if Pydantic parsing fails or agent returns plain text
            extracted_education = message.content
            break

    if extracted_education:
        print("\n--- Extracted Education Information ---")
        print(extracted_education)
        print("--- End of Extracted Education Information ---")
    else:
        print(
            "No structured education information extracted or found in agent's final message."
        )


# 5. Execution Block
if __name__ == "__main__":
    asyncio.run(run_education_extraction())
