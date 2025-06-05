"""
1. Initial Setup
"""

# 1a. Imports
import asyncio
import sys
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.ollama import OllamaChatCompletionClient as set_model
from commonutil import parse_pdf

# 1b. Model Clients
qwen3moe_30b = set_model(
    model="qwen3:30b-a3b",
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
deepR1distill_7b = set_model(
    model="deepseek-r1:7b-qwen-distill-q4_K_M", temperature=0, seed=42
)
deepR1_32b = set_model(model="deepseek-r1:32b", temperature=0, seed=42)
llama32fp16_3b = set_model(model="llama3.2:3b-instruct-fp16", temperature=0, seed=42)
phi35_3b = set_model(model="phi3.5:3.8b", temperature=0, seed=42)
devstral_24b = set_model(
    model="devstral:24b",
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

"""
2. Agent Setup
"""

# 2a. Main resume parsing agent entry point
# ── Resume-parsing agent ───────────────────────────────────────────────
resume_parse_agt = AssistantAgent(
    name="ResumeParseAgt",
    description=(
        "Reads a PDF resume via parse_pdf and returns **un-edited** markdown, "
        "organised into seven sections: Personal Info, Skills, Projects, "
        "Education, Coursework, Certifications, Work Experience."
    ),
    model_client=qwen3moe_30b,
    model_client_stream=True,
    reflect_on_tool_use=False,  # ← was False; must be True for post-tool processing
    system_message="""
    You are a strict resume-parsing assistant.

    Workflow:
    1. The user supplies a relative file path such as ‘resumes/resume_ex.pdf’.
    2. Call **parse_pdf** with exactly that path.
    3. Take the markdown string returned by the tool and **do not alter, rephrase, or re-format any text**.
    4. Categorise every line into one of the following sections.
    • Personal Info  
    • Skills  
    • Projects  
    • Education  
    • Coursework  
    • Certifications  
    • Work Experience
    5. Output markdown with this exact template (leave a section blank if nothing fits):

    ### Personal Info  
    <original lines and headers here>

    ### Skills  
    <original lines and headers here>

    ### Projects  
    <original lines and headers here>

    ### Education  
    <original lines and headers here>

    ### Coursework  
    <original lines and headers here>

    ### Certifications  
    <original lines and headers here>

    ### Work Experience  
    <original lines and headers here>
    
    Rules:
    – **No paraphrasing, summarising, or punctuation edits.**  
    – **No duplicated lines across sections.**  
    – Preserve bullets, line breaks, symbols, and casing exactly as received.  
    – If in doubt about a line’s best section, choose the single most appropriate one; never repeat it.
""",
    tools=[parse_pdf],
)

# ── Education Extractor Agent ──────────────────────────────────────────
education_extract_agt = AssistantAgent(
    name="EducationExtractAgt",
    description=(
        "Receives markdown output from ResumeParseAgt and extracts only the "
        "content relevant to the 'Education' section, presenting it exactly "
        "as it appears in the input."
    ),
    model_client=qwen3moe_30b,
    model_client_stream=True,
    system_message="""
    You will receive a parsed resume in markdown format.
    Your sole task is to identify and extract all lines of text that fall under the 'Education' section.
    Present this extracted information exactly as it appears in the input.
    Do not add any extra formatting, headings, or commentary.
    Focus on identifying and extracting all lines that describe educational qualifications, degrees, institutions, and dates of attendance.
    If no education section is found, output nothing or a simple message like "No education section found."
""",
)


"""
3. GraphFlow Setup
"""
# 3a. Setup agent and entry point
builder = DiGraphBuilder()
builder.add_node(resume_parse_agt)
builder.add_node(education_extract_agt)  # Add the new agent to the graph
builder.set_entry_point(resume_parse_agt)

# 3b. Add the edges now in the manner the program should run
builder.add_edge(resume_parse_agt, education_extract_agt)

# 3c. Define the final flow for graph
flow = GraphFlow(participants=builder.get_participants(), graph=builder.build())


"""
4. Main Function 
"""


# 4a. Main function
async def main() -> None:
    initial_prompt = "Please parse my resume at resumes/resume_1pg.pdf"
    await Console(flow.run_stream(task=initial_prompt), output_stats=True)
    # await resume_parse_agt.close()
    # await education_extract_agt.close()


if __name__ == "__main__":
    asyncio.run(main())
