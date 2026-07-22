import asyncio
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
from app.services.job_validator import validate_job, safe_str
from app.core.taxonomy import JobStatus

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
    print("Iniciando pipeline de extração de vagas...")
    
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
        print("Buscando vagas na Gupy...")
        new_jobs_data = await run_gupy_scraper(limit=2000)
        print(f"Foram encontradas {len(new_jobs_data)} vagas válidas na Gupy.")
        
        jobs_added = 0
        
        # Processa vagas Gupy
        for job_data in new_jobs_data:
            is_valid, reason = validate_job(job_data)
            if not is_valid:
                print(f"[ETL] Ignorando vaga Gupy inválida '{safe_str(job_data.get('title'))}': {reason}")
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
                existing_jobs.append(job_data) # Atualiza o cache local
                jobs_added += 1

        # Busca vagas na Eureca
        print("Buscando vagas na Eureca...")
        eureca_jobs_data = await run_eureca_scraper(limit=2000)
        print(f"Foram encontradas {len(eureca_jobs_data)} vagas válidas na Eureca.")
        
        # Processa vagas Eureca
        for job_data in eureca_jobs_data:
            is_valid, reason = validate_job(job_data)
            if not is_valid:
                print(f"[ETL] Ignorando vaga Eureca inválida '{safe_str(job_data.get('title'))}': {reason}")
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
                existing_jobs.append(job_data) # Atualiza o cache local
                jobs_added += 1

        print("Buscando vagas em plataformas secundárias...")
        sec_results = await scrape_secondary_platforms()
        
        for platform_name, sec_jobs in sec_results.items():
            if not sec_jobs:
                continue
            
            print(f"Foram encontradas {len(sec_jobs)} vagas na plataforma {platform_name}.")
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
                    print(f"[ETL] Ignorando vaga {platform_name} inválida '{safe_str(job_data.get('title'))}': {reason}")
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
                        source_id=job_data.get("source_id", ""),
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
            print(f"Sucesso! {jobs_added} novas vagas salvas no banco de dados.")
        else:
            print("Nenhuma nova vaga encontrada (todas foram deduplicadas ou filtradas).")

if __name__ == "__main__":
    asyncio.run(run_pipeline())

