"""
SQLAlchemy model registry.

Import `Base` from here when you need fully populated metadata
(e.g. Alembic autogenerate). ORM model files themselves should import Base
from `app.database.base_class` to avoid circular imports.
"""
from app.database.base_class import Base

metadata = Base.metadata
__all__ = ["Base", "metadata"]

# ── Model Imports ─────────────────────────────────────────────────────────────
# Import all models here so that Base.metadata knows about every table.
from app.models.user import User  # noqa: E402, F401
from app.models.resume import Resume  # noqa: E402, F401
from app.models.analysis import Analysis  # noqa: E402, F401
from app.models.rewrite import Rewrite  # noqa: E402, F401
from app.models.embedding import ResumeEmbedding  # noqa: E402, F401
