import time
import uuid
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.pipeline import pipeline
from app.repositories.analysis_repository import analysis_repo
from app.repositories.resume_repository import resume_repo
from app.schemas.analysis import AnalysisRequest


class AnalysisService:
    async def run_analysis(
        self, db: AsyncSession, user_id: uuid.UUID, request: AnalysisRequest
    ) -> Any:
        started_at = time.perf_counter()
        resume = await resume_repo.get_by_id(db, id=request.resume_id)
        if not resume or resume.user_id != user_id:
            raise ValueError("Resume not found")
        if not resume.raw_text:
            raise ValueError("Resume text is missing or could not be extracted")

        analysis = await analysis_repo.create(
            db,
            obj_in={
                "resume_id": resume.id,
                "user_id": user_id,
                "job_description": request.job_description,
                "status": "processing",
            },
        )
        logger.info(
            f"Analysis record created analysis_id={analysis.id} resume_id={resume.id} user_id={user_id}"
        )

        try:
            result_dict = await pipeline.run(
                resume.raw_text,
                request.job_description,
                user_id,
                resume.id,
                db,
            )

            await analysis_repo.update(
                db,
                db_obj=analysis,
                obj_in={
                    "status": "completed",
                    "result_json": result_dict,
                    "ats_score": result_dict.get("ats_score"),
                    "resume_score": result_dict.get("resume_score"),
                    "skill_match_percentage": result_dict.get(
                        "match_score", result_dict.get("skill_match_percentage")
                    ),
                },
            )

            duration_ms = (time.perf_counter() - started_at) * 1000
            logger.info(
                f"Analysis completed analysis_id={analysis.id} resume_id={resume.id} user_id={user_id} "
                f"ats_score={result_dict.get('ats_score')} match_score={result_dict.get('match_score')} "
                f"duration_ms={duration_ms:.2f}"
            )
            return result_dict
        except Exception as exc:
            await analysis_repo.update(db, db_obj=analysis, obj_in={"status": "failed"})
            duration_ms = (time.perf_counter() - started_at) * 1000
            logger.error(
                f"Analysis failed analysis_id={analysis.id} resume_id={resume.id} user_id={user_id} "
                f"duration_ms={duration_ms:.2f} error={exc}"
            )
            raise

    async def get_analysis(
        self, db: AsyncSession, analysis_id: uuid.UUID, user_id: uuid.UUID
    ) -> Any:
        analysis = await analysis_repo.get_by_id(db, id=analysis_id)
        if not analysis or analysis.user_id != user_id:
            return None
        return analysis.result_json


analysis_service = AnalysisService()
