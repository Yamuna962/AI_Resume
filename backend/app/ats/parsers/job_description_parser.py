"""Deterministic job description parser."""
from __future__ import annotations

import re

from app.ats.domain.interfaces import IJobDescriptionParser
from app.ats.domain.schemas import ParsedJobDescription
from app.ats.normalization.education_tokens import (
    canonical_degree_level,
    mine_education_from_text,
)
from app.ats.normalization.domain_tokens import infer_domain
from app.ats.normalization.skill_tokens import (
    _split_commas_outside_parens,
    canonicalize,
    is_soft_skill_only,
    mine_tech_keywords,
)

_SECTION_PATTERNS = {
    "required_skills": r"(?i)(required\s+skills|key\s+skills|must[\-\s]have|technical\s+skills|skills\s+required)",
    "preferred_skills": r"(?i)(preferred\s+qualifications|preferred\s+skills|nice[\-\s]to[\-\s]have|bonus)",
    "responsibilities": r"(?i)(key\s+responsibilities|responsibilities|what\s+you(?:'ll|\s+will)\s+do|duties|you\s+will)",
    "education": r"(?i)(education\s+requirements|education|degree\s+requirements|academic\s+requirements)",
    "certifications": r"(?i)(certifications|certificates|licenses)",
    "experience": r"(?i)(experience\s*:|years\s+of\s+experience|experience\s+required|minimum\s+experience|\d+\s*[\-–]\s*\d+\s*years?)",
    "title": r"(?i)(job\s+title|position\s*:|role\s*:|we\s+are\s+hiring)",
    # Qualifications may contain education OR skills — parsed separately below
    "qualifications": r"(?i)(qualifications|requirements)",
}


def _extract_section(text: str, start_key: str) -> str:
    start_pat = _SECTION_PATTERNS[start_key]
    start = re.search(start_pat, text)
    if not start:
        return ""
    begin = start.end()
    end = len(text)
    for key, pat in _SECTION_PATTERNS.items():
        if key == start_key:
            continue
        nxt = re.search(pat, text[begin:])
        if nxt:
            end = min(end, begin + nxt.start())
    return text[begin:end].strip()


def _parse_skill_lines(section: str) -> list[str]:
    """Parse skills line-by-line; respect parentheses when splitting commas."""
    if not section:
        return []

    items: list[str] = []
    for line in section.splitlines():
        line = re.sub(r"^[\-\*\u2022:\d\.\)\s]+", "", line.strip())
        if not line or len(line) < 2:
            continue

        # One skill per line (common JD format)
        if "\n" not in line and "," not in line and "/" not in line:
            items.append(line)
            continue

        for part in _split_commas_outside_parens(line):
            cleaned = part.strip().strip(".,;")
            if cleaned and len(cleaned) > 2:
                items.append(cleaned)

    return items


def _parse_responsibilities(section: str) -> list[str]:
    if not section:
        return []
    items: list[str] = []
    for line in section.splitlines():
        line = re.sub(r"^[\-\*\u2022:\d\.\)\s]+", "", line.strip())
        if line and len(line) > 10:
            items.append(line)
    return items


def _extract_title(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""
    title_section = _extract_section(text, "title")
    if title_section:
        return title_section.splitlines()[0].strip()
    # First line often is the title (skip "Job Description –" prefix)
    first = lines[0]
    first = re.sub(r"(?i)^job\s+description\s*[–\-:]\s*", "", first)
    return first[:120]


def _dedupe_skills_by_meaning(skills: list[str]) -> list[str]:
    """Keep one label per canonical skill; prefer the longer/more descriptive label."""
    by_canon: dict[str, str] = {}
    for skill in skills:
        key = canonicalize(skill)
        if not key:
            continue
        existing = by_canon.get(key)
        if not existing or len(skill) > len(existing):
            by_canon[key] = skill
    return list(by_canon.values())


def _is_education_line(line: str) -> bool:
    """True if line describes a degree/education requirement, not a tech skill."""
    if canonical_degree_level(line):
        return True
    lower = line.lower()
    return any(
        kw in lower
        for kw in (
            "bachelor", "master", "degree", "diploma", "phd", "ph.d",
            "b.tech", "btech", "m.tech", "mtech", "graduate", "undergraduate",
            "associate", "ged", "education",
        )
    )


def _split_qualifications_block(block: str) -> tuple[list[str], list[str]]:
    """Split qualifications into education reqs vs technical skills."""
    edu: list[str] = []
    skills: list[str] = []
    for line in _parse_skill_lines(block):
        if _is_education_line(line):
            edu.append(line)
        elif not is_soft_skill_only(line):
            skills.append(line)
    return edu, skills


def _fallback_required_skills(text: str) -> list[str]:
    """Extract tech skills from full JD when no skills section is found."""
    mined = mine_tech_keywords(text)
    for match in re.finditer(
        r"(?i)(?:skills|technologies|requirements)\s*[:\-]\s*([^\n]+)",
        text,
    ):
        for part in _split_commas_outside_parens(match.group(1)):
            p = part.strip()
            if p and len(p) > 2 and not is_soft_skill_only(p) and not _is_education_line(p):
                mined.append(p)
    return list(dict.fromkeys(mined))


class JobDescriptionParser(IJobDescriptionParser):
    """Extracts structured JD data deterministically."""

    def parse(self, text: str) -> ParsedJobDescription:
        if not text or not text.strip():
            return ParsedJobDescription(raw_text=text)

        required_block = _extract_section(text, "required_skills")
        qual_block = _extract_section(text, "qualifications")
        preferred_block = _extract_section(text, "preferred_skills")
        resp_block = _extract_section(text, "responsibilities")
        edu_block = _extract_section(text, "education")
        cert_block = _extract_section(text, "certifications")
        exp_block = _extract_section(text, "experience")

        required_skills = _parse_skill_lines(required_block)
        preferred_skills = _parse_skill_lines(preferred_block)
        responsibilities = _parse_responsibilities(resp_block)
        education = _parse_skill_lines(edu_block)

        # Qualifications block: route degree lines → education, tech lines → skills
        if qual_block:
            qual_edu, qual_skills = _split_qualifications_block(qual_block)
            education.extend(qual_edu)
            if not required_block:
                required_skills.extend(qual_skills)

        # Fallback: mine degree requirements from inline JD text
        if not education:
            education = mine_education_from_text(text)

        # Normalize degree names
        from app.ats.normalization.education_tokens import normalize_degree_name
        education = [normalize_degree_name(e) for e in education]

        # Filter soft skills and education lines from technical skills
        required_skills = [
            s for s in required_skills
            if not is_soft_skill_only(s) and not _is_education_line(s)
        ]

        if not required_skills:
            required_skills = _fallback_required_skills(text)

        required_skills = _dedupe_skills_by_meaning(required_skills)
        preferred_skills = _dedupe_skills_by_meaning(preferred_skills)
        education = list(dict.fromkeys(education))

        all_skills_text = " ".join(required_skills + preferred_skills)
        tools = mine_tech_keywords(
            _extract_section(text, "required_skills") + " " + qual_block
        )
        technologies = _dedupe_skills_by_meaning(required_skills + preferred_skills)
        domain = infer_domain(
            f"{_extract_title(text)} {all_skills_text} {resp_block[:300]}"
        )

        return ParsedJobDescription(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            required_experience=exp_block or "",
            responsibilities=responsibilities,
            education=education,
            certifications=_parse_skill_lines(cert_block),
            tools=tools,
            technologies=technologies,
            job_title=_extract_title(text),
            domain=domain,
            raw_text=text,
        )


job_description_parser = JobDescriptionParser()
