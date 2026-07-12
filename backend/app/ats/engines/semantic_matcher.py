"""Section-level semantic matching — embeds Skills/Experience/Projects/Education separately."""
from __future__ import annotations

import numpy as np
from loguru import logger

from app.ats.domain.interfaces import ISemanticMatcher
from app.ats.domain.schemas import ParsedJobDescription, ParsedResume, SemanticMatchItem, SemanticMatchResult
from app.ats.embeddings.embedding_service import embedding_service
from app.ats.normalization.skill_tokens import canonicalize, decompose_skill_phrase

# JD term type → resume sections to search (section-wise matching)
_SECTION_MAP = {
    "skill": ("skills", "tools", "technologies", "certifications"),
    "responsibility": ("experience", "responsibilities"),
    "project": ("projects",),
    "education": ("education",),
}


def _build_section_texts(resume: ParsedResume) -> dict[str, str]:
    """One text block per resume section for embedding."""
    skills_text = " ".join(resume.skills + resume.tools + resume.technologies)
    exp_parts: list[str] = []
    for e in resume.experience:
        if e.title:
            exp_parts.append(e.title)
        if e.company:
            exp_parts.append(e.company)
        exp_parts.extend(e.bullets)
    experience_text = " ".join(exp_parts)
    projects_text = " ".join(
        f"{p.name} {p.description} {' '.join(p.technologies)}".strip()
        for p in resume.projects
    )
    education_text = " ".join(
        f"{e.degree} {e.institution} {e.year}".strip() for e in resume.education
    )
    resp_text = " ".join(resume.responsibilities)

    return {
        "skills": skills_text.strip(),
        "tools": skills_text.strip(),
        "technologies": skills_text.strip(),
        "certifications": " ".join(resume.certifications),
        "experience": experience_text.strip(),
        "responsibilities": resp_text.strip() or experience_text.strip(),
        "projects": projects_text.strip(),
        "education": education_text.strip(),
    }


def _section_embeddings(section_texts: dict[str, str]) -> dict[str, np.ndarray]:
    """Embed each non-empty section as a single vector."""
    embeddings: dict[str, np.ndarray] = {}
    for name, text in section_texts.items():
        if text and len(text) > 5:
            vec = embedding_service.encode([text])
            if vec.size:
                embeddings[name] = vec[0]
    return embeddings


_GENERIC_TERMS = {
    "skill", "skills", "tool", "tools", "technology", "technologies",
    "certification", "certifications", "experience", "responsibility",
    "responsibilities", "project", "projects", "work", "working",
}


def _normalize_term(text: str) -> str | None:
    term = canonicalize(text)
    if not term or len(term) <= 2:
        return None
    if term in _GENERIC_TERMS:
        return None
    return term


def _add_phrase_terms(pool: list[tuple[str, str]], category: str, items: list[str]) -> None:
    """Add normalized phrase-level candidates, not individual random words."""
    seen: set[tuple[str, str]] = set()
    for item in items:
        if not item:
            continue
        candidates = [item, *decompose_skill_phrase(item)]
        for candidate in candidates:
            term = _normalize_term(candidate)
            if not term:
                continue
            key = (term, category)
            if key in seen:
                continue
            seen.add(key)
            pool.append((term, category))


def _term_pool(resume: ParsedResume, categories: tuple[str, ...]) -> list[tuple[str, str]]:
    """Build phrase-level (term, category) pools from structured resume sections."""
    pool: list[tuple[str, str]] = []

    for cat in categories:
        if cat == "skills":
            _add_phrase_terms(pool, cat, resume.skills)
        elif cat == "tools":
            _add_phrase_terms(pool, cat, resume.tools)
        elif cat == "technologies":
            _add_phrase_terms(pool, cat, resume.technologies)
        elif cat == "certifications":
            _add_phrase_terms(pool, cat, resume.certifications)
        elif cat == "experience":
            exp_items: list[str] = []
            for exp in resume.experience:
                if exp.title:
                    exp_items.append(exp.title)
                exp_items.extend(exp.bullets)
            _add_phrase_terms(pool, cat, exp_items)
        elif cat == "responsibilities":
            resp_items = list(resume.responsibilities)
            if not resp_items:
                for exp in resume.experience:
                    resp_items.extend(exp.bullets)
            _add_phrase_terms(pool, cat, resp_items)
        elif cat == "projects":
            proj_items: list[str] = []
            for proj in resume.projects:
                if proj.name:
                    proj_items.append(proj.name)
                if proj.description:
                    proj_items.append(proj.description)
                proj_items.extend(proj.technologies)
            _add_phrase_terms(pool, cat, proj_items)
        elif cat == "education":
            edu_items = [f"{e.degree} {e.institution} {e.year}".strip() for e in resume.education]
            _add_phrase_terms(pool, cat, edu_items)

    return pool


