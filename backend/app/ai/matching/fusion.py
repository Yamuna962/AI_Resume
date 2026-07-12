from pydantic import BaseModel

from app.ai.matching.exact_match import ExactMatchResult
from app.ai.matching.semantic_search import SemanticMatchResult


class FusionResult(BaseModel):
    all_matched_skills: list[str]
    all_missing_skills: list[str]
    final_score: float
    exact_score: float
    vector_score: float
    semantic_score: float
    context_payload: str


class FusionEngine:
    def fuse(
        self,
        exact_result: ExactMatchResult,
        vector_score: float,
        semantic_result: SemanticMatchResult,
        jd_skills: list[str],
    ) -> FusionResult:
        """
        Merges algorithm layer results into reference scores for the LLM.
        Weights: Exact = 30%, Vector = 40%, Semantic = 30%
        """
        matched_set: set[str] = set(exact_result.matched)
        for match in semantic_result.matched:
            matched_set.add(str(match["jd_skill"]).lower())

        all_matched = sorted(matched_set)
        all_missing = [
            s for s in jd_skills if s.lower() not in matched_set
        ]

        final_score = (
            (exact_result.score * 0.30)
            + ((vector_score * 100) * 0.40)
            + (semantic_result.score * 0.30)
        )
        final_score = min(100.0, max(0.0, final_score))

        context = (
            f"--- ALGORITHM REFERENCE (may miss synonyms — LLM should verify) ---\n"
            f"Keyword Exact Match: {exact_result.score:.1f}/100\n"
            f"Semantic Similarity: {semantic_result.score:.1f}/100\n"
            f"Document Vector Similarity: {vector_score:.2f} (0-1 scale)\n"
            f"Combined Algorithm Score: {final_score:.1f}/100\n\n"
            f"Keywords Matched: {exact_result.matched}\n"
            f"Keywords Possibly Missing: {all_missing}\n"
        )

        return FusionResult(
            all_matched_skills=all_matched,
            all_missing_skills=all_missing,
            final_score=round(final_score, 2),
            exact_score=exact_result.score,
            vector_score=round(vector_score * 100, 2),
            semantic_score=semantic_result.score,
            context_payload=context,
        )


fusion_engine = FusionEngine()
