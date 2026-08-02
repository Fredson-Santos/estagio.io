import logging

from sqlalchemy.future import select
from src.db.database import AsyncSessionLocal
from src.db.models import ScrapedJob, Source
from estagio_shared.taxonomy import SourceStatus
from src.scrapers.gupy import run_gupy_scraper, run_gupy_vagaja_scraper
from src.scrapers.eureca import run_eureca_scraper
from src.scrapers.ciadeestagios import run_ciadeestagios_scraper
from src.scrapers.abler import run_abler_scraper
from src.scrapers.estagios import scrape_secondary_platforms
from src.services.dedup import is_duplicate
from src.services.job_validator import validate_job, safe_str, trunc

logger = logging.getLogger(__name__)


async def get_or_create_source(session, name: str, base_url: str, source_type: str = "json") -> Source:
    """Factory genérico: busca ou cria uma Source pelo nome."""
    result = await session.execute(select(Source).where(Source.name == name))
    source = result.scalars().first()
    if not source:
        source = Source(
            name=name,
            type=source_type,
            base_url=base_url,
            status=SourceStatus.ACTIVE
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)
    return source


async def get_or_create_gupy_source(session) -> Source:
    return await get_or_create_source(session, "Gupy", "https://portal.gupy.io")


async def get_or_create_eureca_source(session) -> Source:
    return await get_or_create_source(session, "Eureca", "https://eureca.me")


async def get_or_create_ciadeestagios_source(session) -> Source:
    return await get_or_create_source(session, "Cia de Estagios", "https://ciadeestagios.com.br")


async def get_or_create_abler_source(session) -> Source:
    return await get_or_create_source(session, "Abler", "https://abler.com.br")


async def _ingest_jobs(
    session,
    jobs_data: list[dict],
    source: Source,
    existing_jobs: list[dict],
    platform_label: str,
) -> int:
    """Pipeline interno: valida, deduplica e cria ScrapedJob no DB."""
    jobs_added = 0
    for job_data in jobs_data:
        is_valid, reason = validate_job(job_data)
        if not is_valid:
            logger.warning(
                "[ETL] Ignorando vaga %s inválida '%s': %s",
                platform_label, safe_str(job_data.get('title')), reason
            )
            continue

        if not is_duplicate(job_data, existing_jobs):
            new_job = ScrapedJob(
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
                source_uuid=source.id,
                synced=False
            )
            session.add(new_job)
            existing_jobs.append(job_data)
            jobs_added += 1
    return jobs_added


async def run_pipeline():
    """Pipeline orquestrado:

    Sequência (mirror do pipeline.py do scraper-api):
      1. Cia de Estágios
      2. Eureca (com fetch de detalhes)
      3. Gupy Jobs (com enriquecimento HTML)
      4. Gupy Vaga-Já
      5. Abler (2-tier: token oficial + fallback cookie)
      6. Plataformas secundárias (Vagas.com.br + SuperEstagios via LLM/CSS)
      7. LLM Area Matching (pós-pipeline, se AREA_MATCHER_MODE=llm)
    """
    logger.info("Iniciando pipeline de extração de vagas...")
    totals: dict[str, int] = {}

    async with AsyncSessionLocal() as session:
        source_gupy = await get_or_create_gupy_source(session)
        source_eureca = await get_or_create_eureca_source(session)
        source_cia = await get_or_create_ciadeestagios_source(session)
        source_abler = await get_or_create_abler_source(session)

        result = await session.execute(select(ScrapedJob))
        existing_jobs = [
            {"title": j.title, "company": j.company, "location": j.location, "source_url": j.source_url}
            for j in result.scalars().all()
        ]

        # 1. Cia de Estágios
        logger.info("Buscando vagas na Cia de Estágios...")
        cia_jobs = await run_ciadeestagios_scraper()
        logger.info("Encontradas %d vagas válidas na Cia de Estágios.", len(cia_jobs))
        totals["Cia de Estágios"] = await _ingest_jobs(
            session, cia_jobs, source_cia, existing_jobs, "Cia de Estágios"
        )

        # 2. Eureca
        logger.info("Buscando vagas na Eureca...")
        eureca_jobs = await run_eureca_scraper(limit=2000)
        logger.info("Encontradas %d vagas válidas na Eureca.", len(eureca_jobs))
        totals["Eureca"] = await _ingest_jobs(
            session, eureca_jobs, source_eureca, existing_jobs, "Eureca"
        )

        # 3. Gupy
        logger.info("Buscando vagas na Gupy...")
        gupy_jobs = await run_gupy_scraper(limit=2000)
        logger.info("Encontradas %d vagas válidas na Gupy.", len(gupy_jobs))
        totals["Gupy"] = await _ingest_jobs(
            session, gupy_jobs, source_gupy, existing_jobs, "Gupy"
        )

        # 4. Gupy Vaga-Já
        logger.info("Buscando vagas no Gupy Vaga-Já...")
        vagaja_jobs = await run_gupy_vagaja_scraper(limit=500)
        logger.info("Encontradas %d vagas válidas no Gupy Vaga-Já.", len(vagaja_jobs))
        totals["Gupy Vaga-Já"] = await _ingest_jobs(
            session, vagaja_jobs, source_gupy, existing_jobs, "Gupy Vaga-Já"
        )

        # 5. Abler
        logger.info("Buscando vagas na Abler...")
        abler_jobs = await run_abler_scraper()
        logger.info("Encontradas %d vagas válidas na Abler.", len(abler_jobs))
        totals["Abler"] = await _ingest_jobs(
            session, abler_jobs, source_abler, existing_jobs, "Abler"
        )

        # 6. Plataformas secundárias (Vagas.com.br + SuperEstagios)
        logger.info("Buscando vagas em plataformas secundárias...")
        sec_results = await scrape_secondary_platforms()

        for platform_name, sec_jobs in sec_results.items():
            if not sec_jobs:
                continue
            logger.info("Encontradas %d vagas na plataforma %s.", len(sec_jobs), platform_name)
            p_source = await get_or_create_source(
                session,
                platform_name,
                f"https://{platform_name.lower().replace(' ', '')}",
                source_type="scraper"
            )
            totals[platform_name] = await _ingest_jobs(
                session, sec_jobs, p_source, existing_jobs, platform_name
            )

        if any(totals.values()):
            await session.commit()
            total_added = sum(totals.values())
            logger.info("Sucesso! %d novas vagas salvas no banco de dados.", total_added)
        else:
            logger.info("Nenhuma nova vaga encontrada (todas foram deduplicadas ou filtradas).")

        logger.info("Resumo: %s", totals)

    # 7. LLM Area Matching (pós-pipeline, se configurado)
    from src.config import settings
    if settings.AREA_MATCHER_MODE.lower() == "llm":
        logger.info("Executando classificação de áreas via LLM (pós-pipeline)...")
        try:
            from src.services.matcher import process_db_area_matching
            matched = await process_db_area_matching()
            totals["LLM Matched"] = matched
            logger.info("LLM area matching: %d vagas reclassificadas.", matched)
        except Exception:
            logger.exception("Falha ao executar LLM area matching")
    else:
        logger.debug("Area matcher desativado (AREA_MATCHER_MODE != 'llm').")

    return totals
