"""Dynamic weight allocation and recruiter-style score aggregation."""
from __future__ import annotations

from app.ats.domain.schemas import (
    ATSBreakdown,
    DetailedScoreBreakdown,
    EducationMatchResult,
    ExperienceMatchResult,
    FormattingResult,
    FusionResult,
    KeywordMatchResult,
    MatchScoreResult,
    ParsedJobDescription,
    ParsedResume,
    ProjectMatchResult,
    ScoreBreakdown,
    ScoreWeights,
    SemanticMatchResult,
)

# Base weights — redistributed when JD sections are absent
_BASE_MATCH: dict[str, float] = {
    "required_skills": 0.30,
    "experience": 0.25,
    "responsibilities": 0.20,
    "projects": 0.15,
    "preferred_skills": 0.10,
}

_BASE_ATS: dict[str, float] = {
    "formatting": 0.20,
    "required_skills": 0.20,
    "semantic": 0.25,
    "experience": 0.20,
    "projects": 0.10,
    "education": 0.05,
}


def _jd_applicability(jd: ParsedJobDescription, resume: ParsedResume) -> dict[str, bool]:
    """Which score components apply for this JD/resume pair."""
    # Strict project applicability check
    raw_lower = jd.raw_text.lower()
    project_indicators = (
        "portfolio", "project portfolio", "showcase projects", "github link", 
        "github profile", "side projects", "personal projects", "list of projects", 
        "sample projects", "code samples"
    )
    has_projects_jd = any(kw in raw_lower for kw in project_indicators)
    has_projects_resume = bool(resume.projects)
    projects_applicable = has_projects_jd or has_projects_resume

    return {
        "projects": projects_applicable,
        "responsibilities": bool(jd.responsibilities),
        "preferred_skills": bool(jd.preferred_skills),
        "education": bool(jd.education),
        "certifications": bool(jd.certifications),
    }


def compute_dynamic_weights(
    jd: ParsedJobDescription,
    resume: ParsedResume,
) -> ScoreWeights:
    """
    Redistribute weights when JD sections are missing or not applicable.
    Excluded components have weight 0; remaining weights sum to 1.0.
    """
    applicable = _jd_applicability(jd, resume)

    match = dict(_BASE_MATCH)
    ats = dict(_BASE_ATS)

    if not applicable["projects"]:
        freed = match.pop("projects", 0.0)
        match["required_skills"] += freed * 0.5
        match["experience"] += freed * 0.3
        match["responsibilities"] += freed * 0.2
        ats.pop("projects", None)

    if not applicable["responsibilities"]:
        freed = match.pop("responsibilities", 0.0)
        match["required_skills"] += freed * 0.6
        match["experience"] += freed * 0.4

    if not applicable["preferred_skills"]:
        freed = match.pop("preferred_skills", 0.0)
        match["required_skills"] += freed

    if not applicable["education"] and not applicable["certifications"]:
        ats.pop("education", None)

    # Normalize match weights to sum to 1
    match_total = sum(match.values()) or 1.0
    match = {k: round(v / match_total, 4) for k, v in match.items()}

    ats_total = sum(ats.values()) or 1.0
    ats = {k: round(v / ats_total, 4) for k, v in ats.items()}

    return ScoreWeights(
        match_weights=match,
        ats_weights=ats,
        applicable_sections=applicable,
    )


def _critical_skills(jd: ParsedJobDescription) -> list[str]:
    req = jd.required_skills
    if len(req) <= 6:
        return req
    return req[:6]


def _critical_coverage(keyword: KeywordMatchResult, jd: ParsedJobDescription) -> float:
    critical = _critical_skills(jd)
    if not critical:
        return 100.0
    matched_set = {s.lower() for s in keyword.matched_skills}
    hit = sum(
        1 for s in critical
        if s.lower() in matched_set or any(s.lower() in m for m in matched_set)
    )
    return round(hit / len(critical) * 100, 2)


