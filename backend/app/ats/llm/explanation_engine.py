"""LLM explanation engine — recruiter persona with generator + auditor passes."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from loguru import logger

from app.ai.gemini_client import gemini_client
from app.ai.groq_client import groq_client
from app.ats.domain.interfaces import ILLMExplanationEngine
from app.ats.domain.schemas import (
    ATSBreakdown,
    DetailedScoreBreakdown,
    ExperienceMatchResult,
    FormattingResult,
    KeywordMatchResult,
    LLMExplanation,
    ParsedJobDescription,
    ParsedResume,
    PrioritizedRecommendations,
    ProjectMatchResult,
    SemanticMatchResult,
)
from app.prompts.recruiter_prompt import (
    RECRUITER_GENERATOR_SYSTEM_PROMPT,
    RESPONSE_AUDITOR_SYSTEM_PROMPT,
    build_recruiter_audit_prompt,
    build_recruiter_explanation_prompt,
)

Analyzer = Callable[[str, str], Awaitable[dict[str, Any]]]


class LLMExplanationEngine(ILLMExplanationEngine):
    """Generates recruiter-style explanations. Scores are immutable and deterministic."""

    async def explain(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
        ats_score: int,
        match_score: int,
        breakdown: ATSBreakdown,
        keyword: KeywordMatchResult,
        semantic: SemanticMatchResult,
        experience: ExperienceMatchResult,
        projects: ProjectMatchResult,
        formatting: FormattingResult,
        detailed_scores: DetailedScoreBreakdown | None = None,
        pre_strengths: list[str] | None = None,
        pre_weaknesses: list[str] | None = None,
        transferable_skills: list[str] | None = None,
    ) -> LLMExplanation:
        detailed = detailed_scores or DetailedScoreBreakdown()
        explanation_prompt = build_recruiter_explanation_prompt(
            ats_score=ats_score,
            match_score=match_score,
            ats_breakdown=breakdown.model_dump(),
            detailed_scores=detailed.model_dump(),
            keyword_matched=keyword.matched_skills,
            keyword_missing=keyword.missing_skills,
            semantic_matches=[m.model_dump() for m in semantic.semantic_matches[:10]],
            experience_matched=experience.matched_responsibilities,
            experience_missing=experience.missing_responsibilities,
            matched_projects=projects.matched_projects,
            formatting_issues=formatting.issues,
            jd_title=jd.job_title,
            jd_required=jd.required_skills,
            jd_preferred=jd.preferred_skills,
            jd_responsibilities=jd.responsibilities,
            resume_summary=resume.summary or resume.raw_text[:400],
            resume_skills=resume.skills,
            resume_tools=resume.tools,
            resume_technologies=resume.technologies,
            resume_certifications=resume.certifications,
            resume_achievements=resume.achievements,
            resume_education=[e.model_dump() for e in resume.education],
            resume_experience=[e.model_dump() for e in resume.experience],
            resume_projects=[p.model_dump() for p in resume.projects],
            transferable_skills=transferable_skills or [],
            domain=jd.domain or "general",
            pre_strengths=pre_strengths,
            pre_weaknesses=pre_weaknesses,
        )

        try:
            raw = await self._generate_and_audit(
                provider_name="Groq",
                analyzer=groq_client.analyze,
                fallback_analyzer=gemini_client.analyze,
                explanation_prompt=explanation_prompt,
                resume=resume,
                ats_score=ats_score,
                match_score=match_score,
                breakdown=breakdown,
                detailed=detailed,
                keyword=keyword,
                transferable_skills=transferable_skills or [],
            )
            logger.info("Recruiter explanation generated via Groq")
        except Exception as groq_err:
            logger.warning(f"Groq explanation failed: {groq_err}, trying Gemini")
            try:
                raw = await self._generate_and_audit(
                    provider_name="Gemini",
                    analyzer=gemini_client.analyze,
                    fallback_analyzer=groq_client.analyze,
                    explanation_prompt=explanation_prompt,
                    resume=resume,
                    ats_score=ats_score,
                    match_score=match_score,
                    breakdown=breakdown,
                    detailed=detailed,
                    keyword=keyword,
                    transferable_skills=transferable_skills or [],
                )
                logger.info("Recruiter explanation generated via Gemini")
            except Exception as gemini_err:
                logger.error(f"Gemini explanation failed: {gemini_err}")
                return self._deterministic_fallback(
                    keyword, experience, projects, formatting,
                    ats_score, match_score, detailed,
                )

        return self._parse_llm_response(raw, keyword)

    async def _generate_and_audit(
        self,
        *,
        provider_name: str,
        analyzer: Analyzer,
        fallback_analyzer: Analyzer,
        explanation_prompt: str,
        resume: ParsedResume,
        ats_score: int,
        match_score: int,
        breakdown: ATSBreakdown,
        detailed: DetailedScoreBreakdown,
        keyword: KeywordMatchResult,
        transferable_skills: list[str],
    ) -> dict[str, Any]:
        generated = await analyzer(explanation_prompt, RECRUITER_GENERATOR_SYSTEM_PROMPT)
        logger.info(f"Recruiter explanation generated via {provider_name}; running audit pass")

        audit_prompt = build_recruiter_audit_prompt(
            generated_response=generated,
            ats_score=ats_score,
            match_score=match_score,
            ats_breakdown=breakdown.model_dump(),
            detailed_scores=detailed.model_dump(),
            matched_skills=keyword.matched_skills,
            missing_skills=keyword.missing_skills,
            transferable_skills=transferable_skills,
            resume_skills=resume.skills,
            resume_tools=resume.tools,
            resume_technologies=resume.technologies,
            resume_certifications=resume.certifications,
            resume_education=[e.model_dump() for e in resume.education],
            resume_experience=[e.model_dump() for e in resume.experience],
            resume_projects=[p.model_dump() for p in resume.projects],
        )

        try:
            audited = await analyzer(audit_prompt, RESPONSE_AUDITOR_SYSTEM_PROMPT)
            logger.info(f"Recruiter audit completed via {provider_name}")
            return audited
        except Exception as primary_audit_err:
            logger.warning(
                f"{provider_name} audit failed: {primary_audit_err}; trying secondary auditor"
            )
            try:
                audited = await fallback_analyzer(audit_prompt, RESPONSE_AUDITOR_SYSTEM_PROMPT)
                logger.info("Recruiter audit completed via secondary provider")
                return audited
            except Exception as secondary_audit_err:
                logger.warning(
                    f"Secondary audit failed: {secondary_audit_err}; using generated output before deterministic validation"
                )
                return generated

    @staticmethod
    def _parse_llm_response(raw: dict[str, Any], keyword: KeywordMatchResult) -> LLMExplanation:
        prioritized_raw = raw.get("recommendations_prioritized") or {}
        if isinstance(prioritized_raw, dict):
            pri = PrioritizedRecommendations(
                high_priority=(
                    prioritized_raw.get("high_priority")
                    or raw.get("high_priority_recommendations")
                    or []
                ),
                medium_priority=(
                    prioritized_raw.get("medium_priority")
                    or raw.get("medium_priority_recommendations")
                    or []
                ),
                low_priority=(
                    prioritized_raw.get("low_priority")
                    or raw.get("low_priority_recommendations")
                    or []
                ),
            )
        else:
            pri = PrioritizedRecommendations(
                high_priority=raw.get("high_priority_recommendations") or [],
                medium_priority=raw.get("medium_priority_recommendations") or [],
                low_priority=raw.get("low_priority_recommendations") or [],
            )

        flat = raw.get("recommendations") or []
        if not flat and (pri.high_priority or pri.medium_priority or pri.low_priority):
            flat = pri.high_priority + pri.medium_priority + pri.low_priority

        return LLMExplanation(
            strengths=raw.get("strengths") or [],
            weaknesses=raw.get("weaknesses") or [],
            missing_skills=raw.get("missing_skills") or keyword.missing_skills,
            recommendations=flat,
            resume_summary=raw.get("resume_summary") or "",
            rewritten_summary=(
                raw.get("rewritten_summary")
                or raw.get("resume_summary")
                or ""
            ),
            rewritten_experience=raw.get("rewritten_experience") or [],
            project_improvements=raw.get("project_improvements") or [],
            interview_tips=(
                raw.get("interview_tips")
                or raw.get("interview_preparation")
                or []
            ),
            reasoning=(
                raw.get("reasoning")
                or raw.get("recruiter_analysis")
                or ""
            ),
            recommendations_prioritized=pri,
        )

    @staticmethod
    def _deterministic_fallback(
        keyword: KeywordMatchResult,
        experience: ExperienceMatchResult,
        projects: ProjectMatchResult,
        formatting: FormattingResult,
        ats_score: int,
        match_score: int,
        detailed: DetailedScoreBreakdown,
    ) -> LLMExplanation:
        """Rule-based recruiter explanation when LLM providers are unavailable."""
        strengths: list[str] = []
        if keyword.matched_skills:
            strengths.append(
                f"Demonstrates {len(keyword.matched_skills)} matched skills including {', '.join(keyword.matched_skills[:4])}."
            )
        if experience.matched_responsibilities:
            strengths.append(
                f"Experience aligns with {len(experience.matched_responsibilities)} key job responsibilities."
            )
        if projects.matched_projects:
            strengths.append(
                f"Relevant work evidence includes {', '.join(projects.matched_projects[:3])}."
            )
        if detailed.formatting_score >= 95:
            strengths.append("Resume formatting is ATS-friendly and easy to parse.")

        weaknesses: list[str] = []
        high_pri: list[str] = []
        med_pri: list[str] = []
        low_pri: list[str] = []

        if keyword.missing_skills:
            weaknesses.append(f"Some required skills are not explicitly shown: {', '.join(keyword.missing_skills[:5])}.")
            high_pri.append(
                f"Add explicit resume evidence only for genuinely held skills such as {', '.join(keyword.missing_skills[:4])}."
            )
        if experience.missing_responsibilities:
            weaknesses.append(
                f"Limited evidence is shown for responsibilities such as {', '.join(experience.missing_responsibilities[:3])}."
            )
            med_pri.append(
                f"Strengthen experience bullets by clarifying responsibility coverage for {', '.join(experience.missing_responsibilities[:2])}."
            )
        if detailed.business_impact_score < 60:
            weaknesses.append("Business impact is under-expressed because achievements are not consistently quantified.")
            med_pri.append("Quantify existing achievements with counts, percentages, turnaround time, or quality metrics where already supported by the resume.")
        if detailed.leadership_score < 60:
            weaknesses.append("Leadership or mentoring indicators are limited in the current wording.")
            low_pri.append("Highlight existing coaching, knowledge transfer, onboarding, or review responsibilities more explicitly if they already appear in the resume.")

        reasoning = (
            f"ATS Score is {ats_score}/100 and Match Score is {match_score}/100. "
            f"The main deductions come from required skill coverage ({detailed.required_skill_coverage:.0f}%), "
            f"experience fit ({detailed.experience_match_score:.0f}%), semantic alignment ({detailed.semantic_similarity_score:.0f}%), "
            f"education match ({detailed.education_match_score:.0f}%), and formatting ({detailed.formatting_score:.0f}%)."
        )

        recs = high_pri + med_pri + low_pri
        if not recs and formatting.recommendations:
            recs = formatting.recommendations[:2]
        if not recs:
            recs = ["Continue tailoring summary and experience bullets to mirror the job description using only factual resume content."]

        return LLMExplanation(
            strengths=strengths or ["Resume contains relevant domain experience and responsibilities."],
            weaknesses=weaknesses,
            missing_skills=keyword.missing_skills,
            recommendations=recs,
            resume_summary="",
            rewritten_summary="",
            rewritten_experience=[],
            project_improvements=["Clarify project scope, technologies used, and business problem solved using only facts already present."] if projects.matched_projects else [],
            interview_tips=[
                f"Prepare specific examples for {', '.join(experience.matched_responsibilities[:3])}."
            ] if experience.matched_responsibilities else [],
            reasoning=reasoning,
            recommendations_prioritized=PrioritizedRecommendations(
                high_priority=high_pri,
                medium_priority=med_pri,
                low_priority=low_pri,
            ),
        )


llm_explanation_engine = LLMExplanationEngine()
