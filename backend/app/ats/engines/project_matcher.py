"""Project section matching — only when projects are applicable."""
from __future__ import annotations

import numpy as np

from app.ats.domain.interfaces import IProjectMatcher
from app.ats.domain.schemas import ParsedJobDescription, ParsedResume, ProjectMatchResult
from app.ats.embeddings.embedding_service import embedding_service


def _projects_applicable(jd: ParsedJobDescription, resume: ParsedResume) -> bool:
    """
    Projects section is only applicable if the resume explicitly defines projects,
    or the JD specifically requests a portfolio, projects, github repository showcase, etc.
    We avoid generic verbs like 'built' or 'developed' to prevent unfair penalties.
    """
    if resume.projects:
        return True
    
    raw_lower = jd.raw_text.lower()
    project_indicators = (
        "portfolio", "project portfolio", "showcase projects", "github link", 
        "github profile", "side projects", "personal projects", "list of projects", 
        "sample projects", "code samples"
    )
    return any(kw in raw_lower for kw in project_indicators)


class ProjectMatcher(IProjectMatcher):
    """Compares resume projects section against JD responsibilities/skills."""

    def match(self, resume: ParsedResume, jd: ParsedJobDescription) -> ProjectMatchResult:
        if not _projects_applicable(jd, resume):
            return ProjectMatchResult(project_score=100.0, applicable=False)

        jd_targets = jd.responsibilities or jd.required_skills
        if not jd_targets:
            return ProjectMatchResult(project_score=100.0, applicable=False)

        project_texts = [
            f"{p.name} {p.description} {' '.join(p.technologies)}".strip()
            for p in resume.projects
        ]

        if not project_texts:
            # If the JD requested projects, but resume has none:
            return ProjectMatchResult(project_score=50.0, applicable=True)

        proj_emb = embedding_service.encode(project_texts)
        jd_emb = embedding_service.encode(jd_targets)

        matched_projects: list[str] = []
        scores: list[float] = []

        for i, text in enumerate(project_texts):
            sims = proj_emb[i] @ jd_emb.T
            best_sim = float(np.max(sims)) if sims.size else 0.0
            bucket = embedding_service.similarity_to_bucket(best_sim)
            scores.append(bucket)
            # Finer bucket adjustment: >= 52 indicates a positive semantic relationship
            if bucket >= 52:
                matched_projects.append(resume.projects[i].name or text[:80])

        project_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        return ProjectMatchResult(
            project_score=project_score,
            matched_projects=sorted(set(matched_projects)),
            applicable=True,
        )


project_matcher = ProjectMatcher()
