"""
Resume-related Pydantic schemas.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    """Schema returned after a successful resume upload."""

    model_config = {"from_attributes": True}

    success: bool = True
    resume_id: uuid.UUID = Field(..., description="UUID of the newly created resume record")
    filename: str = Field(..., description="Original uploaded filename")
    storage_url: str | None = Field(None, description="Supabase storage URL")
    file_size: int | None = Field(None, description="File size in bytes")
    text_extracted: bool = Field(
        ..., description="Whether text was successfully extracted from the PDF"
    )
    message: str = Field(default="Resume uploaded successfully.")


class ResumeResponse(BaseModel):
    """Full resume record schema."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    storage_url: str | None
    file_size: int | None
    raw_text: str | None
    created_at: datetime