def build_detailed_scores(
    keyword: KeywordMatchResult,
    semantic: SemanticMatchResult,
    experience: ExperienceMatchResult,
    projects: ProjectMatchResult,
    education: EducationMatchResult,
    formatting: FormattingResult,
    jd: ParsedJobDescription,
    weights: ScoreWeights,
    transferable_skill_score: float = 0.0,
) -> DetailedScoreBreakdown:
    edu_only = education.degree_score if weights.applicable_sections.get("education") else 100.0
    proj_score = projects.project_score if weights.applicable_sections.get("projects") else 100.0
    cert_score = (
        education.certification_score
        if weights.applicable_sections.get("certifications")
        else 100.0
    )
    resp_total = len(jd.responsibilities) or 1
    resp_matched = len(experience.matched_responsibilities)
    resp_pct = (
        round(resp_matched / resp_total * 100, 2)
        if weights.applicable_sections.get("responsibilities")
        else 100.0
    )

    return DetailedScoreBreakdown(
        skill_match_score=round(
            keyword.required_skill_score * 0.7 + semantic.semantic_score * 0.3, 2
        ),
        experience_match_score=experience.experience_score,
        project_match_score=proj_score,
        education_match_score=edu_only,
        certification_match_score=cert_score,
        formatting_score=formatting.formatting_score,
        semantic_similarity_score=semantic.semantic_score,
        required_skill_coverage=keyword.required_skill_score,
        preferred_skill_coverage=keyword.preferred_skill_score,
        responsibilities_match_score=resp_pct,
        domain_match_score=experience.domain_score,
        transferable_skill_score=transferable_skill_score,
        critical_skill_coverage=_critical_coverage(keyword, jd),
        business_impact_score=experience.business_impact_score,
        leadership_score=experience.leadership_score,
    )


def _transferable_score(keyword: KeywordMatchResult, semantic: SemanticMatchResult) -> float:
    """Credit for related/semantic matches that are not literal keyword hits."""
    if not keyword.matched_skills:
        return 0.0
    semantic_only = sum(
        1 for m in semantic.semantic_matches
        if m.bucket_score >= 70 and m.jd_term not in {s.lower() for s in keyword.matched_skills}
    )
    total = len(keyword.matched_skills) + len(keyword.missing_skills) or 1
    return round(min(100.0, (semantic_only / total) * 100 + semantic.semantic_score * 0.15), 2)


def build_score_breakdown(
    keyword: KeywordMatchResult,
    semantic: SemanticMatchResult,
    experience: ExperienceMatchResult,
    projects: ProjectMatchResult,
    education: EducationMatchResult,
    formatting: FormattingResult,
    match: MatchScoreResult,
    weights: ScoreWeights,
    transferable: float,
) -> ScoreBreakdown:

    return ScoreBreakdown(
        keyword=round(keyword.required_skill_score * 0.65 + keyword.preferred_skill_score * 0.35, 2),
        semantic=semantic.semantic_score,
        experience=experience.experience_score,
        responsibilities=match.responsibilities_component,
        projects=projects.project_score if weights.applicable_sections.get("projects") else 100.0,
        education=education.education_score if weights.applicable_sections.get("education") else 100.0,
        formatting=formatting.formatting_score,
        certifications=(
            education.certification_score
            if weights.applicable_sections.get("certifications")
            else 100.0
        ),
        domain=experience.domain_score,
        transferable=transferable,
    )


def calculate_match_score(
    keyword: KeywordMatchResult,
    semantic: SemanticMatchResult,
    experience: ExperienceMatchResult,
    projects: ProjectMatchResult,
    jd: ParsedJobDescription,
    resume: ParsedResume,
    weights: ScoreWeights | None = None,
) -> MatchScoreResult:
    """Recruiter-style Match Score with dynamic section weights."""
    w = weights or compute_dynamic_weights(jd, resume)
    mw = w.match_weights

    resp_total = len(jd.responsibilities) or 1
    resp_matched = len(experience.matched_responsibilities)
    responsibilities_component = (
        round(resp_matched / resp_total * 100, 2)
        if w.applicable_sections.get("responsibilities")
        else 100.0
    )

    required_component = round(
        keyword.required_skill_score * 0.65 + semantic.semantic_score * 0.35, 2
    )
    preferred_component = 100.0
    if w.applicable_sections.get("preferred_skills"):
        preferred_base = keyword.preferred_skill_score
        if preferred_base > 0:
            preferred_component = round(
                min(100.0, preferred_base * 0.8 + semantic.semantic_score * 0.2), 2
            )
        else:
            preferred_component = 0.0
    projects_component = (
        projects.project_score
        if w.applicable_sections.get("projects")
        else 100.0
    )

    raw = (
        required_component * mw.get("required_skills", 0.0)
        + experience.experience_score * mw.get("experience", 0.0)
        + responsibilities_component * mw.get("responsibilities", 0.0)
        + projects_component * mw.get("projects", 0.0)
        + preferred_component * mw.get("preferred_skills", 0.0)
    )

    return MatchScoreResult(
        match_score=int(round(min(raw, 100.0))),
        required_skills_component=required_component,
        responsibilities_component=responsibilities_component,
        experience_component=experience.experience_score,
        projects_component=projects_component,
        preferred_skills_component=preferred_component,
    )


