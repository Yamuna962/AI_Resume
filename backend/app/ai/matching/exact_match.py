from typing import Any

from pydantic import BaseModel


class ExactMatchResult(BaseModel):
    matched: list[str]
    missing: list[str]
    score: float


class ExactMatcher:
    def match(self, resume_skills: list[str], jd_skills: list[str]) -> ExactMatchResult:
        """
        Performs exact token matching between resume skills and JD skills.
        """
        if not jd_skills:
            return ExactMatchResult(matched=[], missing=[], score=100.0)

        # Normalize
        norm_resume = {s.lower().strip() for s in resume_skills}
        norm_jd = {s.lower().strip() for s in jd_skills}

        matched_set = norm_resume.intersection(norm_jd)
        missing_set = norm_jd - norm_resume

        score = (len(matched_set) / len(norm_jd)) * 100.0 if norm_jd else 100.0

        return ExactMatchResult(
            matched=list(matched_set),
            missing=list(missing_set),
            score=round(score, 2),
        )


exact_matcher = ExactMatcher()
