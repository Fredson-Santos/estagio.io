"""
run_crawl4ai_test.py — Script de teste REAL para scraping com Crawl4AI gravando em um banco de dados novo.
"""

from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from estagio_shared.db.database import Base
from estagio_shared.db.models import Job, Source, SourceStatus
from estagio_shared.taxonomy import JobStatus
from estagio_shared.services.scrapers.crawl4ai_scraper import run_crawl4ai_scraper, parse_crawl4ai_markdown
from estagio_shared.services.job_validator import validate_job, safe_str
from estagio_shared.services.dedup import is_duplicate

# Banco de dados novo e isolado para o teste
TEST_DB_FILE = "estagio_crawl4ai_test.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///./{TEST_DB_FILE}"


async def init_test_db(engine):
    """Cria a estrutura de tabelas no novo banco de dados."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"[OK] Banco de dados novo configurado com sucesso em: {TEST_DB_FILE}")


async def get_or_create_crawl4ai_source(session) -> Source:
    result = await session.execute(select(Source).where(Source.name == "Crawl4AI"))
    source = result.scalars().first()
    if not source:
        source = Source(
            name="Crawl4AI",
            type="scraper",
            base_url="https://crawl4ai.com",
            status=SourceStatus.ACTIVE
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)
    return source


async def main():
    print("==================================================")
    print(" Iniciando Teste REAL de Scraping Crawl4AI (Novo DB) ")
    print("==================================================")
    
    # 1. Conecta ao novo banco de dados
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    await init_test_db(engine)

    # 2. URLs reais de teste de páginas de vagas de estágio
    test_urls = [
        "https://www.vagas.com.br/vagas-de-estagio",
        "https://www.superestagios.com.br/index/"
    ]

    print(f"\n[BUSCA] Raspando {len(test_urls)} URL(s) em tempo real via Crawl4AI...")
    scraped_jobs = await run_crawl4ai_scraper(test_urls)

    print(f"[DADOS] Total de vagas extraídas em tempo real: {len(scraped_jobs)}")

    if not scraped_jobs:
        print("[WARN] Nenhuma vaga foi extraída da rede. Verifique se o Crawl4AI e os navegadores estão instalados.")
        await engine.dispose()
        return

    # 3. Salva no novo DB
    async with async_session() as session:
        source = await get_or_create_crawl4ai_source(session)
        
        # Cache local para dedup
        res = await session.execute(select(Job))
        existing_jobs = [
            {"title": j.title, "company": j.company, "location": j.location, "source_url": j.source_url}
            for j in res.scalars().all()
        ]

        jobs_added = 0
        for job_data in scraped_jobs:
            is_valid, reason = validate_job(job_data)
            if not is_valid:
                print(f"[AVISO] Vaga inválida '{safe_str(job_data.get('title'))}': {reason}")
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
                    source_id=str(job_data.get("source_id", "")),
                    posted_at=job_data.get("posted_at"),
                    source_uuid=source.id,
                    status=JobStatus.ACTIVE,
                    is_active=True
                )
                session.add(new_job)
                existing_jobs.append(job_data)
                jobs_added += 1

        if jobs_added > 0:
            await session.commit()
            print(f"\n[SALVO] {jobs_added} vaga(s) real(is) salva(s) com sucesso no novo banco de dados '{TEST_DB_FILE}'!")
        else:
            print("\n[INFO] Nenhuma nova vaga inserida (já existente ou filtrada).")

        # 4. Leitura e exibicao dos dados salvos no novo DB
        print("\n--- Conteúdo do Novo DB (Tabela Job) ---")
        all_db_jobs = (await session.execute(select(Job))).scalars().all()
        for idx, job in enumerate(all_db_jobs, 1):
            print(f" [{idx}] ID: {job.id}")
            print(f"     Título: {job.title}")
            print(f"     Empresa: {job.company}")
            print(f"     Modalidade: {job.modality.value if hasattr(job.modality, 'value') else job.modality}")
            print(f"     Área: {job.area.value if hasattr(job.area, 'value') else job.area}")
            print(f"     URL: {job.source_url}")
            print(f"     Descrição (amostra): {job.description[:150]}...\n")

    await engine.dispose()
    print("==================================================")
    print(" Teste REAL concluído com sucesso! ")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
