"""Canonical skill normalization — uses shared skill_tokens."""
from __future__ import annotations

from typing import Iterable

from app.ats.domain.interfaces import ISkillNormalizer
from app.ats.domain.schemas import ParsedJobDescription, ParsedResume
from app.ats.normalization.domain_tokens import infer_domain, normalize_domain_label
from app.ats.normalization.education_tokens import parse_education_line
from app.ats.normalization.skill_tokens import canonicalize, decompose_skill_phrase

_STOP_WORDS = {
    "and", "or", "the", "with", "for", "in", "on", "at", "to", "of", "a", "an",
    "strong", "excellent", "good", "plus", "preferred", "required",
}


def _dedupe_sorted(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in sorted(items, key=str.lower):
        c = canonicalize(item)
        if c and c not in seen and c not in _STOP_WORDS:
            seen.add(c)
            result.append(c)
    return result


def _expand_skill_list(skills: list[str]) -> list[str]:
    """Decompose compound phrases then dedupe."""
    expanded: list[str] = []
    for skill in skills:
        expanded.extend(decompose_skill_phrase(skill))
    return _dedupe_sorted(expanded)


def _dedupe_preserve_original(items: Iterable[str]) -> list[str]:
    """Case-insensitive dedupe while keeping original JD phrasing."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result


class SkillNormalizer(ISkillNormalizer):
    def normalize_resume(self, resume: ParsedResume) -> ParsedResume:
        data = resume.model_dump()
        data["skills"] = _expand_skill_list(resume.skills)
        data["tools"] = _expand_skill_list(resume.tools)
        data["technologies"] = _expand_skill_list(resume.technologies)
        data["certifications"] = _dedupe_sorted(resume.certifications)
        data["achievements"] = _dedupe_sorted(resume.achievements)
        data["responsibilities"] = _dedupe_sorted(resume.responsibilities)
        data["domain"] = normalize_domain_label(resume.domain or infer_domain(resume.raw_text[:800]))
        for exp in data["experience"]:
            exp["bullets"] = _dedupe_sorted(exp.get("bullets", []))
        for proj in data["projects"]:
            proj["technologies"] = _expand_skill_list(proj.get("technologies", []))
        # Normalize education entries for consistent matching
        normalized_edu: list[dict] = []
        from app.ats.normalization.education_tokens import normalize_degree_name
        for edu in resume.education:
            raw = edu.degree or ""
            if edu.institution:
                raw = f"{raw}, {edu.institution}"
            if edu.year:
                raw = f"{raw} {edu.year}"
            parsed = parse_education_line(raw.strip()) if raw.strip() else {}
            
            degree_normalized = normalize_degree_name(edu.degree)
            if not degree_normalized and parsed.get("canonical"):
                degree_normalized = normalize_degree_name(parsed["canonical"])
                
            normalized_edu.append({
                "degree": degree_normalized or edu.degree,
                "institution": parsed.get("institution", edu.institution) or edu.institution,
                "year": parsed.get("year", edu.year) or edu.year,
            })
        data["education"] = normalized_edu
        return ParsedResume(**data)

    def normalize_jd(self, jd: ParsedJobDescription) -> ParsedJobDescription:
        data = jd.model_dump()
        # Keep original JD phrasing for display; matching decomposes at compare time
        data["required_skills"] = _dedupe_preserve_original(jd.required_skills)
        data["preferred_skills"] = _dedupe_preserve_original(jd.preferred_skills)
        data["responsibilities"] = _dedupe_sorted(jd.responsibilities)
        data["education"] = _dedupe_sorted(jd.education)
        data["certifications"] = _dedupe_sorted(jd.certifications)
        data["tools"] = _expand_skill_list(jd.tools)
        data["technologies"] = _expand_skill_list(jd.technologies)
        data["job_title"] = jd.job_title.lower().strip()
        data["domain"] = normalize_domain_label(
            jd.domain or infer_domain(f"{jd.job_title} {' '.join(jd.required_skills[:12])}")
        )
        return ParsedJobDescription(**data)


skill_normalizer = SkillNormalizer()
