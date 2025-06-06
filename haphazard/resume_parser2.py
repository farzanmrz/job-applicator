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
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel
import asyncio
import sys
from pathlib import Path
from typing import List, Sequence

from autogen_agentchat.agents import (
    AssistantAgent,
    MessageFilterAgent,
    MessageFilterConfig,
    PerSourceFilter,
)
from autogen_agentchat.messages import (
    ThoughtEvent,
    ToolCallExecutionEvent,
    ToolCallRequestEvent,
    ToolCallSummaryMessage,
)
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_core.model_context import (
    BufferedChatCompletionContext,
    UnboundedChatCompletionContext,
)
from autogen_core.models import (
    AssistantMessage,
    FunctionExecutionResultMessage,
    LLMMessage,
    SystemMessage,
    UserMessage,
)
# from commonutil import parse_pdf, pretty_dump

# 1b. Model Clients
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

qwen3moe_30b1 = set_model(
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

class ExtractionContext(UnboundedChatCompletionContext):
    """Remove Thought + ToolCall* events; keep everything else."""

    _EXCLUDE_TYPES = (
        ThoughtEvent,
        ToolCallRequestEvent,
        ToolCallExecutionEvent,
        ToolCallSummaryMessage,
    )

    async def get_messages(self) -> List[LLMMessage]:
        messages = await super().get_messages()
        # Filter out thought field from AssistantMessage.
        messages_out: List[LLMMessage] = []
        for message in messages:
            if isinstance(message, AssistantMessage):
                message.thought = None
                messages_out.append(message)
            elif isinstance(message, FunctionExecutionResultMessage):
                messages_out.append(message)
            elif isinstance(message, UserMessage):
                messages_out.append(message)
            elif isinstance(message, SystemMessage):
                messages_out.append(message)

        # return messages_out
        return messages_out

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

# ── Education Extractor Agent ──────────────────────────────────────────
education_extract_agt = AssistantAgent(
    name="EducationExtractAgt",
    description=(
        "Receives markdown output from ResumeParseAgt and extracts only the "
        "content relevant to the 'Education' section, presenting it exactly "
        "as it appears in the input."
    ),
    model_client=qwen3moe_30b,
    # model_client_stream=True,
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

class ExperienceType(str, Enum):
    full_time = "full-time"
    intern = "intern"
    research = "research"
    freelance = "freelance"


class ExperienceModality(str, Enum):
    Remote = "Remote"
    IRL = "IRL"
    Hybrid = "Hybrid"


class ExperienceInfo(BaseModel):
    exp_org: str
    exp_role: str
    exp_startdate: datetime
    exp_enddate: datetime
    exp_location: str
    exp_type: ExperienceType
    exp_desc: str
    exp_skills: List[str]  # Assuming skill names or identifiers are represented as strings
    exp_tech: Optional[List[str]] = None
    exp_action_words: Optional[List[str]] = None
    exp_modality: Optional[ExperienceModality] = None
    exp_industry: Optional[str] = None


# ── Work Experience Extractor Agent ──────────────────────────────────────────
work_ex_extract_agt = AssistantAgent(
    name="WorkExExtractAgt",
    description=(
        "Receives markdown output from ResumeParseAgt and extracts only the "
        "content relevant to the 'Work Experience' section, presenting it exactly "
        "as it appears in the input."
    ),
    model_client=qwen3moe_30b,
    # model_client_stream=True,
    system_message="""
    You will receive a parsed resume in markdown format.
    Your sole task is to identify and extract all lines of text that fall under the 'Work Experience' section.
    Present this extracted information exactly as it appears in the input.
    Do not add any extra formatting, headings, or commentary.
    Focus on identifying and extracting all lines that describe skills, technologies used, institutions, and dates of presence.
    If no work ex section is found, output nothing or a simple message like "No work ex section found."
    """,
    output_content_type=ExperienceInfo,
)

class ProjectType(str, Enum):
    research = "research"
    coursework = "coursework"
    personal = "personal"


class ProjectContainer(BaseModel):
    class ProjectInfo(BaseModel):
        proj_name: str
        proj_startdate: datetime
        proj_enddate: datetime
        proj_desc: str
        proj_skills: List[str]  # Assuming skills are represented by strings or identifiers
        proj_tech: Optional[List[str]] = None
        proj_metrics: Optional[List[str]] = None
        proj_url: Optional[str] = None
        proj_team: Optional[List[str]] = None
        proj_role: Optional[str] = None
        proj_type: Optional[ProjectType] = None
    projects: list[ProjectInfo]

# ── Project Info Extractor Agent ──────────────────────────────────────────
proj_info_extract_agt = AssistantAgent(
    name="ProjInfoExtractAgt",
    description=(
        "Receives markdown output from ResumeParseAgt and extracts only the "
        "content relevant to the 'Projects' section, presenting it exactly "
        "as it appears in the input."
    ),
    model_client=qwen3moe_30b,
    # model_client_stream=True,
    system_message="""
    You will receive a parsed resume in markdown format.
    Your sole task is to identify and extract all lines of text that fall under the 'Projects' section.
    Present this extracted information exactly as it appears in the input.
    Do not add any extra formatting, headings, or commentary.
    Focus on identifying and extracting all lines that describe skills, technologies used, institutions, and dates of duration.
    If no projects section is found, output nothing or a simple message like "No projects section found."
    """,
    output_content_type=ProjectContainer,
)

class SkillType(str, Enum):
    Soft = "Soft"
    Hard = "Hard"
    Technical = "Technical"

class SkillContainer(BaseModel):
    class SkillInfo(BaseModel):
        skill_category: str
        skill_items: List[str]
        skill_type: SkillType
        skill_lvl: Optional[str] = None  # Internal algorithm score, treated as string
        skill_exp: Optional[int] = None  # Experience in years
        skill_spread: Optional[Dict[str, str]] = None  # Mapping from project/role names to descriptions
    
    skills: list[SkillInfo]

# ── Project Info Extractor Agent ──────────────────────────────────────────
skill_info_extract_agt = AssistantAgent(
    name="SkillInfoExtractAgt",
    description=(
        "Receives markdown output from ResumeParseAgt and extracts only the "
        "content relevant to the 'Technical Skills/ Skills' section, presenting it exactly "
        "as it appears in the input."
    ),
    model_client=qwen3moe_30b,
    # model_client_stream=True,
    system_message="""
    You will receive a parsed resume in markdown format.
    Your sole task is to identify and extract all lines of text that fall under the 'Technical skills' section.
    Present this extracted information exactly as it appears in the input.
    Do not add any extra formatting, headings, or commentary.
    Focus on identifying and extracting all lines that describe skills, technologies used.
    If no technical skills/ skills section is found, output nothing or a simple message like "No skills section found."
    """,
    output_content_type=SkillContainer,
)

class CertificationContainer(BaseModel):
    class CertificationInfo(BaseModel):
        cert_name: str
        cert_issuer: str
        cert_date: datetime
        cert_id: Optional[str] = None
        cert_expiry: Optional[datetime] = None
        cert_url: Optional[str] = None
        cert_skills: Optional[List[str]] = None  # Assuming a flat list of skill names
        cert_lvl: Optional[str] = None
    certificates: list[CertificationInfo]

# ── Cert Info Extractor Agent ──────────────────────────────────────────
cert_info_extract_agt = AssistantAgent(
    name="CertInfoExtractAgt",
    description=(
        "Receives markdown output from ResumeParseAgt and extracts only the "
        "content relevant to the 'Certifications' section, presenting it exactly "
        "as it appears in the input."
    ),
    model_client=qwen3moe_30b,
    # model_client_stream=True,
    system_message="""
    You will receive a parsed resume in markdown format.
    Your sole task is to identify and extract all lines of text that fall under the 'Certifications' section.
    Present this extracted information exactly as it appears in the input.
    Do not add any extra formatting, headings, or commentary.
    Focus on identifying and extracting all lines that describe certifications, skills obtained through those certifications and the date the certificate was obtained.
    If no Certifications section is found, output nothing or a simple message like "No Certifications section found."
    """,
    output_content_type=CertificationContainer,
)

class CourseConatiner(BaseModel):
    class CourseInfo(BaseModel):
        course_name: str
        course_org: str
        course_category: str
        course_code: Optional[str] = None
        course_date: Optional[datetime] = None
        course_grade: Optional[str] = None
        course_desc: Optional[str] = None
        course_skills: Optional[List[str]] = None  # List of skill names/keywords
        course_projects: Optional[List[str]] = None  # List of project titles or descriptions
    courses: list[CourseInfo]

# ── Course Info Extractor Agent ──────────────────────────────────────────
course_info_extract_agt = AssistantAgent(
    name="CourseInfoExtractAgt",
    description=(
        "Receives markdown output from ResumeParseAgt and extracts only the "
        "content relevant to the 'Relevant Courses' section, presenting it exactly "
        "as it appears in the input."
    ),
    model_client=qwen3moe_30b,
    # model_client_stream=True,
    system_message="""
    You will receive a parsed resume in markdown format.
    Your sole task is to identify and extract all lines of text that fall under the 'Relevant Courses' section.
    Present this extracted information exactly as it appears in the input.
    Do not add any extra formatting, headings, or commentary.
    Focus on identifying and extracting all lines that describe courses, skills obtained through those courses and the start and end dates to complete the course.
    If no Relevant Courses section is found, output nothing or a simple message like "No Relevant Courses section found."
    """,
    output_content_type=CourseConatiner,
)

"""
3. GraphFlow Setup
"""
# 3a. Setup agent and entry point
builder = DiGraphBuilder()
builder.add_node(resume_parse_agt).add_node(education_extract_agt).add_node(work_ex_extract_agt).add_node(proj_info_extract_agt).add_node(skill_info_extract_agt).add_node(cert_info_extract_agt).add_node(course_info_extract_agt)
builder.set_entry_point(resume_parse_agt)

# 3b. Add the edges now in the manner the program should run
builder.add_edge(resume_parse_agt, education_extract_agt)
builder.add_edge(resume_parse_agt, work_ex_extract_agt)
builder.add_edge(resume_parse_agt, proj_info_extract_agt)
builder.add_edge(resume_parse_agt, skill_info_extract_agt)
builder.add_edge(resume_parse_agt, cert_info_extract_agt)
builder.add_edge(resume_parse_agt, course_info_extract_agt)

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
