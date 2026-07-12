"""Section-aware keyword matching with tiered semantic + related-skill support."""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.ats.domain.interfaces import IKeywordMatcher
from app.ats.domain.schemas import (
    KeywordMatchResult,
    ParsedJobDescription,
    ParsedResume,
    SemanticMatchResult,
)
from app.ats.normalization.skill_tokens import (
    canonicalize,
    decompose_skill_phrase,
    find_related_skill,
    mine_tech_keywords,
)

_SEMANTIC_FULL = 85
_SEMANTIC_GOOD = 70
_SEMANTIC_PARTIAL = 55


@dataclass(frozen=True)
class SkillScoreProfile:
    semantic_full_credit: float
    semantic_good_credit: float
    semantic_partial_credit: float
    related_credit: float
    partial_section_bonus: float
    matched_threshold: float
    related_threshold: float


_REQUIRED_PROFILE = SkillScoreProfile(
    semantic_full_credit=0.88,
    semantic_good_credit=0.68,
    semantic_partial_credit=0.42,
    related_credit=0.38,
    partial_section_bonus=0.0,
    matched_threshold=0.65,
    related_threshold=0.38,
)

# Preferred skills are bonus signals, so give more recruiter-like credit for
# transferable evidence from experience, projects, and adjacent tools.
_PREFERRED_PROFILE = SkillScoreProfile(
    semantic_full_credit=0.94,
    semantic_good_credit=0.78,
    semantic_partial_credit=0.58,
    related_credit=0.52,
    partial_section_bonus=0.08,
    matched_threshold=0.55,
    related_threshold=0.45,
)

# Section search order for JD skills → resume skills section first
_SKILL_SECTIONS = ("skills", "tools", "technologies", "certifications")
_EXPERIENCE_SECTIONS = ("experience", "responsibilities")
_PROJECT_SECTIONS = ("projects",)
_FALLBACK_SECTIONS = ("raw",)

_SECTION_CREDIT = {
    "skills": 1.0,
    "tools": 1.0,
    "technologies": 1.0,
    "certifications": 0.95,
    "experience": 0.85,
    "responsibilities": 0.85,
    "projects": 0.75,
    "raw": 0.65,
}


def _build_section_pools(resume: ParsedResume) -> dict[str, set[str]]:
    """Build per-section normalized skill pools for section-aware matching."""
    pools: dict[str, set[str]] = {
        "skills": set(),
        "tools": set(),
        "technologies": set(),
        "certifications": set(),
        "experience": set(),
        "responsibilities": set(),
        "projects": set(),
        "raw": set(),
    }

    def _add(pool_key: str, items: list[str]) -> None:
        for item in items:
            for token in decompose_skill_phrase(item):
                pools[pool_key].add(token)
            pools[pool_key].add(canonicalize(item))

    _add("skills", resume.skills)
    _add("tools", resume.tools)
    _add("technologies", resume.technologies)
    _add("certifications", resume.certifications)

    for exp in resume.experience:
        if exp.title:
            _add("experience", [exp.title])
        _add("experience", exp.bullets)
        _add("responsibilities", exp.bullets)

    for proj in resume.projects:
        _add("projects", [proj.name, proj.description, *proj.technologies])

    _add("raw", mine_tech_keywords(resume.raw_text or ""))

    return pools


def _text_contains_skill(raw_text: str, variant: str) -> bool:
    if not raw_text or not variant:
        return False
    raw = raw_text.lower()
    v = variant.lower().strip()
    if len(v) <= 3:
        return re.search(rf"\b{re.escape(v)}\b", raw) is not None
    return v in raw


def _literal_in_pool(pool: set[str], variant: str) -> bool:
    if variant in pool:
        return True
    if len(variant) > 3:
        for r in pool:
            if variant in r or r in variant:
                return True
    return False


def _section_literal_match(
    pools: dict[str, set[str]],
    raw_text: str,
    jd_skill: str,
    search_order: tuple[str, ...],
) -> tuple[float, str]:
    """Search sections in priority order; return best credit and section found."""
    variants = decompose_skill_phrase(jd_skill) or [canonicalize(jd_skill)]
    best_credit = 0.0
    best_section = "none"

    for section in search_order:
        pool = pools.get(section, set())
        section_base = _SECTION_CREDIT.get(section, 0.65)
        for variant in variants:
            if _literal_in_pool(pool, variant):
                return section_base, section
            if section == "raw" and _text_contains_skill(raw_text, variant):
                return section_base, section

    return best_credit, best_section


def _meaningful_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9+#./-]+", canonicalize(text))
        if len(token) > 3 and token not in {"skills", "skill", "tools", "tool"}
    }


