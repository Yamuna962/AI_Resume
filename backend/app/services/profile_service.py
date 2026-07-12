import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.repositories.user_repository import user_repo
from app.schemas.profile import ProfileResponse, ProfileUpdate


class ProfileService:
    async def get_profile(self, db: AsyncSession, user_id: uuid.UUID) -> ProfileResponse:
        user = await user_repo.get_by_id(db, id=user_id)
        if not user:
            raise ValueError("User not found")
            
        # Get stats
        stats_query = select(
            func.count(Analysis.id).label("total"),
            func.avg(Analysis.ats_score).label("avg_ats")
        ).filter(Analysis.user_id == user_id)
        
        result = await db.execute(stats_query)
        stats = result.first()
        
        return ProfileResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            total_analyses=stats.total if stats and stats.total else 0,
            avg_ats_score=round(stats.avg_ats, 1) if stats and stats.avg_ats else 0.0
        )
        
    async def update_profile(self, db: AsyncSession, user_id: uuid.UUID, update_in: ProfileUpdate) -> ProfileResponse:
        user = await user_repo.get_by_id(db, id=user_id)
        if not user:
            raise ValueError("User not found")
            
        update_data = update_in.model_dump(exclude_unset=True)
        await user_repo.update(db, db_obj=user, obj_in=update_data)
        
        return await self.get_profile(db, user_id)


profile_service = ProfileService()
