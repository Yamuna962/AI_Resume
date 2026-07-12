"""Deterministic Match Score engine — JD-specific fit score."""
from __future__ import annotations

from app.ats.domain.interfaces import IMatchScoreEngine
from app.ats.domain.schemas import (
    ExperienceMatchResult,
    KeywordMatchResult,
    MatchScoreResult,
    ParsedJobDescription,
    ProjectMatchResult,
    SemanticMatchResult,
)


class MatchScoreEngine(IMatchScoreEngine):
    """
    Match Score =
      Required Skills  40%
      Responsibilities 20%
      Experience       20%
      Projects         10%
      Preferred Skills 10%
    """

    def calculate(
        self,
        keyword: KeywordMatchResult,
        semantic: SemanticMatchResult,
        experience: ExperienceMatchResult,
        projects: ProjectMatchResult,
        jd: ParsedJobDescription,
    ) -> MatchScoreResult:
        required_component = keyword.required_skill_score
        preferred_component = keyword.preferred_skill_score

        resp_total = len(jd.responsibilities)
        resp_matched = len(experience.matched_responsibilities)
        responsibilities_component = (
            (resp_matched / resp_total * 100) if resp_total else 100.0
        )

        experience_component = experience.experience_score
        projects_component = projects.project_score

        raw = (
            required_component * 0.40
            + responsibilities_component * 0.20
            + experience_component * 0.20
            + projects_component * 0.10
            + preferred_component * 0.10
        )

        # Small boost when semantic still exceeds keyword (partial gaps only)
        if semantic.semantic_score > required_component + 15:
            raw += min(5.0, (semantic.semantic_score - required_component) * 0.05)

        return MatchScoreResult(
            match_score=int(round(min(raw, 100.0))),
            required_skills_component=round(required_component, 2),
            responsibilities_component=round(responsibilities_component, 2),
            experience_component=round(experience_component, 2),
            projects_component=round(projects_component, 2),
            preferred_skills_component=round(preferred_component, 2),
        )


match_score_engine = MatchScoreEngine()
