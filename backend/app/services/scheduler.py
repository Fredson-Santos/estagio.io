"""Scheduler ETL: roda `run_pipeline()` periodicamente via APScheduler AsyncIOScheduler."""
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _etl_job():
    """Wrapper async que roda o pipeline. Import lazy para evitar import circular no startup."""
    from scripts.run_etl import run_pipeline
    try:
        await run_pipeline()
    except Exception:
        logger.exception("Falha ao executar o pipeline ETL agendado")


async def start_scheduler():
    global _scheduler
    interval = settings.ETL_INTERVAL_HOURS
    if not interval or interval <= 0:
        logger.info("ETL automático desabilitado (ETL_INTERVAL_HOURS=%s)", interval)
        return

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _etl_job,
        "interval",
        hours=interval,
        id="etl_pipeline",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("ETL automático agendado: a cada %d hora(s).", interval)


async def shutdown_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("ETL scheduler desligado.")
