from app.ats.domain.schemas import (
    ExperienceMatchResult,
    KeywordMatchResult,
    ParsedJobDescription,
    ParsedResume,
    ProjectMatchResult,
    SemanticMatchResult,
)
from app.ats.engines.keyword_matcher import keyword_matcher
from app.ats.fusion.recruiter_score_engine import calculate_match_score, compute_dynamic_weights


def test_preferred_skills_get_more_lenient_related_credit_than_required() -> None:
    resume = ParsedResume(skills=["Know Your Customer (KYC)"])

    required_jd = ParsedJobDescription(required_skills=["Customer Due Diligence (CDD)"])
    preferred_jd = ParsedJobDescription(preferred_skills=["Customer Due Diligence (CDD)"])

    required_result = keyword_matcher.match(resume, required_jd)
    preferred_result = keyword_matcher.match(resume, preferred_jd)

    assert required_result.required_skill_score == 38.0
    assert preferred_result.preferred_skill_score == 52.0
    assert preferred_result.preferred_skill_score > required_result.required_skill_score


def test_preferred_component_gets_semantic_boost_when_partial_evidence_exists() -> None:
    keyword = KeywordMatchResult(
        required_skill_score=88.0,
        preferred_skill_score=52.0,
        keyword_score=88.0,
    )
    semantic = SemanticMatchResult(semantic_score=80.0)
    experience = ExperienceMatchResult(experience_score=75.0)
    projects = ProjectMatchResult(project_score=100.0)
    jd = ParsedJobDescription(preferred_skills=["Customer Due Diligence (CDD)"])
    resume = ParsedResume()
    weights = compute_dynamic_weights(jd, resume)

    match = calculate_match_score(
        keyword,
        semantic,
        experience,
        projects,
        jd,
        resume,
        weights,
    )

    assert match.preferred_skills_component == 57.6
    assert match.preferred_skills_component > keyword.preferred_skill_score
