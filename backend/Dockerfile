# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────
# Stage 1 – Build dependencies
# ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system-level build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies into a virtual environment
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────
# Stage 2 – Runtime image
# ─────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="AI Resume Reviewer <support@example.com>"
LABEL description="AI Resume Reviewer FastAPI Backend"
LABEL version="1.0.0"

WORKDIR /app

# Install minimal runtime system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --no-create-home appuser

# Copy virtual environment from builder stage
COPY --from=builder /venv /venv

# Copy application source code
COPY --chown=appuser:appgroup . .

# Make the venv binaries available on PATH
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Health check for Render / Docker health monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Apply migrations before starting the server
CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 --log-level info"]
