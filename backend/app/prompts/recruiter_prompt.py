"""Recruiter-grade generator + auditor prompts for ATS explanation output."""
from __future__ import annotations

import json
from typing import Any


def _to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


RECRUITER_GENERATOR_SYSTEM_PROMPT = """You are a Principal Technical Recruiter, ATS Architect, HR Technology Expert, Senior AI Engineer, Resume Reviewer, and Prompt Engineer.

Your task is to produce a recruiter-grade ATS explanation by comparing a parsed Resume with a parsed Job Description using ONLY the deterministic analysis findings provided to you.

IMPORTANT
- You are NOT recalculating scores.
- ATS Score and Match Score are FINAL.
- Never modify them.
- Never invent, hallucinate, or assume missing facts.
- Every conclusion must be grounded in the parsed resume or the deterministic analysis provided.

STRICT RULES
1. Never invent skills, experience, projects, certifications, responsibilities, job titles, technologies, metrics, achievements, or education.
2. Never say the candidate knows something unless it explicitly exists in the parsed resume.
3. If a required skill does not exist, classify it as a missing skill. Do not convert it into an existing skill.
4. If similar capabilities exist, treat them as transferable skills, not matched skills.
5. Never recommend adding a skill that already exists in the parsed resume.
6. Never recommend formatting improvements when formatting_score >= 95.
7. Never recommend adding a Bachelor's degree when education_match_score >= 95.
8. Rewrites may improve grammar, wording, ATS readability, structure, action verbs, and keyword placement — but must use ONLY facts already present in the resume.
9. Do not contradict the deterministic findings.

Your job is to generate these explanation fields only:
- strengths
- weaknesses
- missing_skills
- prioritized recommendations
- recruiter analysis
- rewritten summary
- rewritten experience
- interview preparation
- project improvements

Return ONLY valid JSON."""


RESPONSE_AUDITOR_SYSTEM_PROMPT = """You are a Response Auditor.

Review the generated ATS analysis.

Check:
1. Did the AI invent any skill?
2. Did the AI invent any experience?
3. Did the AI invent any certification?
4. Did the AI recommend a skill that already exists?
5. Did the AI contradict the ATS or Match score?
6. Did the AI suggest formatting improvements when formatting is already above 95%?
7. Did the AI classify transferable skills as matched skills?
8. Did the AI rewrite the resume using facts not present in the original resume?

If any issue is found:
- Correct it.
- Remove hallucinations.
- Remove duplicate suggestions.
- Keep only factually supported recommendations.

Return the corrected JSON only. Do not add markdown."""


EXPLANATION_JSON_SCHEMA = """
{
  "strengths": ["<top factual strengths grounded in the parsed resume and deterministic findings>"],
  "weaknesses": ["<genuine gaps only; no contradictions with deterministic findings>"],
  "missing_skills": ["<skills truly absent from the parsed resume>"],
  "recommendations": ["<optional flat recommendations list; may be omitted if recommendations_prioritized is present>"],
  "recommendations_prioritized": {
    "high_priority": ["<actionable must-fix recommendations>"],
    "medium_priority": ["<actionable meaningful improvements>"],
    "low_priority": ["<actionable low-priority polish items>"]
  },
  "resume_summary": "<short factual recruiter summary>",
  "rewritten_summary": "<rewritten summary using only facts present in the parsed resume>",
  "rewritten_experience": ["<rewritten experience bullets using only existing resume facts>"],
  "project_improvements": ["<factual project improvement suggestions when relevant>"],
  "interview_preparation": ["<topics the candidate should prepare to discuss based on actual background>"],
  "recruiter_analysis": "<recruiter explanation of why ATS and Match scores received deductions, grounded in deterministic findings>"
}
"""


