import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoryItem(BaseModel):
    id: uuid.UUID
    job_description: str
    ats_score: int | None
    resume_score: int | None
    skill_match_percentage: float | None
    status: str
    created_at: datetime
    resume_filename: str | None = None

    model_config = ConfigDict(from_attributes=True)


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    limit: int
