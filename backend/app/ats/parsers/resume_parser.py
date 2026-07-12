"""Deterministic resume parser — uses layout-preserved text from PDF extraction."""
from __future__ import annotations

import re

from loguru import logger

from app.ats.domain.interfaces import IResumeParser
from app.ats.domain.schemas import ParsedEducation, ParsedExperience, ParsedProject, ParsedResume
from app.ats.normalization.domain_tokens import infer_domain
from app.ats.normalization.skill_tokens import mine_tech_keywords
from app.utils.pdf_parser import parse_resume_sections

try:
    import spacy
    spacy.load("en_core_web_sm")
except Exception:
    logger.debug("spaCy not available; using regex-only resume parsing")

_BULLET = re.compile(r"^[\u2022\-\*\u2023\u25E6\u2013\u2014]\s*")
_SKILL_SPLIT = re.compile(r"[,|;•\n]|(?:\s{2,})")

# Expanded section headers — also match inline "Skills: Java, Python"
_INLINE_HEADER = re.compile(
    r"(?i)^\s*(skills|technical skills|technologies|tools|certifications?)\s*:\s*(.+)$"
)

_DATE_RANGE = re.compile(
    r"(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}"
    r"|\d{4}\s*[\-–—to]+\s*(\d{4}|present|current)"
    r"|(?:present|current)"
)
_EMAIL = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE = re.compile(r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?)?\d{3}[\s\-]?\d{4}")
_LINKEDIN = re.compile(r"(?i)linkedin\.com/in/[\w\-]+")


def _parse_personal_info(text: str) -> dict[str, str]:
    """Extract contact fields from resume header."""
    info: dict[str, str] = {}
    header = "\n".join(text.splitlines()[:12])
    email = _EMAIL.search(header)
    if email:
        info["email"] = email.group(0)
    phone = _PHONE.search(header)
    if phone:
        info["phone"] = phone.group(0).strip()
    linkedin = _LINKEDIN.search(header)
    if linkedin:
        info["linkedin"] = linkedin.group(0)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        info["name"] = lines[0][:80]
        if len(lines) > 1 and len(lines[1]) < 80 and not _EMAIL.search(lines[1]):
            info["headline"] = lines[1]
    return info


def _parse_achievements_block(block: str) -> list[str]:
    if not block:
        return []
    items: list[str] = []
    for line in block.splitlines():
        line = _BULLET.sub("", line.strip()).strip()
        if line and len(line) > 5:
            items.append(line)
    return items


def _split_title_company(line: str) -> tuple[str, str]:
    """Parse 'Title | Company | Dates' or 'Title at Company'."""
    if "|" in line:
        parts = [p.strip() for p in line.split("|")]
        title = parts[0] if parts else line
        company = parts[1] if len(parts) > 1 else ""
        return title, company
    at_match = re.search(r"(?i)\s+at\s+(.+)$", line)
    if at_match:
        return line[: at_match.start()].strip(), at_match.group(1).strip()
    return line, ""


def _split_sections(text: str) -> dict[str, str]:
    """Delegate to shared pdf_parser section logic for consistency."""
    return parse_resume_sections(text)


def _parse_skills_block(block: str) -> list[str]:
    skills: list[str] = []
    if not block:
        return skills

    # Handle inline "Skills: Java, Python, React"
    for line in block.splitlines():
        inline = _INLINE_HEADER.match(line.strip())
        if inline:
            block = inline.group(2) + "\n" + block
            break

    # Comma/pipe separated
    for part in _SKILL_SPLIT.split(block):
        s = part.strip().strip(".")
        if s and len(s) > 1 and not s.isdigit():
            skills.append(s)

    # Space-separated skill lines: "Java Python React AWS"
    if len(skills) <= 2:
        for line in block.splitlines():
            line = line.strip()
            if not line or ":" in line:
                continue
            tokens = [t.strip() for t in line.split() if len(t.strip()) > 1]
            if len(tokens) >= 2 and all(t[0].isupper() or t.isupper() for t in tokens):
                skills.extend(tokens)

    return list(dict.fromkeys(skills))


