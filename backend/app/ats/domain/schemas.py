"""Domain schemas for the deterministic ATS scoring engine."""
from pydantic import BaseModel, Field


class ParsedExperience(BaseModel):
    title: str = ""
    company: str = ""
    duration: str = ""
    bullets: list[str] = Field(default_factory=list)


class ParsedProject(BaseModel):
    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)


class ParsedEducation(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""


class ParsedResume(BaseModel):
    personal_info: dict[str, str] = Field(default_factory=dict)
    skills: list[str] = Field(default_factory=list)
    experience: list[ParsedExperience] = Field(default_factory=list)
    projects: list[ParsedProject] = Field(default_factory=list)
    education: list[ParsedEducation] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    summary: str = ""
    domain: str = ""
    raw_text: str = ""


class ParsedJobDescription(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    required_experience: str = ""
    responsibilities: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    job_title: str = ""
    domain: str = ""
    raw_text: str = ""


class KeywordMatchResult(BaseModel):
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    extra_skills: list[str] = Field(default_factory=list)
    required_skill_score: float = 0.0
    preferred_skill_score: float = 0.0
    keyword_score: float = 0.0
    # Separated skill categories (populated by orchestrator)
    matched_required_skills: list[str] = Field(default_factory=list)
    matched_preferred_skills: list[str] = Field(default_factory=list)


class SemanticMatchItem(BaseModel):
    jd_term: str
    resume_term: str
    similarity: float
    bucket_score: float
    category: str


class SemanticMatchResult(BaseModel):
    semantic_matches: list[SemanticMatchItem] = Field(default_factory=list)
    semantic_score: float = 0.0
    confidence: float = 0.0
    section_scores: dict[str, float] = Field(default_factory=dict)


class ExperienceMatchResult(BaseModel):
    experience_score: float = 0.0
    matched_responsibilities: list[str] = Field(default_factory=list)
    missing_responsibilities: list[str] = Field(default_factory=list)
    years_score: float = 0.0
    role_score: float = 0.0
    domain_score: float = 0.0
    # Extended breakdown (spec §3)
    responsibilities_score: float = 0.0
    business_impact_score: float = 0.0
    leadership_score: float = 0.0


class ProjectMatchResult(BaseModel):
    project_score: float = 0.0
    matched_projects: list[str] = Field(default_factory=list)
    applicable: bool = True


class EducationMatchResult(BaseModel):
    education_score: float = 0.0
    certification_score: float = 0.0
    degree_score: float = 0.0


class FormattingResult(BaseModel):
    formatting_score: float = 0.0
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ATSBreakdown(BaseModel):
    keyword: float = 0.0
    semantic: float = 0.0
    experience: float = 0.0
    responsibilities: float = 0.0
    projects: float = 0.0
    formatting: float = 0.0
    education: float = 0.0
    certifications: float = 0.0
    domain: float = 0.0
    transferable: float = 0.0


class ScoreBreakdown(BaseModel):
    """Unified explainability breakdown (mirrors spec output)."""

    keyword: float = 0.0
    semantic: float = 0.0
    experience: float = 0.0
    responsibilities: float = 0.0
    projects: float = 0.0
    education: float = 0.0
    formatting: float = 0.0
    certifications: float = 0.0
    domain: float = 0.0
    transferable: float = 0.0


class FusionResult(BaseModel):
    ats_score: int = 0
    breakdown: ATSBreakdown = Field(default_factory=ATSBreakdown)


class MatchScoreResult(BaseModel):
    match_score: int = 0
    required_skills_component: float = 0.0
    responsibilities_component: float = 0.0
    experience_component: float = 0.0
    projects_component: float = 0.0
    preferred_skills_component: float = 0.0


class PrioritizedRecommendations(BaseModel):
    high_priority: list[str] = Field(default_factory=list)
    medium_priority: list[str] = Field(default_factory=list)
    low_priority: list[str] = Field(default_factory=list)


class LLMExplanation(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    resume_summary: str = ""
    rewritten_summary: str = ""
    rewritten_experience: list[str] = Field(default_factory=list)
    project_improvements: list[str] = Field(default_factory=list)
    interview_tips: list[str] = Field(default_factory=list)
    reasoning: str = ""
    recommendations_prioritized: PrioritizedRecommendations = Field(
        default_factory=PrioritizedRecommendations
    )


class DetailedScoreBreakdown(BaseModel):
    """Independent recruiter-style score components (each 0–100)."""

    skill_match_score: float = 0.0
    experience_match_score: float = 0.0
    project_match_score: float = 0.0
    education_match_score: float = 0.0
    certification_match_score: float = 0.0
    formatting_score: float = 0.0
    semantic_similarity_score: float = 0.0
    required_skill_coverage: float = 0.0
    preferred_skill_coverage: float = 0.0
    responsibilities_match_score: float = 0.0
    domain_match_score: float = 0.0
    transferable_skill_score: float = 0.0
    critical_skill_coverage: float = 0.0
    # Extended (spec §3)
    business_impact_score: float = 0.0
    leadership_score: float = 0.0


class MatchScoreBreakdown(BaseModel):
    """Per-component Match Score breakdown (0-100 each, before weighting)."""

    required_skills: float = 0.0
    responsibilities: float = 0.0
    experience: float = 0.0
    projects: float = 0.0
    preferred_skills: float = 0.0


class ScoreWeights(BaseModel):
    """Dynamic weights used for this analysis (sum to 1.0 per score type)."""

    match_weights: dict[str, float] = Field(default_factory=dict)
    ats_weights: dict[str, float] = Field(default_factory=dict)
    applicable_sections: dict[str, bool] = Field(default_factory=dict)


class ATSScoreResult(BaseModel):
    """Final structured response returned by the ATS engine."""

    ats_score: int = 0
    match_score: int = 0
    confidence_score: float = 0.0
    keyword_score: float = 0.0
    semantic_score: float = 0.0
    experience_score: float = 0.0
    project_score: float = 0.0
    formatting_score: float = 0.0
    education_score: float = 0.0
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    matched_projects: list[str] = Field(default_factory=list)
    matched_responsibilities: list[str] = Field(default_factory=list)
    extra_skills: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    recommendations_prioritized: PrioritizedRecommendations = Field(
        default_factory=PrioritizedRecommendations
    )
    resume_summary: str = ""
    project_improvements: list[str] = Field(default_factory=list)
    interview_tips: list[str] = Field(default_factory=list)
    breakdown: ATSBreakdown = Field(default_factory=ATSBreakdown)
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    match_breakdown: MatchScoreBreakdown = Field(default_factory=MatchScoreBreakdown)
    score_weights: ScoreWeights = Field(default_factory=ScoreWeights)
    detailed_scores: DetailedScoreBreakdown = Field(default_factory=DetailedScoreBreakdown)
    reasoning: str = ""
    # Backward compatibility for frontend
    skill_match_percentage: float = 0.0
    resume_score: int = 0
    suggestions: list[dict[str, str]] = Field(default_factory=list)
    rewritten_summary: str = ""
    rewritten_resume: str = ""
    rewritten_experience: list[str] = Field(default_factory=list)
    # Extended output (spec §12, §13)
    matched_required_skills: list[str] = Field(default_factory=list)
    matched_preferred_skills: list[str] = Field(default_factory=list)
    transferable_skills: list[str] = Field(default_factory=list)
    score_explanations: dict[str, str] = Field(default_factory=dict)
