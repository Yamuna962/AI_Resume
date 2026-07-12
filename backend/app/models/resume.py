"""
Resume ORM model.
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.embedding import ResumeEmbedding
    from app.models.user import User


class Resume(Base):
    """Represents an uploaded resume file and its extracted text."""

    __tablename__ = "resumes"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        index=True,
    )

    # ── Foreign Keys ──────────────────────────────────────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── File Metadata ─────────────────────────────────────────────────────────
    filename: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    storage_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    # ── Extracted Content ─────────────────────────────────────────────────────
    raw_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_size: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="File size in bytes",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User",
        back_populates="resumes",
        lazy="select",
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        "Analysis",
        back_populates="resume",
        cascade="all, delete-orphan",
        lazy="select",
    )

    embeddings: Mapped[list["ResumeEmbedding"]] = relationship(
        "ResumeEmbedding",
        back_populates="resume",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Resume id={self.id} filename={self.filename!r} user_id={self.user_id}>"
