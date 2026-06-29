# ── Stage 1: Build dependencies ───────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# System deps for Pillow and general Python package builds. No PostgreSQL deps are
# installed because the MVP uses SQLite only.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


# ── Stage 2: Runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.development \
    SQLITE_DATABASE_PATH=/app/data/db.sqlite3 \
    PORT=8000

# Runtime-only system deps for Pillow. No Redis/PostgreSQL/Celery runtime service
# is required by the SQLite presentation MVP.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN groupadd -r medequip && useradd -r -g medequip -d /app -s /sbin/nologin medequip

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy project source
COPY --chown=medequip:medequip . .

# Create persistent SQLite, media, and static dirs
RUN mkdir -p /app/data /app/staticfiles /app/media && \
    chown -R medequip:medequip /app/data /app/staticfiles /app/media

USER medequip

# Collect static files at build time
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Simple MVP runtime. docker-compose.yml runs migrations before this command.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
