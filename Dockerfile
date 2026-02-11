# Builder
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml .

# Install dependencies (ignoring local project code for cache efficiency)
RUN pip install .

# Runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT="production"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -u 1000 chainlituser
USER chainlituser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=chainlituser:chainlituser /opt/venv /opt/venv

# Copy application code
COPY --chown=chainlituser:chainlituser . .

# Ensure data directory exists for SQLite
RUN mkdir -p /app/data

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/ || exit 1

CMD ["chainlit", "run", "guiollama/ui/app.py", "--host", "0.0.0.0", "--port", "8000"]
