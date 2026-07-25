# syntax=docker/dockerfile:1

# ---- Stage 1: builder ----
FROM node:22-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ ./

RUN npm run build

# ---- Stage 2: runtime ----
FROM node:22-alpine AS runtime

RUN addgroup --system app && adduser --system --ingroup app --home /app app

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

USER app

EXPOSE 4321

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:4321/').then(r => r.ok ? process.exit(0) : process.exit(1)).catch(() => process.exit(1))"


CMD ["node", "./dist/server/entry.mjs"]