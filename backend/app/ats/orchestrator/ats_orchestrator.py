"""ATS orchestrator — coordinates the full recruiter-style pipeline."""
from __future__ import annotations

import time
import uuid

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.ats.domain.schemas import (
    ATSScoreResult,
    MatchScoreBreakdown,
    ParsedJobDescription,
    ParsedResume,
    PrioritizedRecommendations,
)
from app.ats.engines.education_matcher import education_matcher
from app.ats.engines.experience_matcher import experience_matcher
from app.ats.engines.formatting_analyzer import formatting_analyzer
from app.ats.engines.keyword_matcher import keyword_matcher
from app.ats.engines.project_matcher import project_matcher
from app.ats.engines.semantic_matcher import semantic_matcher
from app.ats.fusion.confidence_engine import compute_confidence_score
from app.ats.fusion.recruiter_score_engine import (
    _transferable_score,
    build_detailed_scores,
    build_score_breakdown,
    build_score_explanations,
    calculate_ats_score,
    calculate_match_score,
    compute_dynamic_weights,
)
from app.ats.llm.explanation_engine import llm_explanation_engine
from app.ats.llm.suggestion_validator import validate_explanation
from app.ats.normalization.skill_normalizer import skill_normalizer
from app.ats.parsers.job_description_parser import job_description_parser
from app.ats.parsers.resume_parser import resume_parser
from app.ats.normalization.skill_tokens import canonicalize, decompose_skill_phrase


def _log_stage_duration(
    stage: str,
    started_at: float,
    resume_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    duration_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        f"ATS stage complete stage={stage} resume_id={resume_id} user_id={user_id} "
        f"duration_ms={duration_ms:.2f}"
    )