class SemanticMatcher(ISemanticMatcher):
    """Section-constrained embedding matcher with spec cosine thresholds."""

    def match(self, resume: ParsedResume, jd: ParsedJobDescription) -> SemanticMatchResult:
        jd_skill_terms = sorted(
            {
                token
                for skill in jd.required_skills + jd.preferred_skills
                for token in decompose_skill_phrase(skill)
                if token
            },
            key=str.lower,
        )
        jd_resp_terms = [canonicalize(r) for r in jd.responsibilities if len(r) > 10]

        if not jd_skill_terms and not jd_resp_terms:
            return SemanticMatchResult(semantic_score=100.0, confidence=1.0)

        section_texts = _build_section_texts(resume)
        sec_emb = _section_embeddings(section_texts)

        skill_pool = _term_pool(resume, _SECTION_MAP["skill"])
        resp_pool = _term_pool(resume, _SECTION_MAP["responsibility"])

        matches: list[SemanticMatchItem] = []
        bucket_scores: list[float] = []
        raw_sims: list[float] = []
        section_score_acc: dict[str, list[float]] = {}

        # --- JD Skills ↔ Resume Skills sections ---
        if jd_skill_terms and skill_pool:
            pool_terms = [t for t, _ in skill_pool]
            pool_cats = [c for _, c in skill_pool]
            pool_emb = embedding_service.encode(pool_terms)
            jd_emb = embedding_service.encode(jd_skill_terms)

            for i, jd_term in enumerate(jd_skill_terms):
                term_sims = pool_emb @ jd_emb[i]
                best_idx = int(np.argmax(term_sims))
                best_sim = float(term_sims[best_idx])
                bucket = embedding_service.similarity_to_bucket(best_sim)

                # Section-level boost: compare JD term against whole skills section vector
                if "skills" in sec_emb:
                    jd_vec = jd_emb[i]
                    sec_sim = embedding_service.cosine_similarity(jd_vec, sec_emb["skills"])
                    sec_bucket = embedding_service.similarity_to_bucket(sec_sim)
                    bucket = max(bucket, sec_bucket * 0.95)
                    best_sim = max(best_sim, sec_sim)

                raw_sims.append(best_sim)
                bucket_scores.append(bucket)
                cat = pool_cats[best_idx]
                section_score_acc.setdefault(cat, []).append(bucket)
                if bucket > 0:
                    matches.append(
                        SemanticMatchItem(
                            jd_term=jd_term,
                            resume_term=pool_terms[best_idx],
                            similarity=round(best_sim, 4),
                            bucket_score=bucket,
                            category=cat,
                        )
                    )

        # --- JD Responsibilities ↔ Resume Experience sections ---
        if jd_resp_terms and (resp_pool or "experience" in sec_emb):
            if resp_pool:
                pool_terms = [t for t, _ in resp_pool]
                pool_cats = [c for _, c in resp_pool]
                pool_emb = embedding_service.encode(pool_terms)
                jd_emb = embedding_service.encode(jd_resp_terms)

                for i, jd_term in enumerate(jd_resp_terms):
                    term_sims = pool_emb @ jd_emb[i]
                    best_idx = int(np.argmax(term_sims))
                    best_sim = float(term_sims[best_idx])
                    bucket = embedding_service.similarity_to_bucket(best_sim)

                    if "experience" in sec_emb:
                        sec_sim = embedding_service.cosine_similarity(jd_emb[i], sec_emb["experience"])
                        bucket = max(bucket, embedding_service.similarity_to_bucket(sec_sim) * 0.95)
                        best_sim = max(best_sim, sec_sim)

                    raw_sims.append(best_sim)
                    bucket_scores.append(bucket)
                    cat = pool_cats[best_idx]
                    section_score_acc.setdefault(cat, []).append(bucket)
                    if bucket > 0:
                        matches.append(
                            SemanticMatchItem(
                                jd_term=jd_term,
                                resume_term=pool_terms[best_idx],
                                similarity=round(best_sim, 4),
                                bucket_score=bucket,
                                category=cat,
                            )
                        )

        section_scores = {
            k: round(sum(v) / len(v), 2) for k, v in section_score_acc.items() if v
        }
        
        # Avoid double-counting missing skills: only average terms that had some semantic/literal alignment (bucket_score > 0)
        active_buckets = [b for b in bucket_scores if b > 0]
        semantic_score = round(sum(active_buckets) / len(active_buckets), 2) if active_buckets else 0.0
        confidence = round(float(np.mean(raw_sims)), 4) if raw_sims else 0.0

        logger.debug(
            f"Section semantic score={semantic_score}, sections={section_scores}, "
            f"matches={len(matches)}"
        )
        return SemanticMatchResult(
            semantic_matches=sorted(matches, key=lambda m: m.jd_term),
            semantic_score=semantic_score,
            confidence=confidence,
            section_scores=section_scores,
        )


semantic_matcher = SemanticMatcher()
