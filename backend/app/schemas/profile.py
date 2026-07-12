from pydantic import BaseModel, ConfigDict, HttpUrl


class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    avatar_url: str | None = None
    total_analyses: int = 0
    avg_ats_score: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None
