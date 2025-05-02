import json
import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import ollama  # Import the ollama client
from docling.document_converter import DocumentConverter

# Define the path to the PDF file
resume_path = "docs/resumes/ex4.pdf"


# Define a simple function to extract raw text from the PDF
def parse_pdf(file_path: str) -> str:
    """Parses a PDF file and returns its content as markdown."""
    # If file unavailable, return error message
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return f"Error: File not found or invalid path: {file_path}"

    # Parse content using docling
    parsed_content = (
        DocumentConverter().convert(file_path).document.export_to_markdown()
    )
    return parsed_content


def extract_education_info(markdown_text: str, model="gemma3:12b-it-qat") -> str:

    # Define the JSON schema (remains the same, as it defines the structure)
    output_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "ed_lvl": {
                    "type": "string",
                    "description": "Education level from: Highschool, Associate, Undergrad, Postgrad, Doctoral, Postdoctoral)",
                },
                "ed_org": {
                    "type": "string",
                    "description": "Name of educational institution",
                },
                "ed_degree": {
                    "type": "string",
                    "description": "ONLY the degree type (e.g., 'Bachelor of Science')",
                },
                "ed_startdate": {
                    "type": ["string", "null"],
                    "description": "Date started in MM/YY format. Use null if not found.",
                },
                "ed_enddate": {
                    "type": ["string", "null"],
                    "description": "Date ended in MM/YY format. If only one date, assume it's the end date. Use null if not found.",
                },
                "ed_status": {
                    "type": "string",
                    "description": "Status of education (Complete, Ongoing, Drop)",
                },
                "ed_majors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of majors/fields of study, expanded to full names, should NOT include the degree type",
                },
                "ed_minors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of minors, expanded to full names",
                },
                "ed_location": {
                    "type": "string",
                    "description": "Parsable location of the institution",
                },
                "ed_gpa": {
                    "type": ["number", "null"],
                    "description": "Grade Point Average as a float. Use null if not specified.",
                },
            },
            "required": [
                "ed_lvl",
                "ed_org",
                "ed_degree",
                "ed_status",
                "ed_majors",
                "ed_minors",
                "ed_location",
            ],
        },
    }

    # Create a prompt focusing on identifying and processing *each* entry
    prompt = f"""You are provided with a resume in markdown format. Your task is to carefully read the "Education" section (or any part describing education) and extract information for EACH distinct educational entry found.

    For every educational entry identified, generate a JSON object according to the provided schema with the following details:

    Important Rules for Extraction:
    1. For each education entry, determine the appropriate education level (ed_lvl) from the options: Highschool, Associate, Undergrad, Postgrad, Doctoral, Postdoctoral
    2. Identify the name of the educational institution (ed_org).
    3. Extract ONLY the degree type (ed_degree).
    4. Find the start date (ed_startdate) and end date (ed_enddate).
       - Convert all dates to MM/YY format (e.g., "June 2025" -> "06/25").
       - If no start date is found, use null.
       - If only one date is found, assume it's the end date.
       - Remove words like "(Expected)" from dates, but use them to determine the status.
    5. Determine the status of education (ed_status) based on the dates and keywords like "(Expected)". Use "Complete" for past degrees, "Ongoing" for future/expected graduation dates, and "Drop" for incomplete education if indicated.
    6. Extract the majors/fields of study (ed_majors). This should be a list of strings and should NOT include the degree type itself. Expand abbreviations (e.g., "CS" -> "Computer Science").
    7. Extract any minors (ed_minors) as a list of strings, expanding abbreviations.
    8. Identify the location of the institution (ed_location).
    9. Extract the Grade Point Average (ed_gpa) as a floating-point number. Use null if the GPA is not specified.
    10. There can never be a scenario where ed_startdate has a value and ed_enddate is null. If ed_startdate is null, then change its value to what ed_startdate is and set ed_startdate to null.

    Ensure that the text extracted for ed_majors does not duplicate text in ed_degree.
    Ensure the text extracted for ed_location does not duplicate text in ed_org.

    If no education entries are found, return an empty JSON array [].

    RESUME MARKDOWN:
    {markdown_text}

    Provide the extracted information as a JSON array, with one object for EACH distinct educational entry identified in the markdown text, strictly adhering to the specified schema.
    """

    # Call the Ollama model, using the format parameter with the JSON schema
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format=output_schema,  # Pass the JSON schema dictionary here
        options={
            "temperature": 0.1,
            "seed": 0,
            "top_p": 0.5,
            "top_k": 10,
        },
    )

    json_output_string = response["message"]["content"]
    try:
        education_data = json.loads(json_output_string)
        # You can now work with education_data as a Python list
        # print(education_data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        print(f"Raw response content: {json_output_string}")
        education_data = None  # Or handle the error as needed

    return (
        json_output_string  # Or return education_data if you prefer the parsed object
    )


if __name__ == "__main__":

    markdown_output = parse_pdf(resume_path)
    print("\n=== MARKDOWN OUTPUT ===\n")
    education_info = extract_education_info(markdown_output)

    print("\n=== EDUCATION INFORMATION ===\n")
    print(education_info)
