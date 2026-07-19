import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.future import select
from app.db.database import AsyncSessionLocal
from app.db.models import Job, Source, SourceStatus
from app.services.scrapers.gupy import run_gupy_scraper
from app.services.dedup import is_duplicate
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

async def run_pipeline():
    print("Iniciando pipeline de extração de vagas...")
    
    async with AsyncSessionLocal() as session:
        # Busca a fonte Gupy
        source = await get_or_create_gupy_source(session)
        
        # Busca vagas existentes para dedup (somente ativas para simplificar cache na memória)
        result = await session.execute(select(Job).where(Job.is_active == True))
        existing_jobs = [
            {"title": j.title, "company": j.company, "location": j.location, "source_url": j.source_url}
            for j in result.scalars().all()
        ]
        
        # Busca novas vagas na Gupy
        print("Buscando vagas na Gupy...")
        new_jobs_data = await run_gupy_scraper(limit=20)
        print(f"Foram encontradas {len(new_jobs_data)} vagas na Gupy.")
        
        jobs_added = 0
        for job_data in new_jobs_data:
            if not is_duplicate(job_data, existing_jobs):
                new_job = Job(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    modality=job_data["modality"],
                    area=job_data["area"],
                    description=job_data["description"],
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
                
        if jobs_added > 0:
            await session.commit()
            print(f"Sucesso! {jobs_added} novas vagas salvas no banco de dados.")
        else:
            print("Nenhuma nova vaga encontrada (todas foram deduplicadas).")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
