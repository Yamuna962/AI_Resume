from typing import Any


def build_analysis_prompt(resume_text: str, jd_text: str, fusion_context: Any) -> str:
    return f"""
Analyze this resume against the job description. This may be ANY role domain
(developer, sales, ERP consultant, marketing, data analyst, etc.) — adapt your analysis accordingly.

--- JOB DESCRIPTION ---
{jd_text}

--- RESUME ---
{resume_text}

--- ALGORITHMIC REFERENCE DATA (optional hint — YOU make the final scoring decision) ---
{fusion_context.context_payload}

The algorithm above uses keyword matching and may miss synonyms or skills buried in Experience.
Use it as a hint only. Your analysis should reflect the FULL resume content.

--- INSTRUCTIONS ---
1. Identify the role domain from the JD (tech, sales, finance, etc.) and analyze accordingly.
2. Determine matched_skills and missing_skills by reading the entire resume.
3. Score ats_score, resume_score, and skill_match_percentage based on your expert judgment.
4. Provide specific, domain-relevant suggestions (not generic "add keywords").
5. Return valid JSON matching the schema below exactly.

--- JSON SCHEMA ---
{{
  "resume_score": <int 0-100>,
  "ats_score": <int 0-100>,
  "skill_match_percentage": <int 0-100>,
  "matched_skills": ["<skill or requirement string>"],
  "missing_skills": ["<skill or requirement string>"],
  "strengths": ["<str>"],
  "weaknesses": ["<str>"],
  "improvement_areas": ["<str>"],
  "suggestions": [{{"title": "<str>", "description": "<str>"}}],
  "project_suggestions": ["<str>"],
  "exact_match_score": {fusion_context.exact_score},
  "vector_similarity_score": {fusion_context.vector_score},
  "semantic_match_score": {fusion_context.semantic_score},
  "rewritten_summary": "<str>",
  "rewritten_resume": "<str>"
}}
"""
