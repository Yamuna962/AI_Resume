"""Section-aware experience matching — responsibilities vs experience bullets only."""
from __future__ import annotations

import re
import numpy as np

from app.ats.domain.interfaces import IExperienceMatcher
from app.ats.domain.schemas import ExperienceMatchResult, ParsedJobDescription, ParsedResume
from app.ats.embeddings.embedding_service import embedding_service
from app.ats.normalization.skill_tokens import canonicalize

_YEARS_RE = re.compile(r"(\d+)\+?\s*(?:years?|yrs?)", re.I)
_JD_YEARS_RE = re.compile(
    r"(\d+)\s*[\-–to]+\s*(\d+)\s*(?:years?|yrs?)|(\d+)\+?\s*(?:years?|yrs?)", re.I
)

# Regex and word sets for Business Impact & Leadership detection
#
# Fixes vs. original:
# - Percentage pattern no longer requires trailing \b, so "98%+" is matched.
# - Added numeric range pattern to catch "100–120+" style metrics.
# - Added dollar-amount pattern with optional comma separators.
_METRIC_RE = re.compile(
    r'\b\d+(?:\.\d+)?%\+?'                                              # 98%, 98%+, 2.5%
    r'|\b\d+\s*[\-\u2013]\s*\d+\+?'                                     # 100-120+, 100–120
    r'|\b\d+\+?\s*(?:percent|million|billion|usd|inr|gb|tb|user|client|customer)s?\b'  # 50 users
    r'|\$[\d,]+',                                                        # $50,000
    re.I,
)

# Both past-tense and stem/present forms so bullets like "improve", "reduce",
# "deliver" are detected alongside "improved", "reduced", "delivered".
_IMPACT_WORDS = {
    # Past tense
    "reduced", "increased", "saved", "grew", "optimized", "delivered",
    "improved", "automated", "boosted", "cut", "decreased", "minimized",
    "maximized", "accelerated", "enhanced", "generated", "yielded",
    "scaled", "streamlined",
    # Present / stem forms
    "reduce", "increase", "save", "grow", "optimize", "deliver",
    "improve", "automate", "boost", "decrease", "minimize",
    "maximize", "accelerate", "enhance", "generate", "yield",
    "scale", "streamline",
    # Nouns / impact signals
    "revenue", "growth", "efficiency", "sales", "costs", "profit",
    "under budget", "roi", "automation",
}

# Added gerund / noun forms so bullets like "coaching", "onboarding",
# "knowledge transfer" are detected alongside classic past-tense verbs.
_LEADERSHIP_WORDS = {
    "led", "managed", "supervised", "mentored", "mentoring", "lead", "championed",
    "directed", "headed", "coordinated", "trained", "training", "founded", "hired",
    "coached", "coaching", "manager", "director", "head", "chief", "principal",
    "architect", "team of", "spearheaded", "led a team", "guiding", "guide",
    "delegated", "facilitated", "owner", "onboarding", "knowledge transfer",
}


def _extract_resume_years(resume: ParsedResume) -> float:
    text = " ".join(
        [exp.duration + " " + exp.title + " " + " ".join(exp.bullets) for exp in resume.experience]
    )
    nums = [int(m.group(1)) for m in _YEARS_RE.finditer(text)]
    if nums:
        return float(max(nums))
    ranges = re.findall(r"(20\d{2})\s*[\-–]\s*(20\d{2}|present|current)", text, re.I)
    if ranges:
        from datetime import datetime

        total = 0.0
        current_year = datetime.now().year
        for start, end in ranges:
            end_year = current_year if end.lower() in ("present", "current") else int(end)
            total += max(0, end_year - int(start))
        return total
    return 0.0


def _extract_jd_years(jd: ParsedJobDescription) -> float:
    text = jd.required_experience + " " + jd.raw_text[:500]
    range_match = _JD_YEARS_RE.search(text)
    if range_match:
        if range_match.group(1) and range_match.group(2):
            return float(range_match.group(2))
        if range_match.group(3):
            return float(range_match.group(3))
    return 0.0


