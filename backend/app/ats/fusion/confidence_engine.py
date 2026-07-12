"""Deterministic confidence score from parser, embeddings, and section coverage."""
from __future__ import annotations

from app.ats.domain.schemas import (
    EducationMatchResult,
    ExperienceMatchResult,
    FormattingResult,
    KeywordMatchResult,
    ParsedJobDescription,
    ParsedResume,
    SemanticMatchResult,
)


def _parser_confidence(resume: ParsedResume, jd: ParsedJobDescription) -> float:
    """How completely resume and JD were parsed into structured sections."""
    resume_checks = [
        bool(resume.skills),
        bool(resume.experience),
        bool(resume.education),
        bool(resume.summary or len(resume.raw_text) > 200),
        bool(resume.certifications or resume.projects),
    ]
    jd_checks = [
        bool(jd.required_skills),
        bool(jd.job_title),
        bool(jd.responsibilities or jd.required_experience),
    ]
    resume_pct = sum(resume_checks) / len(resume_checks) * 100
    jd_pct = sum(jd_checks) / len(jd_checks) * 100
    return round((resume_pct * 0.6 + jd_pct * 0.4), 2)


def _section_coverage(
    keyword: KeywordMatchResult,
    experience: ExperienceMatchResult,
    education: EducationMatchResult,
    jd: ParsedJobDescription,
) -> float:
    """Fraction of applicable JD dimensions with meaningful matches."""
    dims: list[float] = []

    if jd.required_skills:
        dims.append(keyword.required_skill_score)
    if jd.preferred_skills:
        dims.append(keyword.preferred_skill_score)
    if jd.responsibilities:
        total = len(jd.responsibilities) or 1
        dims.append(len(experience.matched_responsibilities) / total * 100)
    if jd.education:
        dims.append(education.degree_score)
    if jd.certifications:
        dims.append(education.certification_score)

    return round(sum(dims) / len(dims), 2) if dims else 85.0


def compute_confidence_score(
    resume: ParsedResume,
    jd: ParsedJobDescription,
    keyword: KeywordMatchResult,
    semantic: SemanticMatchResult,
    experience: ExperienceMatchResult,
    education: EducationMatchResult,
    formatting: FormattingResult,
) -> float:
    """
    Aggregate confidence (0–100) from parser quality, embedding signal,
    section coverage, and document completeness.
    """
    parser = _parser_confidence(resume, jd)
    embedding = round(min(100.0, semantic.confidence * 100), 2) if semantic.confidence else 50.0
    coverage = _section_coverage(keyword, experience, education, jd)
    completeness = formatting.formatting_score

    raw = (
        parser * 0.25
        + embedding * 0.25
        + coverage * 0.30
        + completeness * 0.20
    )
    return round(min(100.0, max(0.0, raw)), 2)
