FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para compilar dependências, se houver
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python scripts/wait_for_db.py && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