def _token_overlap(a: str, b: str) -> float:
    ta = set(canonicalize(a).split())
    tb = set(canonicalize(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb) * 100


def _semantic_overlap(jd_text: str, resume_bullets: list[str]) -> float:
    if not jd_text or not resume_bullets:
        return 0.0
    jd_emb = embedding_service.encode([jd_text])[0]
    bullet_emb = embedding_service.encode(resume_bullets)
    sims = bullet_emb @ jd_emb
    best = float(np.max(sims)) if sims.size else 0.0
    return embedding_service.similarity_to_bucket(best)


def _experience_bullets(resume: ParsedResume) -> list[str]:
    """Only experience section bullets — no raw-text fallback."""
    bullets: list[str] = []
    for exp in resume.experience:
        bullets.extend(exp.bullets)
    return [b for b in bullets if b.strip()]


class ExperienceMatcher(IExperienceMatcher):
    """Compares years, role, responsibilities, business impact, and leadership."""

    def match(self, resume: ParsedResume, jd: ParsedJobDescription) -> ExperienceMatchResult:
        resume_years = _extract_resume_years(resume)
        jd_years = _extract_jd_years(jd)

        if jd_years <= 0:
            years_score = 100.0 if resume_years > 0 else 50.0
        elif resume_years >= jd_years:
            years_score = 100.0
        else:
            years_score = max(0.0, (resume_years / jd_years) * 100)

        # Section-aware: JD responsibilities ↔ resume experience bullets only
        resume_bullets = _experience_bullets(resume)
        jd_resps = jd.responsibilities

        matched_resp: list[str] = []
        missing_resp: list[str] = []
        resp_scores: list[float] = []

        for resp in sorted(jd_resps, key=str.lower):
            best = 0.0
            for bullet in resume_bullets:
                score = _token_overlap(resp, bullet)
                if score > best:
                    best = score
            sem_score = _semantic_overlap(resp, resume_bullets)
            combined = max(best, sem_score)
            if combined >= 40:
                matched_resp.append(resp)
                resp_scores.append(min(100.0, combined))
            else:
                missing_resp.append(resp)
                resp_scores.append(combined * 0.5)

        resp_score = sum(resp_scores) / len(resp_scores) if resp_scores else (
            100.0 if not jd_resps else 50.0
        )

        resume_titles = " ".join(exp.title for exp in resume.experience)
        role_score = _token_overlap(jd.job_title, resume_titles) if jd.job_title else 50.0
        if role_score == 0 and resume.experience:
            role_score = 40.0

        resume_domain = (resume.summary + " " + resume_titles).lower()
        jd_domain = (jd.job_title + " " + " ".join(jd.required_skills[:10])).lower()
        domain_score = max(
            _token_overlap(resume_domain, jd_domain),
            _semantic_overlap(jd_domain, resume_bullets) if resume_bullets else 0.0,
        )

        # Business Impact Score: detect metrics and impact keywords in bullets
        if not resume_bullets:
            business_impact_score = 0.0
        else:
            impact_hits = sum(1 for b in resume_bullets if _METRIC_RE.search(b) or any(w in b.lower() for w in _IMPACT_WORDS))
            business_impact_score = min(100.0, 40.0 + impact_hits * 15.0)

        # Leadership Score: detect leadership indicators in titles and bullets
        if not resume.experience:
            leadership_score = 0.0
        else:
            title_hits = sum(1 for exp in resume.experience if any(w in exp.title.lower() for w in _LEADERSHIP_WORDS))
            bullet_hits = sum(1 for b in resume_bullets if any(w in b.lower() for w in _LEADERSHIP_WORDS))
            hit_count = title_hits * 2 + bullet_hits
            leadership_score = min(100.0, 40.0 + hit_count * 15.0)

        # Overall Experience Score with new weights:
        # Years: 25%, Responsibilities: 35%, Domain: 20%, Business Impact: 10%, Leadership: 10%
        experience_score = round(
            years_score * 0.25
            + resp_score * 0.35
            + domain_score * 0.20
            + business_impact_score * 0.10
            + leadership_score * 0.10,
            2,
        )

        return ExperienceMatchResult(
            experience_score=experience_score,
            matched_responsibilities=sorted(matched_resp),
            missing_responsibilities=sorted(missing_resp),
            years_score=round(years_score, 2),
            role_score=round(role_score, 2),
            domain_score=round(domain_score, 2),
            responsibilities_score=round(resp_score, 2),
            business_impact_score=round(business_impact_score, 2),
            leadership_score=round(leadership_score, 2),
        )


experience_matcher = ExperienceMatcher()