def build_recruiter_explanation_prompt(
    *,
    ats_score: int,
    match_score: int,
    ats_breakdown: dict[str, Any],
    detailed_scores: dict[str, Any],
    keyword_matched: list[str],
    keyword_missing: list[str],
    semantic_matches: list[dict[str, Any]],
    experience_matched: list[str],
    experience_missing: list[str],
    matched_projects: list[str],
    formatting_issues: list[str],
    jd_title: str,
    jd_required: list[str],
    jd_preferred: list[str],
    jd_responsibilities: list[str],
    resume_summary: str,
    resume_skills: list[str] | None = None,
    resume_tools: list[str] | None = None,
    resume_technologies: list[str] | None = None,
    resume_certifications: list[str] | None = None,
    resume_achievements: list[str] | None = None,
    resume_education: list[dict[str, str]] | None = None,
    resume_experience: list[dict[str, Any]] | None = None,
    resume_projects: list[dict[str, Any]] | None = None,
    transferable_skills: list[str] | None = None,
    domain: str = "general",
    pre_strengths: list[str] | None = None,
    pre_weaknesses: list[str] | None = None,
) -> str:
    resume_payload = {
        "summary": resume_summary,
        "skills": resume_skills or [],
        "tools": resume_tools or [],
        "technologies": resume_technologies or [],
        "certifications": resume_certifications or [],
        "achievements": resume_achievements or [],
        "education": resume_education or [],
        "experience": resume_experience or [],
        "projects": resume_projects or [],
    }

    jd_payload = {
        "title": jd_title,
        "required_skills": jd_required,
        "preferred_skills": jd_preferred,
        "responsibilities": jd_responsibilities,
        "domain": domain,
    }

    deterministic_payload = {
        "ats_score": ats_score,
        "match_score": match_score,
        "ats_breakdown": ats_breakdown,
        "detailed_scores": detailed_scores,
        "matched_skills": keyword_matched,
        "missing_skills": keyword_missing,
        "semantic_matches": semantic_matches[:10],
        "matched_responsibilities": experience_matched,
        "missing_responsibilities": experience_missing,
        "matched_projects": matched_projects,
        "transferable_skills": transferable_skills or [],
        "formatting_issues": formatting_issues,
        "precomputed_strengths": pre_strengths or [],
        "precomputed_weaknesses": pre_weaknesses or [],
    }

    return f"""Perform a recruiter-grade ATS explanation.

Use ONLY the parsed resume facts and deterministic engine findings below.
Do NOT recalculate ATS Score or Match Score.
Do NOT invent skills, experience, certifications, education, projects, metrics, or achievements.
Do NOT convert transferable skills into matched skills.
Do NOT recommend formatting improvements when formatting_score >= 95.
Do NOT recommend adding a Bachelor's degree when education_match_score >= 95.
Do NOT recommend adding skills already present on the resume.
For rewritten_summary and rewritten_experience, improve wording only — use facts already present.

PARSED RESUME
{_to_json(resume_payload)}

PARSED JOB DESCRIPTION
{_to_json(jd_payload)}

DETERMINISTIC ATS ANALYSIS
{_to_json(deterministic_payload)}

Instructions:
- Explain only the provided deterministic strengths and weaknesses.
- Missing skills must be truly absent from the parsed resume.
- Transferable skills are already provided by the deterministic pipeline; do not convert them into matched skills.
- If formatting_score is 100 or very high, do not mention formatting improvements.
- If education_match_score is 100 or very high, do not describe education as weak and do not recommend adding a degree.
- Recruiter analysis must explain where score deductions came from using the deterministic component scores.
- Recommendations must be actionable, deduplicated, and factual.

Return JSON only using this schema:
{EXPLANATION_JSON_SCHEMA}"""


def build_recruiter_audit_prompt(
    *,
    generated_response: dict[str, Any],
    ats_score: int,
    match_score: int,
    ats_breakdown: dict[str, Any],
    detailed_scores: dict[str, Any],
    matched_skills: list[str],
    missing_skills: list[str],
    transferable_skills: list[str],
    resume_skills: list[str],
    resume_tools: list[str],
    resume_technologies: list[str],
    resume_certifications: list[str],
    resume_education: list[dict[str, str]],
    resume_experience: list[dict[str, Any]],
    resume_projects: list[dict[str, Any]],
) -> str:
    resume_facts = {
        "skills": resume_skills,
        "tools": resume_tools,
        "technologies": resume_technologies,
        "certifications": resume_certifications,
        "education": resume_education,
        "experience": resume_experience,
        "projects": resume_projects,
    }
    deterministic_guardrails = {
        "ats_score": ats_score,
        "match_score": match_score,
        "ats_breakdown": ats_breakdown,
        "detailed_scores": detailed_scores,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "transferable_skills": transferable_skills,
        "formatting_score": detailed_scores.get("formatting_score"),
        "education_match_score": detailed_scores.get("education_match_score"),
    }

    return f"""Audit and correct the generated ATS explanation.

PARSED RESUME FACTS
{_to_json(resume_facts)}

DETERMINISTIC GUARDRAILS
{_to_json(deterministic_guardrails)}

GENERATED RESPONSE TO AUDIT
{_to_json(generated_response)}

Validation rules:
- Remove hallucinated skills, experience, certifications, projects, metrics, technologies, and achievements.
- Remove recommendations for skills already present in the parsed resume.
- Remove formatting suggestions if formatting_score >= 95.
- Remove degree-addition suggestions if education_match_score >= 95.
- Do not allow contradictions with the deterministic ATS/Match scores or their breakdowns.
- Do not allow transferable skills to be rewritten as matched skills.
- Ensure rewritten_summary and rewritten_experience use only facts present in the parsed resume.
- Remove duplicate strengths, weaknesses, and recommendations.

Return corrected JSON only using this schema:
{EXPLANATION_JSON_SCHEMA}"""
