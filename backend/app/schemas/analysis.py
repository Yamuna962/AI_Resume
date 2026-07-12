"""
Analysis-related Pydantic schemas.
Full AI result schema with all matching layers and LLM outputs.
"""
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ── Sub-schemas ───────────────────────────────────────────────────────────────

class MatchedSkill(BaseModel):
    """Represents a skill that was matched between resume and job description."""

    skill: str = Field(..., description="The matched skill name")
    match_type: Literal["exact", "semantic", "vector"] = Field(
        ..., description="How this skill was matched"
    )


class Suggestion(BaseModel):
    """A concrete improvement suggestion for the resume."""

    title: str = Field(..., description="Short title of the suggestion")
    description: str = Field(..., description="Detailed explanation of the suggestion")


# ── Request Schemas ───────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    """Request body to trigger a resume analysis."""

    resume_id: uuid.UUID = Field(..., description="UUID of the previously uploaded resume")
    job_description: str = Field(
        ...,
        min_length=50,
        max_length=20000,
        description="The full job description text to analyze against",
    )


# ── Response Schemas ──────────────────────────────────────────────────────────

class AnalysisResult(BaseModel):
    """
    The complete structured AI analysis result.
    This mirrors the exact JSON schema the LLM is instructed to return.
    """

    # Overall scores
    resume_score: int = Field(..., ge=0, le=100, description="Overall resume quality score")
    ats_score: int = Field(..., ge=0, le=100, description="ATS compatibility score")
    skill_match_percentage: float = Field(
        ..., ge=0.0, le=100.0, description="Percentage of JD skills matched"
    )

    # Skills analysis
    matched_skills: list[MatchedSkill] = Field(
        default_factory=list, description="Skills present in both resume and JD"
    )
    missing_skills: list[str] = Field(
        default_factory=list, description="Skills required by JD but absent from resume"
    )

    # Qualitative feedback
    strengths: list[str] = Field(
        default_factory=list, description="Key strengths identified in the resume"
    )
    weaknesses: list[str] = Field(
        default_factory=list, description="Weaknesses or gaps identified"
    )
    improvement_areas: list[str] = Field(
        default_factory=list, description="Specific areas the candidate should improve"
    )
    suggestions: list[Suggestion] = Field(
        default_factory=list, description="Actionable improvement suggestions"
    )
    project_suggestions: list[str] = Field(
        default_factory=list, description="Suggested projects to build for missing skills"
    )

    # Matching layer scores
    exact_match_score: float = Field(
        ..., ge=0.0, le=100.0, description="Raw exact keyword match score"
    )
    vector_similarity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Cosine similarity from vector search (0-1)"
    )
    semantic_match_score: float = Field(
        ..., ge=0.0, le=100.0, description="Semantic similarity match score"
    )

    # AI-generated rewrite
    rewritten_summary: str = Field(
        ..., description="AI-rewritten professional summary tailored to the JD"
    )
    rewritten_resume: str = Field(
        ..., description="Full AI-rewritten resume text tailored to the JD"
    )


class AnalysisResponse(BaseModel):
    """Full API response wrapping the analysis result."""

    model_config = {"from_attributes": True}

    success: bool = True
    analysis_id: uuid.UUID
    resume_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    result: AnalysisResult | None = None
    created_at: datetime
    message: str = "Analysis completed successfully."


class AnalysisStatusResponse(BaseModel):
    """Lightweight status check response."""

    analysis_id: uuid.UUID
    status: str
    message: str
