import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analysis_repository import analysis_repo
from app.schemas.history import HistoryResponse


class HistoryService:
    async def get_user_history(
        self, db: AsyncSession, user_id: uuid.UUID, page: int = 1, limit: int = 10
    ) -> HistoryResponse:
        items, total = await analysis_repo.get_by_user_id_paginated(db, user_id, page, limit)
        
        history_items = []
        for item in items:
            history_items.append({
                "id": item.id,
                "job_description": item.job_description[:100] + "..." if item.job_description else "",
                "ats_score": item.ats_score,
                "resume_score": item.resume_score,
                "skill_match_percentage": item.skill_match_percentage,
                "status": item.status,
                "created_at": item.created_at,
                "resume_filename": item.resume.filename if item.resume else None
            })
            
        return HistoryResponse(
            items=history_items,
            total=total,
            page=page,
            limit=limit
        )


history_service = HistoryService()