def _semantic_match_supported(jd_skill: str, resume_term: str, category: str, bucket_score: float) -> bool:
    """Only allow semantic credit when there is meaningful evidence.

    This prevents nonsense matches like:
    - Microsoft Excel -> SQL
    - Governance -> Collaboration
    - GRC -> Git
    """
    jd_canon = canonicalize(jd_skill)
    resume_canon = canonicalize(resume_term)

    if not jd_canon or not resume_canon:
        return False
    if jd_canon == resume_canon:
        return True
    if find_related_skill(jd_canon, resume_canon):
        return True

    jd_tokens = _meaningful_tokens(jd_skill)
    resume_tokens = _meaningful_tokens(resume_term)
    if jd_tokens & resume_tokens:
        return True

    jd_mined = set(mine_tech_keywords(jd_skill))
    resume_mined = set(mine_tech_keywords(resume_term))
    if jd_mined and resume_mined and jd_mined & resume_mined:
        return True

    # Allow strong phrase-level evidence from experience/projects, but not weak skill-to-skill drift.
    if category in {"experience", "responsibilities", "projects"} and bucket_score >= 80 and len(resume_canon.split()) >= 3:
        return True

    return False


def _semantic_tier(
    jd_skill: str,
    semantic: SemanticMatchResult | None,
    profile: SkillScoreProfile,
) -> float:
    if not semantic:
        return 0.0
    jd_variants = set(decompose_skill_phrase(jd_skill))
    jd_variants.add(canonicalize(jd_skill))
    best = 0.0
    for match in semantic.semantic_matches:
        if match.jd_term not in jd_variants and canonicalize(jd_skill) != match.jd_term:
            continue
        if not _semantic_match_supported(jd_skill, match.resume_term, match.category, match.bucket_score):
            continue
        if match.bucket_score >= _SEMANTIC_FULL:
            best = max(best, profile.semantic_full_credit)
        elif match.bucket_score >= _SEMANTIC_GOOD:
            best = max(best, profile.semantic_good_credit)
        elif match.bucket_score >= _SEMANTIC_PARTIAL:
            best = max(best, profile.semantic_partial_credit)
    return best


def _related_match(
    pools: dict[str, set[str]],
    jd_skill: str,
    profile: SkillScoreProfile,
) -> float:
    jd_canon = canonicalize(jd_skill)
    for section in _SKILL_SECTIONS + _EXPERIENCE_SECTIONS + _PROJECT_SECTIONS:
        for r in pools.get(section, set()):
            if find_related_skill(jd_canon, r):
                return profile.related_credit * _SECTION_CREDIT.get(section, 0.65)
    return 0.0


def _score_skill(
    jd_skill: str,
    pools: dict[str, set[str]],
    raw_text: str,
    semantic: SemanticMatchResult | None,
    profile: SkillScoreProfile,
) -> tuple[float, str]:
    search_order = _SKILL_SECTIONS + _EXPERIENCE_SECTIONS + _PROJECT_SECTIONS + _FALLBACK_SECTIONS
    lit_credit, _ = _section_literal_match(pools, raw_text, jd_skill, search_order)
    if lit_credit >= 1.0:
        return lit_credit, "exact"

    # Partial literal in non-primary sections
    if lit_credit > 0:
        return min(1.0, lit_credit + profile.partial_section_bonus), "section_partial"

    sem = _semantic_tier(jd_skill, semantic, profile)
    if sem > 0:
        return sem, "semantic"

    rel = _related_match(pools, jd_skill, profile)
    if rel > 0:
        return rel, "related"

    return 0.0, "none"


def _match_skill_list(
    skills: list[str],
    pools: dict[str, set[str]],
    raw_text: str,
    semantic: SemanticMatchResult | None,
    profile: SkillScoreProfile,
) -> tuple[list[str], list[str], float]:
    if not skills:
        return [], [], 100.0

    matched: list[str] = []
    missing: list[str] = []
    credits: list[float] = []

    for orig in sorted(set(skills), key=str.lower):
        credit, _ = _score_skill(orig, pools, raw_text, semantic, profile)
        credits.append(credit)
        if credit >= profile.matched_threshold:
            matched.append(orig)
        elif credit >= profile.related_threshold:
            matched.append(f"{orig} (related)")
        else:
            missing.append(orig)

    coverage = round(sum(credits) / len(credits) * 100, 2)
    return matched, missing, coverage


class KeywordMatcher(IKeywordMatcher):
    def match(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
        semantic: SemanticMatchResult | None = None,
    ) -> KeywordMatchResult:
        pools = _build_section_pools(resume)
        raw_text = resume.raw_text or ""

        req_matched, req_missing, req_score = _match_skill_list(
            jd.required_skills, pools, raw_text, semantic, _REQUIRED_PROFILE
        )
        pref_matched, pref_missing, pref_score = _match_skill_list(
            jd.preferred_skills, pools, raw_text, semantic, _PREFERRED_PROFILE
        )

        all_resume: set[str] = set()
        for pool in pools.values():
            all_resume.update(pool)

        all_jd_canon: set[str] = set()
        for skill in jd.required_skills + jd.preferred_skills:
            for token in decompose_skill_phrase(skill):
                all_jd_canon.add(token)
        extra = sorted(r for r in all_resume if r not in all_jd_canon)

        clean_matched = sorted(
            {m.replace(" (related)", "") for m in req_matched + pref_matched},
            key=str.lower,
        )

        return KeywordMatchResult(
            matched_skills=clean_matched,
            missing_skills=sorted(set(req_missing + pref_missing), key=str.lower),
            extra_skills=extra,
            required_skill_score=req_score,
            preferred_skill_score=pref_score if jd.preferred_skills else 100.0,
            keyword_score=req_score,
        )


keyword_matcher = KeywordMatcher()
