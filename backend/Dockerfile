# syntax=docker/dockerfile:1

FROM python:3.12-slim AS runtime

WORKDIR /app/backend

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --home-dir /app app

COPY shared /app/shared
COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --no-cache-dir /app/shared \
    && pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend/ /app/backend/

USER app

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

