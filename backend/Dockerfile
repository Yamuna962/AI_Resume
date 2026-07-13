# syntax=docker/dockerfile:1

# ==========================================================
# Stage 1 - Build dependencies
# ==========================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Create virtual environment
RUN python -m venv /venv

ENV PATH="/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================================
# Stage 2 - Runtime
# ==========================================================
FROM python:3.11-slim

LABEL maintainer="AI Resume Reviewer"
LABEL version="2.0"

WORKDIR /app

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# Create application user
# ----------------------------------------------------------
RUN groupadd --system appgroup && \
    useradd --system \
    --gid appgroup \
    --home-dir /app \
    appuser

# ----------------------------------------------------------
# Copy virtual environment
# ----------------------------------------------------------
COPY --from=builder /venv /venv

# ----------------------------------------------------------
# Copy application
# ----------------------------------------------------------
COPY --chown=appuser:appgroup . .

# Create writable log directory for the non-root user
RUN mkdir -p /app/logs && chown -R appuser:appgroup /app/logs

# ----------------------------------------------------------
# Create writable directories
# ----------------------------------------------------------
RUN mkdir -p /app/logs && \
    mkdir -p /app/.cache && \
    mkdir -p /app/.cache/huggingface && \
    mkdir -p /app/uploads && \
    chown -R appuser:appgroup /app

# ----------------------------------------------------------
# Environment variables
# ----------------------------------------------------------
ENV PATH="/venv/bin:$PATH"

ENV PYTHONPATH=/app

ENV HOME=/app

ENV PYTHONUNBUFFERED=1

ENV PYTHONDONTWRITEBYTECODE=1

# HuggingFace cache
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/huggingface
ENV XDG_CACHE_HOME=/app/.cache

# ----------------------------------------------------------
# Switch user
# ----------------------------------------------------------
USER appuser

# ----------------------------------------------------------
# Expose port
# ----------------------------------------------------------
EXPOSE 8000

# ----------------------------------------------------------
# Healthcheck
# ----------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Apply migrations before starting the server
# CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 --log-level info"]
# CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
