# syntax=docker/dockerfile:1

# ---- Stage 1: builder ----
FROM python:3.12-slim AS builder
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY shared /shared
COPY scraper/requirements.txt scraper/

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --prefix=/install --no-cache-dir -r scraper/requirements.txt

RUN playwright install --with-deps chromium

# ---- Stage 2: runtime ----
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --home-dir /app app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder /root/.cache/ms-playwright /home/app/.cache/ms-playwright

COPY scraper/ scraper/
COPY shared/ shared/

RUN pip install --no-deps -e /shared

USER app

ENV RULES_FILE=/app/data/scraper_rules.json

HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

CMD ["python", "scraper/main.py"]