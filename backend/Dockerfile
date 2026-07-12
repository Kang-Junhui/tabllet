# syntax=docker/dockerfile:1

# --- Builder: resolve and install dependencies with uv ---
FROM python:3.13-slim AS builder

# uv binary from the official image (pinned tag for reproducibility).
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install only dependencies first so this layer is cached across code changes.
COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

# --- Runtime ---
FROM python:3.13-slim AS runtime

# libpq is required by psycopg at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

# Run as a non-root user.
RUN useradd --create-home --uid 1000 app

# Bring in the virtualenv built in the builder stage, then the app source.
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app . /app

USER app

EXPOSE 8000

# Production default; overridden by compose.dev.yml for development.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
