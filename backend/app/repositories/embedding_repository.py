import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.embedding import ResumeEmbedding
from app.repositories.base import BaseRepository


class EmbeddingRepository(BaseRepository[ResumeEmbedding]):
    def __init__(self):
        super().__init__(ResumeEmbedding)

    async def search_similar(
        self, db: AsyncSession, query_embedding: list[float], user_id: uuid.UUID, top_k: int = 5
    ) -> list[dict]:
        """
        Perform a cosine similarity search on the user's past resumes.
        Returns the most relevant chunks.
        """
        # Using exact nearest neighbor (L2 distance via pgvector)
        # Assuming embedding vector_cosine_ops index is created in DB
        
        query = (
            select(
                ResumeEmbedding.chunk_text,
                ResumeEmbedding.chunk_type,
                ResumeEmbedding.resume_id,
                # 1 - cosine_distance = cosine_similarity
                (1 - ResumeEmbedding.embedding.cosine_distance(query_embedding)).label("similarity")
            )
            .filter(ResumeEmbedding.user_id == user_id)
            .order_by(ResumeEmbedding.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                "chunk_text": row.chunk_text,
                "chunk_type": row.chunk_type,
                "resume_id": row.resume_id,
                "similarity": float(row.similarity)
            }
            for row in rows
        ]


embedding_repo = EmbeddingRepository()
