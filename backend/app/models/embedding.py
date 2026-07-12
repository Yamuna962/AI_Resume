import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.user import User


class ResumeEmbedding(Base):
    """Stores vector embeddings of resume chunks for similarity search."""

    __tablename__ = "resume_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        index=True,
    )

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

    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    chunk_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="skills, experience, education, summary"
    )

    embedding: Mapped[list[float]] = mapped_column(Vector(384))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    resume: Mapped["Resume"] = relationship(
        "Resume",
        back_populates="embeddings",
        lazy="select",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="embeddings",
        lazy="select",
    )
