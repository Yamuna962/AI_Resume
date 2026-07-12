"""Validate LLM suggestions against parsed resume and deterministic score constraints."""
from __future__ import annotations

import re

from app.ats.domain.schemas import LLMExplanation, ParsedResume, PrioritizedRecommendations
from app.ats.normalization.skill_tokens import canonicalize, decompose_skill_phrase


def _resume_skill_corpus(resume: ParsedResume) -> set[str]:
    corpus: set[str] = set()
    pools = (
        resume.skills + resume.tools + resume.technologies
        + resume.certifications + resume.achievements
    )
    for item in pools:
        for token in decompose_skill_phrase(item):
            corpus.add(token)
        corpus.add(canonicalize(item))
    for exp in resume.experience:
        if exp.title:
            corpus.add(canonicalize(exp.title))
        for bullet in exp.bullets:
            for token in decompose_skill_phrase(bullet):
                corpus.add(token)
    for proj in resume.projects:
        for token in decompose_skill_phrase(f"{proj.name} {proj.description}"):
            corpus.add(token)
    corpus.update(canonicalize(w) for w in (resume.raw_text or "").lower().split() if len(w) > 3)
    return corpus


def _skill_in_resume(skill: str, corpus: set[str]) -> bool:
    variants = set(decompose_skill_phrase(skill))
    variants.add(canonicalize(skill))
    for v in variants:
        if not v:
            continue
        if v in corpus:
            return True
        for c in corpus:
            if len(v) > 3 and (v in c or c in v):
                return True
    return False


def _filter_suggestion(text: str, corpus: set[str]) -> str | None:
    """Return None if suggestion asks to add a skill already on resume."""
    if not text or not text.strip():
        return None
    # Extract quoted or capitalized skill-like phrases
    candidates = re.findall(r'"([^"]+)"|\'([^\']+)\'|(?:add|include|mention)\s+([A-Za-z0-9./+\-\s]{2,40})', text, re.I)
    flat = [g for tup in candidates for g in tup if g]
    for cand in flat:
        if _skill_in_resume(cand.strip(), corpus):
            return None
    # Check missing_skills patterns in recommendation text
    for word in re.findall(r"\b[A-Z][A-Za-z0-9.+/#\-]{2,}\b", text):
        if _skill_in_resume(word, corpus):
            return None
    return text.strip()


