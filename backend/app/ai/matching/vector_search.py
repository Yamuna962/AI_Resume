import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.embedding_repository import embedding_repo


class VectorSearcher:
    async def search_similar_history(
        self,
        query_embedding: list[float],
        user_id: uuid.UUID,
        db: AsyncSession,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Searches the user's past resume embeddings for similar sections to the JD.
        """
        return await embedding_repo.search_similar(db, query_embedding, user_id, top_k)

    def compute_section_similarity(
        self, resume_sections_embeddings: list[list[float]], jd_embedding: list[float]
    ) -> float:
        """
        Computes cosine similarity between current resume chunks and JD.
        In-memory L2/Cosine calculation.
        """
        import numpy as np

        if not resume_sections_embeddings or not jd_embedding:
            return 0.0

        res_np = np.array(resume_sections_embeddings)
        jd_np = np.array(jd_embedding)

        # Compute cosine similarity
        dot_product = np.dot(res_np, jd_np)
        norm_res = np.linalg.norm(res_np, axis=1)
        norm_jd = np.linalg.norm(jd_np)

        similarities = dot_product / (norm_res * norm_jd + 1e-9)

        # Return the max similarity across sections
        return float(np.max(similarities))


vector_searcher = VectorSearcher()
