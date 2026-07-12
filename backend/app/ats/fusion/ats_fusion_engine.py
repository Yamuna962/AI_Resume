"""Deterministic ATS fusion engine — weighted score combination."""
from __future__ import annotations

from app.ats.domain.interfaces import IATSFusionEngine
from app.ats.domain.schemas import (
    ATSBreakdown,
    EducationMatchResult,
    ExperienceMatchResult,
    FormattingResult,
    FusionResult,
    KeywordMatchResult,
    ProjectMatchResult,
    SemanticMatchResult,
)

WEIGHTS = {
    "keyword": 0.25,
    "semantic": 0.30,
    "experience": 0.20,
    "projects": 0.10,
    "formatting": 0.10,
    "education": 0.05,
}


class ATSFusionEngine(IATSFusionEngine):
    """
    ATS = Keyword×0.25 + Semantic×0.30 + Experience×0.20
          + Projects×0.10 + Formatting×0.10 + Education×0.05
    Always reproducible — no AI, no randomness.
    """

    def fuse(
        self,
        keyword: KeywordMatchResult,
        semantic: SemanticMatchResult,
        experience: ExperienceMatchResult,
        projects: ProjectMatchResult,
        formatting: FormattingResult,
        education: EducationMatchResult,
    ) -> FusionResult:
        breakdown = ATSBreakdown(
            keyword=keyword.keyword_score,
            semantic=semantic.semantic_score,
            experience=experience.experience_score,
            projects=projects.project_score,
            formatting=formatting.formatting_score,
            education=education.education_score,
        )

        raw = (
            breakdown.keyword * WEIGHTS["keyword"]
            + breakdown.semantic * WEIGHTS["semantic"]
            + breakdown.experience * WEIGHTS["experience"]
            + breakdown.projects * WEIGHTS["projects"]
            + breakdown.formatting * WEIGHTS["formatting"]
            + breakdown.education * WEIGHTS["education"]
        )
        ats_score = int(round(raw))

        return FusionResult(ats_score=ats_score, breakdown=breakdown)


ats_fusion_engine = ATSFusionEngine()