def _filter_list(items: list[str], corpus: set[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        kept = _filter_suggestion(item, corpus)
        if kept:
            out.append(kept)
    return out


def _clean_tokens(s: str) -> set[str]:
    """Normalize, lowercase, and extract meaningful tokens longer than 3 characters."""
    stop_words = {"with", "that", "this", "your", "should", "could", "would", "about", "their", "please", "using"}
    words = re.findall(r'\b\w{3,}\b', s.lower())
    return {w for w in words if w not in stop_words}


def _deduplicate_semantically(items: list[str]) -> list[str]:
    """Remove duplicate or semantically redundant items using token overlap Jaccard similarity."""
    # First pass: remove prefix-dominated items (truncated versions of longer items)
    non_truncated: list[str] = []
    for item in items:
        item = item.strip()
        if not item:
            continue
        dominated = False
        for other in items:
            other = other.strip()
            if other != item and other.startswith(item) and len(other) > len(item):
                dominated = True
                break
        if not dominated:
            non_truncated.append(item)

    cleaned: list[str] = []
    seen_token_sets: list[set[str]] = []
    for item in non_truncated:
        # Deduplicate exact case-insensitive matches immediately
        if any(item.lower() == c.lower() for c in cleaned):
            continue

        tokens = _clean_tokens(item)
        if not tokens:
            cleaned.append(item)
            continue

        duplicate = False
        for existing_tokens in seen_token_sets:
            intersection = tokens & existing_tokens
            union = tokens | existing_tokens
            jaccard = len(intersection) / len(union) if union else 0.0
            # Overlap threshold: if > 50% similar, treat as semantic duplicate
            if jaccard > 0.50:
                duplicate = True
                break
        if not duplicate:
            cleaned.append(item)
            seen_token_sets.append(tokens)
    return cleaned


def _is_formatting_related(text: str) -> bool:
    lowered = text.lower()
    formatting_terms = (
        "format", "formatting", "layout", "ats-friendly", "ats friendly",
        "parseable", "section heading", "resume structure", "resume format",
    )
    return any(term in lowered for term in formatting_terms)


def _is_degree_gap_related(text: str) -> bool:
    lowered = text.lower()
    degree_terms = ("bachelor", "degree", "education requirement", "academic")
    action_terms = ("add", "include", "obtain", "missing", "lacks", "lack", "gap", "weak")
    return any(term in lowered for term in degree_terms) and any(term in lowered for term in action_terms)


def _apply_score_based_filters(
    items: list[str],
    formatting_score: float | None,
    degree_score: float | None,
) -> list[str]:
    filtered: list[str] = []
    for item in items:
        if formatting_score is not None and formatting_score >= 95.0 and _is_formatting_related(item):
            continue
        if degree_score is not None and degree_score >= 95.0 and _is_degree_gap_related(item):
            continue
        filtered.append(item)
    return filtered


def validate_explanation(
    resume: ParsedResume,
    explanation: LLMExplanation,
    formatting_score: float | None = None,
    degree_score: float | None = None,
) -> LLMExplanation:
    """Strip invalid suggestions and merge/deduplicate all user-facing explanation fields."""
    corpus = _resume_skill_corpus(resume)

    missing = [s for s in explanation.missing_skills if not _skill_in_resume(s, corpus)]
    
    # Filter out skills already present in resume from missing lists
    strengths = _deduplicate_semantically(explanation.strengths)
    weaknesses = _deduplicate_semantically(
        _apply_score_based_filters(explanation.weaknesses, formatting_score, degree_score)
    )

    # Process recommendations lists
    recommendations_filtered = _apply_score_based_filters(
        _filter_list(explanation.recommendations, corpus), formatting_score, degree_score
    )
    recommendations = _deduplicate_semantically(recommendations_filtered)

    high_priority = _deduplicate_semantically(
        _apply_score_based_filters(
            _filter_list(explanation.recommendations_prioritized.high_priority, corpus),
            formatting_score,
            degree_score,
        )
    )
    medium_priority = _deduplicate_semantically(
        _apply_score_based_filters(
            _filter_list(explanation.recommendations_prioritized.medium_priority, corpus),
            formatting_score,
            degree_score,
        )
    )
    low_priority = _deduplicate_semantically(
        _apply_score_based_filters(
            _filter_list(explanation.recommendations_prioritized.low_priority, corpus),
            formatting_score,
            degree_score,
        )
    )

    deduped_high = high_priority
    deduped_medium = medium_priority
    deduped_low = low_priority
    # Cross-list deduplication between prioritized tiers using prefix-dominance + exact match

    seen_recs: set[str] = set()
    deduped_final_high: list[str] = []
    for r in deduped_high:
        key = r.lower().strip()
        if key not in seen_recs:
            deduped_final_high.append(r)
            seen_recs.add(key)

    deduped_final_medium: list[str] = []
    for r in deduped_medium:
        key = r.lower().strip()
        # Also skip if it is a prefix of any already-seen recommendation
        dominated = any(existing.startswith(key) and len(existing) > len(key)
                        for existing in seen_recs)
        if key not in seen_recs and not dominated:
            deduped_final_medium.append(r)
            seen_recs.add(key)

    deduped_final_low: list[str] = []
    for r in deduped_low:
        key = r.lower().strip()
        dominated = any(existing.startswith(key) and len(existing) > len(key)
                        for existing in seen_recs)
        if key not in seen_recs and not dominated:
            deduped_final_low.append(r)
            seen_recs.add(key)

    deduped_high, deduped_medium, deduped_low = deduped_final_high, deduped_final_medium, deduped_final_low

    # Fallback to fill prioritized tiers from flat recommendations if prioritized lists are empty
    if not (deduped_high or deduped_medium or deduped_low) and recommendations:
        for i, rec in enumerate(recommendations):
            if i == 0 or "critical" in rec.lower() or "missing" in rec.lower() or "must" in rec.lower():
                deduped_high.append(rec)
            elif i == 1 or "should" in rec.lower() or "add" in rec.lower():
                deduped_medium.append(rec)
            else:
                deduped_low.append(rec)

    return LLMExplanation(
        strengths=strengths,
        weaknesses=weaknesses,
        missing_skills=missing,
        recommendations=recommendations,
        resume_summary=explanation.resume_summary,
        rewritten_summary=explanation.rewritten_summary,
        rewritten_experience=explanation.rewritten_experience,
        project_improvements=_deduplicate_semantically(_filter_list(explanation.project_improvements, corpus)),
        interview_tips=_deduplicate_semantically(explanation.interview_tips),
        reasoning=explanation.reasoning,
        recommendations_prioritized=PrioritizedRecommendations(
            high_priority=deduped_high,
            medium_priority=deduped_medium,
            low_priority=deduped_low,
        ),
    )
