# syntax=docker/dockerfile:1
# -----------------------------------------------------------------------------
# LARA Smart Glasses AI Assistant — Production Dockerfile
# Optimized for high-speed edge reasoning, multimodal vision, and BLE bridge
# -----------------------------------------------------------------------------

FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DOCKER_CONTAINER=true \
    HOST=0.0.0.0 \
    PORT=8001

WORKDIR /app

# Install system dependencies (curl for healthchecks, ffmpeg/libs for audio processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    libasound2-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend application source and scripts
COPY backend/ /app/backend/
COPY lara_research.py /app/lara_research.py
COPY scripts/ /app/scripts/

# Create runtime directories for storage, logs, and database
RUN mkdir -p /app/storage /app/captures /app/scratch

# Expose backend REST & WebSocket port
EXPOSE 8001

# Container healthcheck against the LARA health probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/api/v1/health || exit 1

# Production entrypoint
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