def _parse_experience_block(block: str) -> list[ParsedExperience]:
    entries: list[ParsedExperience] = []
    if not block:
        return entries

    # Split on date ranges or company/title lines
    chunks = re.split(
        r"\n(?=[^\n]{0,100}(?:\d{4}|present|current))",
        block,
        flags=re.I,
    )
    if len(chunks) <= 1:
        chunks = re.split(r"\n{2,}", block)

    for chunk in chunks:
        lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            continue

        title_line = lines[0]
        title, company = _split_title_company(title_line)
        duration = ""
        dur_match = _DATE_RANGE.search(chunk)
        if dur_match:
            duration = dur_match.group(0)

        bullets: list[str] = []
        for ln in lines[1:]:
            if _BULLET.match(ln) or ln.startswith("-") or ln.startswith("*"):
                bullets.append(_BULLET.sub("", ln).strip())
            elif ln[0].islower() or ln.startswith("and "):
                # Continuation of previous bullet
                if bullets:
                    bullets[-1] += " " + ln
                else:
                    bullets.append(ln)
            else:
                bullets.append(ln)

        entries.append(
            ParsedExperience(title=title, company=company, duration=duration, bullets=bullets)
        )
    return entries


def _parse_projects_block(block: str) -> list[ParsedProject]:
    projects: list[ParsedProject] = []
    if not block:
        return projects

    chunks = re.split(r"\n(?=[A-Z][^\n]{3,40}(?:\n|$))", block)
    if len(chunks) <= 1:
        chunks = [block]

    for chunk in chunks:
        lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            continue
        name = lines[0]
        desc_parts = [
            _BULLET.sub("", ln).strip()
            for ln in lines[1:]
            if _BULLET.match(ln) or ln.startswith("-") or not ln.isupper()
        ]
        desc = " ".join(desc_parts)
        techs = mine_tech_keywords(f"{name} {desc}")
        projects.append(
            ParsedProject(name=name, description=desc, technologies=techs)
        )
    return projects


def _parse_education_block(block: str) -> list[ParsedEducation]:
    from app.ats.normalization.education_tokens import parse_education_line, normalize_degree_name

    entries: list[ParsedEducation] = []
    if not block:
        return entries

    for line in block.splitlines():
        line = line.strip()
        if not line or len(line) < 3:
            continue
        parsed = parse_education_line(line)
        degree_raw = parsed.get("raw", line)
        
        # Extract base degree level or field if available to reconstruct cleanly
        if parsed.get("degree_level") or parsed.get("field"):
            parts = []
            if parsed.get("degree_level"):
                parts.append(parsed["degree_level"].replace("_", " ").title())
            if parsed.get("field"):
                parts.append(parsed["field"].title())
            reconstructed = " in ".join(parts) if len(parts) == 2 else " ".join(parts)
            degree_label = normalize_degree_name(reconstructed)
        else:
            degree_label = normalize_degree_name(degree_raw)

        entries.append(
            ParsedEducation(
                degree=degree_label or line,
                institution=parsed.get("institution", ""),
                year=parsed.get("year", ""),
            )
        )
    return entries


def _extract_skills_from_full_text(text: str, sections: dict[str, str]) -> list[str]:
    """Mine skills from Skills section, experience bullets, and full resume text."""
    skills = _parse_skills_block(sections.get("skills", ""))
    pool = "\n".join(
        sections.get(key, "")
        for key in ("skills", "experience", "projects", "summary", "certifications")
    )
    mined = mine_tech_keywords(pool or text)
    # Always mine full raw text — PDF section headers may be missing or mis-detected
    mined_full = mine_tech_keywords(text)
    return list(dict.fromkeys(skills + mined + mined_full))


class ResumeParser(IResumeParser):
    """Extracts structured resume data from layout-preserved PDF text."""

    def parse(self, text: str) -> ParsedResume:
        if not text or not text.strip():
            return ParsedResume(raw_text=text)

        sections = _split_sections(text)
        skills = _extract_skills_from_full_text(text, sections)
        experience = _parse_experience_block(sections.get("experience", ""))
        projects = _parse_projects_block(sections.get("projects", ""))
        education = _parse_education_block(sections.get("education", ""))
        # Fallback: education sometimes listed under qualifications
        if not education and sections.get("qualifications"):
            education = _parse_education_block(sections.get("qualifications", ""))
        certifications = _parse_skills_block(sections.get("certifications", ""))
        achievements = _parse_achievements_block(sections.get("achievements", ""))

        responsibilities: list[str] = []
        for exp in experience:
            responsibilities.extend(exp.bullets)
        responsibilities.extend(achievements)

        domain_text = " ".join(
            [sections.get("summary", ""), " ".join(skills), " ".join(e.degree for e in education)]
        )
        domain = infer_domain(domain_text)

        return ParsedResume(
            personal_info=_parse_personal_info(text),
            skills=skills,
            experience=experience,
            projects=projects,
            education=education,
            certifications=certifications,
            achievements=achievements,
            tools=list(skills),
            technologies=list(skills),
            responsibilities=responsibilities,
            summary=sections.get("summary", ""),
            domain=domain,
            raw_text=text,
        )


resume_parser = ResumeParser()
