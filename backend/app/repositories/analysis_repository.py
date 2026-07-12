import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.analysis import Analysis
from app.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository[Analysis]):
    def __init__(self):
        super().__init__(Analysis)

    async def get_by_user_id_paginated(
        self, db: AsyncSession, user_id: uuid.UUID, page: int = 1, limit: int = 10
    ) -> tuple[list[Analysis], int]:
        skip = (page - 1) * limit
        
        # Get total count
        count_query = select(func.count(Analysis.id)).filter(Analysis.user_id == user_id)
        total = await db.scalar(count_query) or 0
        
        # Get items
        query = (
            select(Analysis)
            .options(joinedload(Analysis.resume))
            .filter(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        items = list(result.scalars().all())
        
        return items, total

    async def get_with_rewrite(self, db: AsyncSession, id: uuid.UUID) -> Analysis | None:
        query = (
            select(Analysis)
            .options(joinedload(Analysis.rewrites))
            .filter(Analysis.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()


analysis_repo = AnalysisRepository()
