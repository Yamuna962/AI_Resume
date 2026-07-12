from typing import Any

from app.ai.matching.fusion import FusionResult


class RuleBasedFallback:
    """
    If both Groq and Gemini fail, provides deterministic analysis.
    Scores are algorithm-based; suggestions are generic but domain-neutral.
    """

    def analyze(
        self, fusion_result: FusionResult, resume_sections: dict[str, str], jd_parsed: dict[str, Any]
    ) -> dict[str, Any]:
        score = int(fusion_result.final_score)
        missing = fusion_result.all_missing_skills
        matched = fusion_result.all_matched_skills

        strengths = []
        if matched:
            strengths.append(f"Matches {len(matched)} job requirements: {', '.join(matched[:5])}")
        if fusion_result.exact_score > 50:
            strengths.append("Good keyword overlap with the job description")
        if not strengths:
            strengths.append("Resume submitted for analysis")

        weaknesses = []
        if missing:
            weaknesses.append(
                f"Missing or unclear: {', '.join(missing[:8])}"
                + ("..." if len(missing) > 8 else "")
            )
        weaknesses.append(
            "AI analysis unavailable — configure GROQ_API_KEY or GEMINI_API_KEY in .env for full analysis"
        )

        suggestions = []
        if missing:
            suggestions.append({
                "title": f"Add {missing[0].title()} to your resume",
                "description": (
                    f"The job description requires '{missing[0]}'. "
                    "Add it to your Skills section and mention it in a relevant Experience bullet."
                ),
            })
        suggestions.append({
            "title": "Enable AI analysis",
            "description": (
                "Set GROQ_API_KEY and/or GEMINI_API_KEY in backend/.env and restart the server "
                "for domain-aware analysis with synonym matching and tailored suggestions."
            ),
        })

        return {
            "resume_score": score,
            "ats_score": max(0, score - 10),
            "skill_match_percentage": fusion_result.final_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_areas": [
                "Add missing job keywords to Skills and Experience sections",
                "Configure AI API keys for full cross-domain analysis",
            ],
            "suggestions": suggestions,
            "project_suggestions": [],
            "exact_match_score": fusion_result.exact_score,
            "vector_similarity_score": fusion_result.vector_score,
            "semantic_match_score": fusion_result.semantic_score,
            "rewritten_summary": resume_sections.get("summary", ""),
            "rewritten_resume": "\n".join(v for v in resume_sections.values() if v),
        }


fallback_engine = RuleBasedFallback()
