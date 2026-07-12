"""
PDF parsing utilities — delegates extraction to multi-engine pdf_extractor.
"""
from __future__ import annotations

import re

from app.utils.pdf_extractor import (
    PDFExtractionResult,
    extract_text_from_pdf,
    extract_text_from_pdf_detailed,
)

# Re-export for backward compatibility
__all__ = [
    "extract_text_from_pdf",
    "extract_text_from_pdf_detailed",
    "PDFExtractionResult",
    "parse_resume_sections",
]


def parse_resume_sections(text: str) -> dict[str, str]:
    """
    Split resume text into standard sections.
    Handles plain text, Markdown headers, ALL CAPS, and colon-style headers.
    """
    sections = {
        "summary": "",
        "experience": "",
        "education": "",
        "skills": "",
        "projects": "",
        "certifications": "",
        "achievements": "",
        "qualifications": "",
    }

    header_patterns = {
        "experience": r"(?i)^\s*(#{1,4}\s+)?(professional\s+)?(experience|work\s+experience|work\s+history|employment(\s+history)?)\s*:?\s*$",
        "education": r"(?i)^\s*(#{1,4}\s+)?(education|academic\s+background|academic\s+credentials|qualifications)\s*:?\s*$",
        "skills": r"(?i)^\s*(#{1,4}\s+)?(technical\s+skills|core\s+competencies|skills(\s+(&|and)\s+technologies)?|technologies|tools|key\s+skills)\s*:?\s*$",
        "projects": r"(?i)^\s*(#{1,4}\s+)?(projects|personal\s+projects|key\s+projects|selected\s+projects)\s*:?\s*$",
        "certifications": r"(?i)^\s*(#{1,4}\s+)?(certifications?|licenses?|certificates?|professional\s+certifications?)\s*:?\s*$",
        "achievements": r"(?i)^\s*(#{1,4}\s+)?(achievements?|awards?|honors?|accomplishments?|recognition)\s*:?\s*$",
        "qualifications": r"(?i)^\s*(#{1,4}\s+)?(qualifications?|credentials?)\s*:?\s*$",
        "summary": r"(?i)^\s*(#{1,4}\s+)?(summary|professional\s+summary|profile|objective|about(\s+me)?|career\s+summary)\s*:?\s*$",
    }

    upper_map = {
        "EXPERIENCE": "experience",
        "WORK EXPERIENCE": "experience",
        "PROFESSIONAL EXPERIENCE": "experience",
        "EDUCATION": "education",
        "SKILLS": "skills",
        "TECHNICAL SKILLS": "skills",
        "CORE COMPETENCIES": "skills",
        "PROJECTS": "projects",
        "CERTIFICATIONS": "certifications",
        "ACHIEVEMENTS": "achievements",
        "AWARDS": "achievements",
        "HONORS": "achievements",
        "QUALIFICATIONS": "qualifications",
        "SUMMARY": "summary",
        "PROFILE": "summary",
        "OBJECTIVE": "summary",
    }

    current = "summary"
    for line in text.splitlines():
        cleaned = line.strip().lstrip("#").strip()
        if not cleaned:
            continue

        is_header = False
        for section, pattern in header_patterns.items():
            if re.match(pattern, line.strip()) or re.match(pattern, cleaned):
                current = section
                is_header = True
                break

        if not is_header:
            upper_key = cleaned.upper().rstrip(":")
            if upper_key in upper_map:
                current = upper_map[upper_key]
                is_header = True

        if not is_header:
            sections[current] += cleaned + "\n"

    return {k: v.strip() for k, v in sections.items()}
