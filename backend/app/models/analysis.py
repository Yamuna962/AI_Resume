"""
Analysis ORM model.
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.rewrite import Rewrite
    from app.models.user import User


class Analysis(Base):
    """Stores the result of an AI resume analysis run."""

    __tablename__ = "analyses"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        index=True,
    )

    # ── Foreign Keys ──────────────────────────────────────────────────────────
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Input ─────────────────────────────────────────────────────────────────
    job_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # ── AI Results ────────────────────────────────────────────────────────────
    result_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Full structured AI analysis output",
    )

    ats_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="ATS score 0-100",
    )

    resume_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Overall resume quality score 0-100",
    )

    skill_match_percentage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Percentage of JD skills matched",
    )

    # ── Processing Status ─────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
        comment="One of: pending, processing, completed, failed",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    resume: Mapped["Resume"] = relationship(  # type: ignore[name-defined]
        "Resume",
        back_populates="analyses",
        lazy="select",
    )

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User",
        back_populates="analyses",
        lazy="select",
    )

    rewrites: Mapped[list["Rewrite"]] = relationship(  # type: ignore[name-defined]
        "Rewrite",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<Analysis id={self.id} resume_id={self.resume_id} "
            f"status={self.status!r} ats_score={self.ats_score}>"
        )
