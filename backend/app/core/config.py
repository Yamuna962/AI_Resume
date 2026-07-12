"""
Application Configuration using Pydantic Settings.
All environment variables are read and validated here.
"""
import json
from functools import lru_cache
from typing import Any, List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration class. All values come from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Database ────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ai_resume"

    # ── Supabase ─────────────────────────────────────────────────────────────
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your-anon-key"
    SUPABASE_SERVICE_KEY: str = "your-service-role-key"
    SUPABASE_STORAGE_BUCKET: str = "resumes"

    # ── AI Providers ─────────────────────────────────────────────────────────
    GROQ_API_KEY: str = "your-groq-api-key"
    GEMINI_API_KEY: str = "your-gemini-api-key"

    # ── JWT ──────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # ── File Upload ──────────────────────────────────────────────────────────
    MAX_FILE_SIZE_MB: int = 10

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATELIMIT_PER_MINUTE: int = 20

    # ── OCR (Tesseract) ───────────────────────────────────────────────────────
    TESSERACT_CMD: str = ""

    # ── App Meta ─────────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    API_V1_STR: str = "/api/v1"

    # ── Derived Properties ───────────────────────────────────────────────────
    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def rate_limit_string(self) -> str:
        return f"{self.RATELIMIT_PER_MINUTE}/minute"

    # ── Validators ───────────────────────────────────────────────────────────
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Accept JSON string or list."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [v]
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return [str(v)]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL must be set.")
        return v

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production", "testing"}
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {allowed}")
        return v_lower


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings instance — only loaded once per process."""
    return Settings()


# Module-level singleton for import convenience
settings: Settings = get_settings()
