"""
Loguru logging setup with rotation, retention, and structured JSON output.
"""
import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure Loguru with:
      - Console sink (stderr) with human-readable format in development.
      - Rotating file sink with structured JSON for production/staging.
      - Error-only file sink for alerting purposes.
    """
    # Remove default Loguru handler
    logger.remove()

    log_level = settings.LOG_LEVEL.upper()
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    is_production = settings.is_production

    # ── Console Sink ─────────────────────────────────────────────────────────
    if is_production:
        # Structured JSON to stdout for log aggregators (Datadog, Papertrail, etc.)
        console_format = (
            "{{"
            '"time": "{time:YYYY-MM-DDTHH:mm:ss.SSSZ}", '
            '"level": "{level}", '
            '"name": "{name}", '
            '"function": "{function}", '
            '"line": {line}, '
            '"message": "{message}"'
            "}}"
        )
    else:
        # Human-readable for local development
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

    logger.add(
        sys.stderr,
        format=console_format,
        level=log_level,
        colorize=not is_production,
        enqueue=True,
    )

    # ── General Rotating File Sink ────────────────────────────────────────────
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format=(
            "{time:YYYY-MM-DDTHH:mm:ss.SSSZ} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
        level=log_level,
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        enqueue=True,
        backtrace=True,
        diagnose=not is_production,  # Disable variable introspection in production
    )

    # ── Error-Only File Sink ──────────────────────────────────────────────────
    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        format=(
            "{time:YYYY-MM-DDTHH:mm:ss.SSSZ} | {level: <8} | "
            "{name}:{function}:{line} - {message}\n{exception}"
        ),
        level="ERROR",
        rotation="50 MB",
        retention="60 days",
        compression="gz",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )

    logger.info(
        f"Logging configured. Level={log_level}, Dir={log_dir.resolve()}, "
        f"Production={is_production}"
    )
