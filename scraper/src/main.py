"""Entrypoint do serviço scraper.

- Executa o pipeline ETL imediatamente e agendado via APScheduler.
- Expõe endpoints /health e /run (POST autenticado) na porta 9090.
- Executa limpeza periódica de registros antigos e verificação de expiração.
"""
import asyncio
from datetime import datetime, timedelta, timezone
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Header, HTTPException, status
from sqlalchemy import delete
from sqlalchemy.future import select
import uvicorn

from src.config import settings
from src.db.database import AsyncSessionLocal, engine, Base
from src.db.models import ScrapedJob
from src.services.etl import run_pipeline
from src.services.sync import sync_to_backend, sync_expirations
from src.services.health_check import check_expired_urls

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("scraper")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _etl_job():
    try:
        await run_pipeline()
        await sync_to_backend(settings.BACKEND_URL, settings.BACKEND_API_KEY)
    except Exception:
        logger.exception("Falha ao executar o pipeline ETL agendado/disparado")


async def _cleanup_job():
    """Deleta vagas sincronizadas há mais de 30 dias."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    try:
        async with AsyncSessionLocal() as session:
            stmt = delete(ScrapedJob).where(
                ScrapedJob.synced == True,
                ScrapedJob.scraped_at < cutoff
            )
            result = await session.execute(stmt)
            await session.commit()
            logger.info("Cleanup: %d vagas sincronizadas antigas foram removidas.", result.rowcount)
    except Exception:
        logger.exception("Falha ao executar o cleanup_job")


async def _check_expired_job():
    """Checa a validade das vagas sincronizadas e envia as expiradas para o backend."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ScrapedJob.source_url).where(ScrapedJob.synced == True)
            )
            urls = result.scalars().all()
            if not urls:
                return

            expired = await check_expired_urls(urls)
            if expired:
                await sync_expirations(settings.BACKEND_URL, settings.BACKEND_API_KEY, expired)
    except Exception:
        logger.exception("Falha ao executar o check_expired_job")


def create_app() -> FastAPI:
    app = FastAPI(title="estagio.io Scraper API")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/run", status_code=status.HTTP_202_ACCEPTED)
    async def run(x_admin_key: str | None = Header(None, alias="X-Admin-Key")):
        expected_key = settings.BACKEND_API_KEY
        if expected_key and x_admin_key != expected_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autorizado")

        asyncio.create_task(_etl_job())
        return {"message": "Pipeline de scrapers disparado", "status": "triggered"}

    return app


async def _run_health_server():
    app = create_app()
    config = uvicorn.Config(app, host="0.0.0.0", port=9090, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await init_db()
    interval = settings.ETL_INTERVAL_HOURS

    scheduler = AsyncIOScheduler()
    if interval and interval > 0:
        scheduler.add_job(
            _etl_job,
            "interval",
            hours=interval,
            id="etl_pipeline",
            max_instances=1,
            coalesce=True,
        )
        scheduler.add_job(
            _cleanup_job,
            "cron",
            hour=3,
            minute=0,
            id="cleanup_job",
            max_instances=1,
            coalesce=True,
        )
        scheduler.add_job(
            _check_expired_job,
            "cron",
            hour=3,
            minute=30,
            id="check_expired_job",
            max_instances=1,
            coalesce=True,
        )
        scheduler.start()
        logger.info("Scraper agendado (ETL: a cada %dh, Cleanup: 03:00 UTC, Expired: 03:30 UTC).", interval)

    # Primeira execução imediata
    logger.info("Executando primeiro pipeline ETL...")
    await _etl_job()

    health_task = asyncio.create_task(_run_health_server())
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        scheduler.shutdown(wait=False)
        health_task.cancel()
        logger.info("Scraper encerrado.")


if __name__ == "__main__":
    asyncio.run(main())