def calculate_ats_score(
    keyword: KeywordMatchResult,
    semantic: SemanticMatchResult,
    experience: ExperienceMatchResult,
    projects: ProjectMatchResult,
    formatting: FormattingResult,
    education: EducationMatchResult,
    jd: ParsedJobDescription,
    resume: ParsedResume,
    weights: ScoreWeights | None = None,
    transferable: float = 0.0,
    match: MatchScoreResult | None = None,
) -> FusionResult:
    """Recruiter-style ATS Score with dynamic section weights."""
    w = weights or compute_dynamic_weights(jd, resume)
    aw = w.ats_weights

    keyword_discoverability = round(
        keyword.required_skill_score * 0.6 + keyword.preferred_skill_score * 0.4, 2
    )

    proj_val = (
        projects.project_score
        if w.applicable_sections.get("projects")
        else 100.0
    )
    edu_val = (
        education.education_score
        if w.applicable_sections.get("education") or w.applicable_sections.get("certifications")
        else 100.0
    )
    cert_val = (
        education.certification_score
        if w.applicable_sections.get("certifications")
        else 100.0
    )
    resp_val = match.responsibilities_component if match else 100.0

    breakdown = ATSBreakdown(
        keyword=keyword_discoverability,
        semantic=semantic.semantic_score,
        experience=experience.experience_score,
        responsibilities=resp_val,
        projects=proj_val,
        formatting=formatting.formatting_score,
        education=edu_val,
        certifications=cert_val,
        domain=experience.domain_score,
        transferable=transferable,
    )

    raw = (
        breakdown.formatting * aw.get("formatting", 0.0)
        + breakdown.keyword * aw.get("required_skills", 0.0)
        + breakdown.semantic * aw.get("semantic", 0.0)
        + breakdown.experience * aw.get("experience", 0.0)
        + breakdown.projects * aw.get("projects", 0.0)
        + breakdown.education * aw.get("education", 0.0)
    )

    return FusionResult(ats_score=int(round(raw)), breakdown=breakdown)


def build_score_explanations(
    detailed: DetailedScoreBreakdown,
    weights: ScoreWeights,
    ats_score: int,
    match_score: int,
) -> dict[str, str]:
    """Generates per-component deterministic recruiter-style explanation texts."""
    exps = {}

    exps["ats_score"] = (
        f"ATS Score is {ats_score}/100. Deductions are mainly due to "
        f"formatting issues ({detailed.formatting_score:.0f}%) or keyword coverage gaps."
    )

    exps["match_score"] = (
        f"Match Score is {match_score}/100. Reflects role alignment based on "
        f"skills, responsibilities overlap, project history, and experience details."
    )

    exps["keyword_score"] = (
        f"Keyword Score is {detailed.required_skill_coverage:.0f}%: reflects direct keyword overlaps "
        f"for critical skills required in the job description."
    )

    exps["semantic_score"] = (
        f"Semantic Score is {detailed.semantic_similarity_score:.0f}%: measures conceptual alignment "
        f"of experience bullets and tools against the role profile."
    )

    exps["experience_score"] = (
        f"Experience is {detailed.experience_match_score:.0f}% because years match requirement "
        f"but leadership experience is scored at {detailed.leadership_score:.0f}% and business impact at {detailed.business_impact_score:.0f}%."
    )

    exps["formatting_score"] = (
        f"Formatting is {detailed.formatting_score:.0f}% because the resume is ATS friendly."
    )

    if weights.applicable_sections.get("education"):
        exps["education_score"] = (
            f"Education is {detailed.education_match_score:.0f}% because the required degree "
            f"is satisfied by the candidate's academic credentials."
        )
    else:
        exps["education_score"] = "Education is 100% because Bachelor's requirement is fully satisfied."

    if weights.applicable_sections.get("projects"):
        exps["project_score"] = (
            f"Project Score is {detailed.project_match_score:.0f}% based on relevance of technologies "
            f"and business problems solved in listed projects."
        )
    else:
        exps["project_score"] = "Projects score is 100% because projects are not requested by the JD."

    exps["responsibilities_score"] = (
        f"Responsibilities Score is {detailed.responsibilities_match_score:.0f}% based on how closely "
        f"experience accomplishments match the day-to-day duties in the JD."
    )

    return exps
