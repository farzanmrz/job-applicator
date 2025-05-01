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
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.ollama import OllamaChatCompletionClient
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

    # Basic usage example
    return MarkItDown().convert(file_path).text_content


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
# agt_edu = AssistantAgent(
#     name="edu_agent",
#     model_client=ollama_client2,
#     system_message="""You are a helpful agent tasked with determining whether the text from the resume file contains education information. Look for these indicators:

#         1. Keywords like 'Education', 'Degree', 'University', 'College', 'School', 'GPA', 'Bachelors', 'Masters', 'Highschool'
#         2. Synonyms of 'Education' like 'Academic Background', 'Academic Qualifications', 'Educational Background', 'Academic History'
#         3. Usually the education section contains the most recent 2 academic qualifications

#     First, tell the user what education entries you found (if any).
#     Then end your message with "EDU DONE" on a new line.

#     Example:
#     "I found education entries from Drexel University (Master's) and Virginia Tech (Bachelor's).
#     EDU DONE"

#     or

#     "No education information found in this resume.
#     EDU DONE"
#     """,
# )

# Define the agent to extract the education section from the PDF
agt_edu = AssistantAgent(
    name="edu_agent",
    model_client=ollama_client2,  # Using the potentially more capable llama3.2 model
    system_message="""You are an expert agent specializing in extracting structured education information from resume text. Your task is to analyze the text provided by the previous agent and identify all distinct education entries.

    **Instructions:**

    1.  **Analyze Input:** Carefully read the text provided by the previous agent. Focus ONLY on sections related to 'Education', 'Academic Background', 'Qualifications', etc.
    2.  **Identify Entries:** Locate each distinct educational qualification listed (e.g., different degrees or universities mentioned).
    3.  **Extract Details:** For EACH entry found, extract the following details IF they are present in the text:
        * `College Name`: The full name of the university, college, or school.
        * `Major/Degree`: The name of the degree (e.g., Master of Science, Bachelor of Arts) AND the field of study (e.g., Artificial Intelligence, Computational Modelling).
        * `Minor`: Any listed minor fields of study.
        * `GPA`: The Grade Point Average listed. Include context if provided (e.g., 'Current GPA: 4.0').
        * `Start Date`: The start date of the program (often not present in resumes).
        * `Graduation Date`: The date of graduation or the expected graduation date. Include context like '(Expected)' if mentioned.
    4.  **Handle Missing Data:** If a specific detail (like Minor, GPA, Start Date) is NOT mentioned for an entry *in the provided text*, use "N/A" for that field in your output. **Crucially, DO NOT invent information or fill fields with assumptions or garbage.** Only report what is explicitly stated.
    5.  **Format Output:** Present the extracted information using the following strict format. Start with the introductory sentence. List each entry clearly numbered.

        ```text
        Based on the provided text, here are the education entries found:

        Entry 1:
        - College Name: [Extracted Name or N/A]
        - Major/Degree: [Extracted Major/Degree or N/A]
        - Minor: [Extracted Minor or N/A]
        - GPA: [Extracted GPA or N/A]
        - Start Date: [Extracted Start Date or N/A]
        - Graduation Date: [Extracted Graduation Date or N/A]

        Entry 2:
        - College Name: [Extracted Name or N/A]
        - Major/Degree: [Extracted Major/Degree or N/A]
        - Minor: [Extracted Minor or N/A]
        - GPA: [Extracted GPA or N/A]
        - Start Date: [Extracted Start Date or N/A]
        - Graduation Date: [Extracted Graduation Date or N/A]

        ... (repeat for each distinct entry found) ...

        EDU DONE
        ```

    6.  **No Education Found:** If, after careful analysis, you cannot find any clear education entries in the provided text, output ONLY the following lines:
        ```text
        No education information found in the provided text.
        EDU DONE
        ```
    7.  **Termination:** Ensure your entire response ends EXACTLY with "EDU DONE" on a new, separate line. There should be nothing after "EDU DONE".

    **Example Output (Based on the resume text you provided earlier):**

    ```text
    Based on the provided text, here are the education entries found:

    Entry 1:
    - College Name: Drexel University
    - Major/Degree: Master of Science in Artificial Intelligence and Machine Learning
    - Minor: N/A
    - GPA: Current GPA: 4.0
    - Start Date: N/A
    - Graduation Date: June 2025 (Expected)

    Entry 2:
    - College Name: Virginia Tech
    - Major/Degree: Bachelor of Science in Computational Modelling and Data Analytics
    - Minor: CS and Mathematics
    - GPA: N/A
    - Start Date: N/A
    - Graduation Date: May 2022

    EDU DONE
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
    # result = await parse_pdf(resume_path)

    # # Print the result
    # print(result)


if __name__ == "__main__":
    asyncio.run(main())
