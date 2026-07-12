"""Deterministic education and certification matching with degree normalization."""
from __future__ import annotations

from app.ats.domain.interfaces import IEducationMatcher
from app.ats.domain.schemas import EducationMatchResult, ParsedJobDescription, ParsedResume
from app.ats.normalization.education_tokens import (
    education_requirements_match,
    parse_education_line,
)
from app.ats.normalization.skill_tokens import canonicalize

# ---------------------------------------------------------------------------
# Compliance / AML / GRC certification domain terms.
# When both the JD-required cert and the candidate's cert fall in this set,
# award partial credit (0.6) rather than a binary 0/1.
# ---------------------------------------------------------------------------
_COMPLIANCE_CERT_TERMS: frozenset[str] = frozenset([
    "grc", "governance", "risk", "compliance",
    "aml", "anti-money laundering", "anti money laundering",
    "cams", "acams", "cfcs", "cfe", "cgss", "cams-audit",
    "kyc", "cdd", "edd", "financial crime",
    "bsa", "bank secrecy", "fincen", "sanctions", "fraud",
    "regulatory", "risk management", "risk and compliance",
])


def _cert_in_domain(cert: str, domain: frozenset[str]) -> bool:
    """Return True when any domain term is a substring of the cert text."""
    t = cert.lower()
    return any(term in t for term in domain)


def _cert_overlap(required: list[str], available: list[str]) -> float:
    """Score certification coverage.

    - Exact / substring canonical match  → 1.0 credit (full).
    - Both certs in the same compliance domain → 0.6 credit (partial).
    - No relationship → 0 credit.
    """
    if not required:
        return 100.0
    if not available:
        return 0.0
    avail_canon = {canonicalize(a) for a in available}
    total_credit = 0.0
    for req in required:
        canon = canonicalize(req)
        # Exact / substring match — full credit
        if any(canon in a or a in canon for a in avail_canon):
            total_credit += 1.0
        # Both certs are compliance-domain related — partial credit
        elif (
            _cert_in_domain(req, _COMPLIANCE_CERT_TERMS)
            and any(_cert_in_domain(a, _COMPLIANCE_CERT_TERMS) for a in available)
        ):
            total_credit += 0.6
    return round(total_credit / len(required) * 100, 2)


def _resume_education_entries(resume: ParsedResume) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for edu in resume.education:
        raw = edu.degree or ""
        if edu.institution:
            raw = f"{raw}, {edu.institution}"
        if edu.year:
            raw = f"{raw} {edu.year}"
        if raw.strip():
            entries.append(parse_education_line(raw.strip()))
    return entries


class EducationMatcher(IEducationMatcher):
    """Compares degrees (level + field) and certifications."""

    def match(self, resume: ParsedResume, jd: ParsedJobDescription) -> EducationMatchResult:
        from app.ats.normalization.education_tokens import canonical_degree_level, LEVEL_RANK
        resume_entries = _resume_education_entries(resume)
        resume_certs = resume.certifications

        # Degree matching with level hierarchy + field overlap
        if jd.education:
            credits: list[float] = []
            for req in jd.education:
                credit, reason = education_requirements_match(req, resume_entries)
                credits.append(credit)
            degree_score = round(sum(credits) / len(credits) * 100, 2) if credits else 0.0

            # Floor: if candidate has education and the JD merely requires a generic bachelor's
            # level (e.g., "Bachelor's Degree or higher in relevant field"), never score below 85
            # when the candidate has any qualifying bachelor-or-above entry.
            if degree_score < 85.0 and resume_entries:
                jd_levels = [canonical_degree_level(req) for req in jd.education]
                jd_min_rank = min((LEVEL_RANK.get(lvl, 0) for lvl in jd_levels if lvl), default=0)
                resume_max_rank = max((LEVEL_RANK.get(e.get("degree_level", ""), 0) for e in resume_entries), default=0)
                if jd_min_rank > 0 and resume_max_rank >= jd_min_rank:
                    degree_score = max(degree_score, 85.0)
        else:
            degree_score = 100.0

        certification_score = _cert_overlap(jd.certifications, resume_certs)

        if jd.education and jd.certifications:
            combined = (degree_score + certification_score) / 2
        elif jd.education:
            combined = degree_score
        elif jd.certifications:
            combined = certification_score
        else:
            combined = 100.0

        return EducationMatchResult(
            education_score=round(combined, 2),
            certification_score=round(certification_score, 2),
            degree_score=round(degree_score, 2),
        )


education_matcher = EducationMatcher()