class ATSOrchestrator:
    """
    Recruiter-style ATS pipeline.

    Flow: Parse → Normalize → Section Match → Score → Explain
    Scores are deterministic; LLM provides recruiter reasoning only.
    """

    async def run(
        self,
        resume_text: str,
        jd_text: str,
        user_id: uuid.UUID,
        resume_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        logger.info(f"ATS pipeline start resume_id={resume_id} user_id={user_id}")
        pipeline_started = time.perf_counter()

        stage_started = time.perf_counter()
        parsed_resume = resume_parser.parse(resume_text)
        parsed_jd = job_description_parser.parse(jd_text)
        _log_stage_duration("parse", stage_started, resume_id, user_id)

        stage_started = time.perf_counter()
        parsed_resume = skill_normalizer.normalize_resume(parsed_resume)
        parsed_jd = skill_normalizer.normalize_jd(parsed_jd)
        _log_stage_duration("normalize", stage_started, resume_id, user_id)

        stage_started = time.perf_counter()
        semantic = semantic_matcher.match(parsed_resume, parsed_jd)
        _log_stage_duration("semantic", stage_started, resume_id, user_id)

        stage_started = time.perf_counter()
        keyword = keyword_matcher.match(parsed_resume, parsed_jd, semantic=semantic)
        _log_stage_duration("keyword", stage_started, resume_id, user_id)

        stage_started = time.perf_counter()
        experience = experience_matcher.match(parsed_resume, parsed_jd)
        _log_stage_duration("experience", stage_started, resume_id, user_id)

        stage_started = time.perf_counter()
        projects = project_matcher.match(parsed_resume, parsed_jd)
        _log_stage_duration("projects", stage_started, resume_id, user_id)

        stage_started = time.perf_counter()
        education = education_matcher.match(parsed_resume, parsed_jd)
        _log_stage_duration("education", stage_started, resume_id, user_id)

        stage_started = time.perf_counter()
        formatting = formatting_analyzer.analyze(parsed_resume)
        _log_stage_duration("formatting", stage_started, resume_id, user_id)

        stage_started = time.perf_counter()
        weights = compute_dynamic_weights(parsed_jd, parsed_resume)
        transferable = _transferable_score(keyword, semantic)

        match = calculate_match_score(
            keyword, semantic, experience, projects, parsed_jd, parsed_resume, weights,
        )
        fusion = calculate_ats_score(
            keyword, semantic, experience, projects, formatting, education,
            parsed_jd, parsed_resume, weights, transferable, match,
        )
        detailed = build_detailed_scores(
            keyword, semantic, experience, projects, education, formatting,
            parsed_jd, weights, transferable,
        )
        score_breakdown = build_score_breakdown(
            keyword, semantic, experience, projects, education, formatting,
            match, weights, transferable,
        )
        confidence = compute_confidence_score(
            parsed_resume, parsed_jd, keyword, semantic, experience, education, formatting,
        )
        _log_stage_duration("score-fusion", stage_started, resume_id, user_id)

        logger.info(
            f"Recruiter scores: ATS={fusion.ats_score} Match={match.match_score} "
            f"Confidence={confidence} Skills={detailed.required_skill_coverage}"
        )

        # ── SKILL DISPLAY SEPARATION (§12) ──────────────────────────────────
        matched_set = {s.lower() for s in keyword.matched_skills}
        matched_req = []
        matched_pref = []
        
        # Categorize matched skills using canonical mapping and compound phrase matching
        res_canon_set = {canonicalize(s) for s in keyword.matched_skills}
        for skill in parsed_jd.required_skills:
            if any(c in res_canon_set for c in decompose_skill_phrase(skill)):
                matched_req.append(skill)
        for skill in parsed_jd.preferred_skills:
            if any(c in res_canon_set for c in decompose_skill_phrase(skill)):
                matched_pref.append(skill)

        # Transferable skills: semantic matches not in literal list, with score >= 70.0
        transferable_skills = []
        for m in semantic.semantic_matches:
            if m.bucket_score >= 70.0 and m.jd_term.lower() not in matched_set:
                transferable_skills.append(f"{m.jd_term} (demonstrated via {m.resume_term})")
        transferable_skills = sorted(list(set(transferable_skills)))

        # ── DETAILED SCORE EXPLANATIONS (§13) ───────────────────────────────
        score_exps = build_score_explanations(
            detailed, weights, fusion.ats_score, match.match_score
        )

        # ── DETERMINISTIC STRENGTHS & WEAKNESSES GENERATION ─────────────────
        pre_strengths = []
        pre_weaknesses = []
        
        if detailed.required_skill_coverage >= 80.0:
            pre_strengths.append(f"Strong match for required technical skills (matched {len(matched_req)} critical skills).")
        elif detailed.required_skill_coverage < 60.0:
            pre_weaknesses.append("Missing some core technical skills required for the role.")
            
        if detailed.preferred_skill_coverage >= 80.0 and parsed_jd.preferred_skills:
            pre_strengths.append("Possesses key preferred qualifications/skills requested.")
            
        if experience.years_score >= 80.0:
            pre_strengths.append(f"Meets or exceeds the required years of professional experience ({experience.years_score:.0f}% match).")
        elif experience.years_score < 60.0:
            pre_weaknesses.append("Years of experience is below the specified requirement.")
            
        if experience.role_score >= 80.0:
            pre_strengths.append("Previous roles and job titles align closely with the target position.")
        elif experience.role_score < 50.0:
            pre_weaknesses.append("Job title history shows some divergence from the target role profile.")
            
        if experience.domain_score >= 80.0:
            pre_strengths.append(f"Demonstrated domain capability in {parsed_jd.domain}.")
        elif experience.domain_score < 60.0:
            pre_weaknesses.append(f"Limited exposure to the specific {parsed_jd.domain} business domain.")
            
        if experience.leadership_score >= 80.0:
            pre_strengths.append("Clear indicators of team leadership, mentorship, or technical ownership.")
        elif experience.leadership_score < 50.0:
            pre_weaknesses.append("Relatively limited leadership or mentorship indicators in previous experience.")
            
        if experience.business_impact_score >= 80.0:
            pre_strengths.append("Quantifiable business outcomes, KPIs, or optimization metrics listed.")
        elif experience.business_impact_score < 50.0:
            pre_weaknesses.append("Accomplishments could benefit from more quantified business impact or metrics.")

        if projects.project_score >= 80.0 and weights.applicable_sections.get("projects"):
            pre_strengths.append("Project portfolio demonstrates practical implementation of required tech stack.")
        elif projects.project_score < 60.0 and weights.applicable_sections.get("projects"):
            pre_weaknesses.append("Project details lack deep alignment with core responsibilities or technology stack.")

        if education.degree_score >= 90.0 and weights.applicable_sections.get("education"):
            pre_strengths.append("Educational level matches or exceeds target qualifications.")
        elif education.degree_score < 70.0 and weights.applicable_sections.get("education"):
            pre_weaknesses.append("Academic degree level or field of study doesn't fully align with the requested qualifications.")

        if formatting.formatting_score >= 90.0:
            pre_strengths.append("Clean, ATS-compliant formatting and layout structure.")
        elif formatting.formatting_score < 75.0:
            pre_weaknesses.append("Format layout issues detected (such as missing common sections or contact info).")
            
        if not pre_strengths:
            pre_strengths.append("Clear description of technical responsibilities in previous roles.")

        stage_started = time.perf_counter()
        explanation = await llm_explanation_engine.explain(
            parsed_resume,
            parsed_jd,
            fusion.ats_score,
            match.match_score,
            fusion.breakdown,
            keyword,
            semantic,
            experience,
            projects,
            formatting,
            detailed_scores=detailed,
            pre_strengths=pre_strengths,
            pre_weaknesses=pre_weaknesses,
            transferable_skills=transferable_skills,
        )
        explanation = validate_explanation(
            parsed_resume,
            explanation,
            formatting_score=formatting.formatting_score,
            degree_score=education.degree_score,
        )
        _log_stage_duration("explanation", stage_started, resume_id, user_id)

        # Flat recommendations for backward compatibility
        flat_recs = (
            explanation.recommendations_prioritized.high_priority
            + explanation.recommendations_prioritized.medium_priority
            + explanation.recommendations_prioritized.low_priority
        )
        if not flat_recs:
            flat_recs = explanation.recommendations

        # Deduplicate flat_recs: remove any item that is a prefix-substring of another
        deduped_flat: list[str] = []
        for rec in flat_recs:
            dominated = False
            for other in flat_recs:
                if rec != other and other.startswith(rec) and len(other) > len(rec):
                    dominated = True
                    break
            if not dominated:
                deduped_flat.append(rec)
        flat_recs = deduped_flat

        result = ATSScoreResult(
            ats_score=fusion.ats_score,
            match_score=match.match_score,
            confidence_score=confidence,
            keyword_score=keyword.keyword_score,
            semantic_score=semantic.semantic_score,
            experience_score=experience.experience_score,
            project_score=projects.project_score,
            formatting_score=formatting.formatting_score,
            education_score=education.education_score,
            matched_skills=keyword.matched_skills,
            missing_skills=explanation.missing_skills or keyword.missing_skills,
            extra_skills=keyword.extra_skills,
            matched_projects=projects.matched_projects,
            matched_responsibilities=experience.matched_responsibilities,
            strengths=explanation.strengths,
            weaknesses=explanation.weaknesses,
            recommendations=flat_recs,
            recommendations_prioritized=explanation.recommendations_prioritized,
            resume_summary=explanation.resume_summary or explanation.rewritten_summary,
            project_improvements=explanation.project_improvements,
            interview_tips=explanation.interview_tips,
            reasoning=explanation.reasoning,
            breakdown=fusion.breakdown,
            score_breakdown=score_breakdown,
            match_breakdown=MatchScoreBreakdown(
                required_skills=match.required_skills_component,
                responsibilities=match.responsibilities_component,
                experience=match.experience_component,
                projects=match.projects_component,
                preferred_skills=match.preferred_skills_component,
            ),
            score_weights=weights,
            detailed_scores=detailed,
            skill_match_percentage=float(match.match_score),
            resume_score=fusion.ats_score,
            suggestions=[
                {"title": _suggestion_title(rec), "description": rec, "priority": _priority_label(rec, explanation.recommendations_prioritized)}
                for rec in flat_recs[:8]
            ],
            rewritten_summary=explanation.rewritten_summary or explanation.resume_summary,
            rewritten_resume=explanation.rewritten_summary or explanation.resume_summary,
            rewritten_experience=explanation.rewritten_experience,
            # Extended output (§12, §13)
            matched_required_skills=matched_req,
            matched_preferred_skills=matched_pref,
            transferable_skills=transferable_skills,
            score_explanations=score_exps,
        )

        # ── FINAL VALIDATION & SANITIZATION (§15) ───────────────────────────
        result = _validate_and_sanitize(result, parsed_resume, parsed_jd)

        total_duration_ms = (time.perf_counter() - pipeline_started) * 1000
        logger.info(
            f"ATS pipeline complete resume_id={resume_id} user_id={user_id} "
            f"ATS={result.ats_score} Match={result.match_score} duration_ms={total_duration_ms:.2f}"
        )
        return result.model_dump()


def _priority_label(rec: str, prioritized: PrioritizedRecommendations) -> str:
    if rec in prioritized.high_priority:
        return "high"
    if rec in prioritized.medium_priority:
        return "medium"
    if rec in prioritized.low_priority:
        return "low"
    return "medium"


def _suggestion_title(rec: str) -> str:
    """Derive a short, meaningful title from a recommendation sentence.
    
    Strategy: take the first clause before a comma, colon, semicolon or period.
    Strip trailing prepositions/conjunctions. Cap at 60 chars.
    """
    import re
    if not rec:
        return "Improvement suggestion"
    # Split on first sentence-ending separator that creates a meaningful split
    for sep in (":", ";", " — ", " – "):
        if sep in rec:
            return rec.split(sep)[0].strip().rstrip(".,")[:60]
    # Split on first comma that is more than 25 chars in (so "Add X, Y, Z" stays together)
    comma_idx = rec.find(",", 25)
    if 25 < comma_idx < 80:
        return rec[:comma_idx].strip().rstrip(".")[:60]
    # Otherwise first sentence
    sentence_end = re.search(r"[.!?]", rec)
    if sentence_end and sentence_end.start() > 15:
        return rec[:sentence_end.start()].strip()[:60]
    # Fallback: word-boundary truncate at 55
    words = rec.split()
    title = ""
    for w in words:
        if len(title) + len(w) + 1 > 55:
            break
        title = (title + " " + w).strip()
    return title or rec[:55]




def _validate_and_sanitize(
    result: ATSScoreResult, 
    resume: ParsedResume, 
    jd: ParsedJobDescription
) -> ATSScoreResult:
    """Enforces strict final validation rules to ensure data sanity and weight sum consistency."""
    # Deduplicate lists
    result.matched_skills = sorted(list(set(result.matched_skills)))
    result.missing_skills = sorted(list(set(result.missing_skills)))
    result.matched_required_skills = sorted(list(set(result.matched_required_skills)))
    result.matched_preferred_skills = sorted(list(set(result.matched_preferred_skills)))
    result.transferable_skills = sorted(list(set(result.transferable_skills)))
    result.strengths = sorted(list(set(result.strengths)))
    result.weaknesses = sorted(list(set(result.weaknesses)))
    result.recommendations = sorted(list(set(result.recommendations)))

    # Deduplicate prioritized recommendation blocks
    hp = sorted(list(set(result.recommendations_prioritized.high_priority)))
    mp = sorted(list(set(result.recommendations_prioritized.medium_priority)))
    lp = sorted(list(set(result.recommendations_prioritized.low_priority)))

    final_hp, final_mp, final_lp = [], [], []
    seen = set()
    for r in hp:
        if r.lower() not in seen:
            final_hp.append(r)
            seen.add(r.lower())
    for r in mp:
        if r.lower() not in seen:
            final_mp.append(r)
            seen.add(r.lower())
    for r in lp:
        if r.lower() not in seen:
            final_lp.append(r)
            seen.add(r.lower())

    result.recommendations_prioritized.high_priority = final_hp
    result.recommendations_prioritized.medium_priority = final_mp
    result.recommendations_prioritized.low_priority = final_lp

    # Ensure dynamic weights sum exactly to 100% (1.0)
    match_sum = sum(result.score_weights.match_weights.values())
    if abs(match_sum - 1.0) > 0.0001 and result.score_weights.match_weights:
        keys = list(result.score_weights.match_weights.keys())
        diff = 1.0 - match_sum
        result.score_weights.match_weights[keys[0]] = round(result.score_weights.match_weights[keys[0]] + diff, 4)

    ats_sum = sum(result.score_weights.ats_weights.values())
    if abs(ats_sum - 1.0) > 0.0001 and result.score_weights.ats_weights:
        keys = list(result.score_weights.ats_weights.keys())
        diff = 1.0 - ats_sum
        result.score_weights.ats_weights[keys[0]] = round(result.score_weights.ats_weights[keys[0]] + diff, 4)

    # Education Match Sanitization (never assign 0 unless education is truly missing)
    if resume.education and result.education_score == 0.0:
        result.education_score = 40.0
        result.detailed_scores.education_match_score = 40.0
        result.score_breakdown.education = 40.0

    # Ensure optional sections do not reduce scores unfairly
    if not result.score_weights.applicable_sections.get("projects"):
        result.project_score = 100.0
        result.score_breakdown.projects = 100.0
        result.detailed_scores.project_match_score = 100.0

    if not result.score_weights.applicable_sections.get("education"):
        result.education_score = 100.0
        result.score_breakdown.education = 100.0
        result.detailed_scores.education_match_score = 100.0
        # Also update the fusion breakdown so the frontend display is consistent.
        if result.breakdown:
            result.breakdown.education = 100.0

    return result


ats_orchestrator = ATSOrchestrator()
