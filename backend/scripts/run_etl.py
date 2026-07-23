import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.future import select
from app.db.database import AsyncSessionLocal
from app.db.models import Job, Source, SourceStatus
from app.services.scrapers.gupy import run_gupy_scraper
from app.services.scrapers.eureca import run_eureca_scraper
from app.services.scrapers.estagios import scrape_secondary_platforms
from app.services.dedup import is_duplicate
from app.services.job_validator import validate_job, safe_str, trunc
from app.core.taxonomy import JobStatus

logger = logging.getLogger(__name__)


async def get_or_create_gupy_source(session) -> Source:
    result = await session.execute(select(Source).where(Source.name == "Gupy"))
    source = result.scalars().first()
    if not source:
        source = Source(
            name="Gupy",
            type="json",
            base_url="https://portal.gupy.io",
            status=SourceStatus.ACTIVE
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)
    return source


async def get_or_create_eureca_source(session) -> Source:
    result = await session.execute(select(Source).where(Source.name == "Eureca"))
    source = result.scalars().first()
    if not source:
        source = Source(
            name="Eureca",
            type="json",
            base_url="https://eureca.me",
            status=SourceStatus.ACTIVE
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)
    return source


async def run_pipeline():
    logger.info("Iniciando pipeline de extração de vagas...")

    async with AsyncSessionLocal() as session:
        # Busca a fonte Gupy e Eureca
        source = await get_or_create_gupy_source(session)
        source_eureca = await get_or_create_eureca_source(session)

        # Busca vagas existentes para dedup (somente ativas para simplificar cache na memória)
        result = await session.execute(select(Job).where(Job.is_active == True))
        existing_jobs = [
            {"title": j.title, "company": j.company, "location": j.location, "source_url": j.source_url}
            for j in result.scalars().all()
        ]

        # Busca vagas na Gupy
        logger.info("Buscando vagas na Gupy...")
        new_jobs_data = await run_gupy_scraper(limit=2000)
        logger.info("Encontradas %d vagas válidas na Gupy.", len(new_jobs_data))

        jobs_added = 0

        # Processa vagas Gupy
        for job_data in new_jobs_data:
            is_valid, reason = validate_job(job_data)
            if not is_valid:
                logger.warning("[ETL] Ignorando vaga Gupy inválida '%s': %s", safe_str(job_data.get('title')), reason)
                continue

            if not is_duplicate(job_data, existing_jobs):
                new_job = Job(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    modality=job_data["modality"],
                    area=job_data["area"],
                    description=job_data["description"],
                    salary=job_data.get("salary"),
                    company_logo=job_data.get("company_logo"),
                    source_url=job_data["source_url"],
                    source_id=job_data["source_id"],
                    posted_at=job_data["posted_at"],
                    source_uuid=source.id,
                    status=JobStatus.ACTIVE,
                    is_active=True
                )
                session.add(new_job)
                existing_jobs.append(job_data)  # Atualiza o cache local
                jobs_added += 1

        # Busca vagas na Eureca
        logger.info("Buscando vagas na Eureca...")
        eureca_jobs_data = await run_eureca_scraper(limit=2000)
        logger.info("Encontradas %d vagas válidas na Eureca.", len(eureca_jobs_data))

        # Processa vagas Eureca
        for job_data in eureca_jobs_data:
            is_valid, reason = validate_job(job_data)
            if not is_valid:
                logger.warning("[ETL] Ignorando vaga Eureca inválida '%s': %s", safe_str(job_data.get('title')), reason)
                continue

            if not is_duplicate(job_data, existing_jobs):
                new_job = Job(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    modality=job_data["modality"],
                    area=job_data["area"],
                    description=job_data["description"],
                    salary=job_data.get("salary"),
                    company_logo=job_data.get("company_logo"),
                    source_url=job_data["source_url"],
                    source_id=job_data["source_id"],
                    posted_at=job_data["posted_at"],
                    source_uuid=source_eureca.id,
                    status=JobStatus.ACTIVE,
                    is_active=True
                )
                session.add(new_job)
                existing_jobs.append(job_data)  # Atualiza o cache local
                jobs_added += 1

        logger.info("Buscando vagas em plataformas secundárias...")
        sec_results = await scrape_secondary_platforms()

        for platform_name, sec_jobs in sec_results.items():
            if not sec_jobs:
                continue

            logger.info("Encontradas %d vagas na plataforma %s.", len(sec_jobs), platform_name)
            # Garante que a Source existe
            source_q = await session.execute(select(Source).where(Source.name == platform_name))
            p_source = source_q.scalars().first()
            if not p_source:
                p_source = Source(name=platform_name, type="scraper", base_url=f"https://{platform_name.lower().replace(' ', '')}", status=SourceStatus.ACTIVE)
                session.add(p_source)
                await session.flush()

            for job_data in sec_jobs:
                is_valid, reason = validate_job(job_data)
                if not is_valid:
                    logger.warning("[ETL] Ignorando vaga %s inválida '%s': %s", platform_name, safe_str(job_data.get('title')), reason)
                    continue

                if not is_duplicate(job_data, existing_jobs):
                    new_job = Job(
                        title=trunc(job_data["title"], 255),
                        company=trunc(job_data["company"], 255),
                        location=trunc(job_data["location"], 255),
                        modality=job_data["modality"],
                        area=job_data["area"],
                        description=job_data["description"],
                        salary=trunc(job_data.get("salary"), 255),
                        company_logo=trunc(job_data.get("company_logo"), 1000),
                        source_url=trunc(job_data["source_url"], 1000),
                        source_id=trunc(job_data.get("source_id", ""), 255),
                        posted_at=job_data.get("posted_at"),
                        source_uuid=p_source.id,
                        status=JobStatus.ACTIVE,
                        is_active=True
                    )
                    session.add(new_job)
                    existing_jobs.append(job_data)
                    jobs_added += 1

        if jobs_added > 0:
            await session.commit()
            logger.info("Sucesso! %d novas vagas salvas no banco de dados.", jobs_added)
        else:
            logger.info("Nenhuma nova vaga encontrada (todas foram deduplicadas ou filtradas).")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    asyncio.run(run_pipeline())
