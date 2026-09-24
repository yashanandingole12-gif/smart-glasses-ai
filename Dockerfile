# ==============================================================================
# EVA Smart Glasses AI Assistant — Production Dockerfile
# Optimized for Local Docker, AWS EC2 (t4g/c7g Graviton & x86_64), and VPS Deployments
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build Dependencies
# ------------------------------------------------------------------------------
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into a clean virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Final Runtime Stage (Slim & Secure)
# ------------------------------------------------------------------------------
FROM python:3.11-slim as runner

WORKDIR /app

# Install runtime libraries for OpenCV, audio codecs, SQLite, and SSL certs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    sqlite3 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Production Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    HOST=0.0.0.0 \
    PORT=8001 \
    PYTHONPATH=/app

# Copy application source code
COPY backend/ /app/backend/
COPY Caddyfile /app/Caddyfile

# Create persistent data, uploads, and logs directories
RUN mkdir -p /app/data /app/storage/uploads /app/logs && \
    chmod -R 777 /app/data /app/storage /app/logs

EXPOSE 8001

# Healthcheck targeting the live health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8001/api/v1/health || exit 1

# Production startup with proxy headers and uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
