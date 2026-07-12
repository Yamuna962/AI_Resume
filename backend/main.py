"""
AI Resume Reviewer - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
import time
import uuid

from fastapi import FastAPI
from loguru import logger
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, OperationalError
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api.v1 import analysis, auth, history, profile, resume
from app.core.config import settings
from app.core.logging import setup_logging
from app.database.session import engine
from app.middleware.rate_limit import limiter


DATABASE_UNAVAILABLE_MESSAGE = (
    "Database unavailable. Set DATABASE_URL to a running PostgreSQL instance and apply migrations."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    setup_logging()
    logger.info("Starting AI Resume Reviewer API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL configured: {bool(settings.DATABASE_URL)}")
    logger.info("Database schema is managed by Alembic migrations.")

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully.")
    except Exception as exc:
        logger.error(f"Could not connect to database at startup: {exc}")
        raise RuntimeError(DATABASE_UNAVAILABLE_MESSAGE) from exc

    logger.info("AI Resume Reviewer API is ready.")

    yield

    logger.info("Shutting down AI Resume Reviewer API...")
    await engine.dispose()
    logger.info("Database connections closed. Goodbye!")



def create_application() -> FastAPI:
    """Factory function to create the FastAPI application."""
    application = FastAPI(
        title="AI Resume Reviewer API",
        description="Production-grade AI-powered resume analysis and review platform.",
        version="1.0.0",
        redirect_slashes=False,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    application.state.limiter = limiter

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        client_host = request.client.host if request.client else "unknown"

        logger.info(
            f"Request start request_id={request_id} method={request.method} "
            f"path={request.url.path} client={client_host}"
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                f"Request failed request_id={request_id} method={request.method} "
                f"path={request.url.path} duration_ms={duration_ms:.2f}"
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            f"Request complete request_id={request_id} method={request.method} "
            f"path={request.url.path} status_code={response.status_code} duration_ms={duration_ms:.2f}"
        )
        return response

    @application.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        client_host = request.client.host if request.client else "unknown"
        logger.warning(
            f"Rate limit exceeded request_id={request_id} client={client_host} detail={exc.detail}"
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "error": "Too many requests. Please slow down.",
                "detail": str(exc.detail),
            },
            headers={"X-Request-ID": request_id},
        )

    @application.exception_handler(ConnectionRefusedError)
    async def database_connection_refused_handler(
        request: Request, exc: ConnectionRefusedError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(
            f"Database connection refused request_id={request_id} method={request.method} "
            f"url={request.url} error={exc}"
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": DATABASE_UNAVAILABLE_MESSAGE,
            },
            headers={"X-Request-ID": request_id},
        )

    @application.exception_handler(OperationalError)
    async def sqlalchemy_operational_error_handler(
        request: Request, exc: OperationalError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(
            f"Database operational error request_id={request_id} method={request.method} "
            f"url={request.url} error={exc}"
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": DATABASE_UNAVAILABLE_MESSAGE,
            },
            headers={"X-Request-ID": request_id},
        )

    @application.exception_handler(DBAPIError)
    async def sqlalchemy_dbapi_error_handler(request: Request, exc: DBAPIError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(
            f"Database DBAPI error request_id={request_id} method={request.method} "
            f"url={request.url} error={exc}"
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": DATABASE_UNAVAILABLE_MESSAGE,
            },
            headers={"X-Request-ID": request_id},
        )

    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(
            f"Unhandled exception request_id={request_id} method={request.method} "
            f"url={request.url} error={exc}"
        )
        content = {
            "success": False,
            "error": "An internal server error occurred. Please try again later.",
        }
        if not settings.is_production:
            content["detail"] = str(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
            headers={"X-Request-ID": request_id},
        )

    @application.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            f"ValueError request_id={request_id} method={request.method} url={request.url} error={exc}"
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": str(exc),
            },
            headers={"X-Request-ID": request_id},
        )

    @application.get(
        "/health",
        tags=["Health"],
        summary="Health check endpoint",
        response_description="Returns API health status",
    )
    async def health_check():
        return {
            "success": True,
            "status": "healthy",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
        }

    api_prefix = "/api/v1"
    application.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
    application.include_router(resume.router, prefix=f"{api_prefix}/resume", tags=["Resume"])
    application.include_router(analysis.router, prefix=f"{api_prefix}/analysis", tags=["Analysis"])
    application.include_router(history.router, prefix=f"{api_prefix}/history", tags=["History"])
    application.include_router(profile.router, prefix=f"{api_prefix}/profile", tags=["Profile"])

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
