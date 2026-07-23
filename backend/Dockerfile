# syntax=docker/dockerfile:1

# ---- Stage 1: builder ----
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY shared /shared
COPY backend/requirements.txt backend/

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --prefix=/install --no-cache-dir -r backend/requirements.txt

# ---- Stage 2: runtime ----
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --home-dir /app app

WORKDIR /app

COPY --from=builder /install /usr/local

COPY backend/ backend/
COPY shared/ shared/

RUN pip install --no-deps -e /shared

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "python backend/scripts/wait_for_db.py && alembic upgrade head && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]