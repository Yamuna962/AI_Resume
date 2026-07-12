import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.analysis import AnalysisRequest
from app.services.analysis_service import analysis_service

router = APIRouter()


@router.post("/run", response_model=dict[str, Any])
async def run_analysis(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await analysis_service.run_analysis(db, current_user.id, request)


@router.get("/{analysis_id}", response_model=dict[str, Any])
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await analysis_service.get_analysis(db, analysis_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result
