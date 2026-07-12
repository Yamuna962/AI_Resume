"""
Async SQLAlchemy engine, session factory, and FastAPI dependency.
"""
import ssl
from collections.abc import AsyncGenerator

from loguru import logger
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.database import base as _model_registry  # noqa: F401


# ── Engine ─────────────────────────────────────────────────────────────────────
_database_url = make_url(settings.DATABASE_URL)
_database_host = (_database_url.host or "").lower()
_is_local_database = _database_host in {"", "localhost", "127.0.0.1"}

_connect_args: dict[str, object] = {}
if not _is_local_database:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    _connect_args["ssl"] = ssl_context

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    future=True,
    connect_args=_connect_args,
)

# ── Session Factory ────────────────────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Important: keep objects usable after commit
)


# ── Dependency ─────────────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.
    Commits on success, rolls back on exception, always closes session.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database session error, rolled back: {exc}")
            raise
        finally:
            await session.close()
