"""
Very small helper: convert a PDF/DOCX resume to markdown text.
Assumes caller passes a valid relative path such as 'resumes/<file>.pdf'.
"""

import sys
from pathlib import Path

from docling.document_converter import DocumentConverter

sys.path.insert(0, str(Path(__file__).parent.parent))


def parse_pdf(file_path: str) -> str:
    """
    Convert the given resume file to markdown.

    Parameters
    ----------
    file_path : str
        Path provided by the caller, e.g. 'resumes/resume_ex.pdf'.

    Returns
    -------
    str
        Markdown on success, or an error string.
    """
    # Resolve path relative to this script’s directory
    file_path = Path(__file__).parent / file_path

    if not file_path.exists() or not file_path.is_file():
        return f"Error: File not found → {file_path}"

    try:
        return DocumentConverter().convert(file_path).document.export_to_markdown()
    except Exception as exc:  # pragma: no cover
        return f"Error: Could not convert file ({exc})"
