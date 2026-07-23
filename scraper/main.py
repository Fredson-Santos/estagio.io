"""Entrypoint do servico scraper.

- Executa o pipeline ETL imediatamente e agendado via APScheduler.
- Expoe um endpoint /health na porta 9090 para Docker/Dokploy healthcheck.
"""
import asyncio
import logging
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from estagio_shared.config import settings
from src.run_etl import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("scraper")


async def _etl_job():
    try:
        await run_pipeline()
    except Exception:
        logger.exception("Falha ao executar o pipeline ETL agendado")


async def _run_health_server():
    from fastapi import FastAPI
    import uvicorn

    health_app = FastAPI()

    @health_app.get("/health")
    def health():
        return {"status": "ok"}

    config = uvicorn.Config(health_app, host="0.0.0.0", port=9090, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
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
        scheduler.start()
        logger.info("Scraper agendado a cada %d hora(s).", interval)

    # Primeira execucao imediata
    logger.info("Executando primeiro pipeline ETL...")
    await _etl_job()

    # Health check server + keep alive
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