"""
Legacy pipeline entry point — delegates to the deterministic ATS orchestrator.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ats.orchestrator.ats_orchestrator import ats_orchestrator


class AIPipeline:
    async def run(
        self,
        resume_text: str,
        jd_text: str,
        user_id: uuid.UUID,
        resume_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict:
        return await ats_orchestrator.run(
            resume_text, jd_text, user_id, resume_id, db
        )


pipeline = AIPipeline()
