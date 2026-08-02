"""Script para limpar os bancos de dados (Backend SQLite e Scraper SQLite),
executar as migrações do Alembic, rodar o pipeline de scraping e sincronizar
as vagas para a base do Backend.
"""
import asyncio
import os
import sys
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
SCRAPER_DIR = ROOT_DIR / "scraper"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(SCRAPER_DIR))
sys.path.insert(0, str(ROOT_DIR / "shared"))


def clean_databases():
    print("[+] Cleaning database files...")
    db_files = [
        BACKEND_DIR / "estagio.db",
        BACKEND_DIR / "estagio.db-wal",
        BACKEND_DIR / "estagio.db-shm",
        BACKEND_DIR / "backend.db",
        SCRAPER_DIR / "scraper.db",
        SCRAPER_DIR / "scraper.db-wal",
        SCRAPER_DIR / "scraper.db-shm",
    ]
    cleaned = 0
    for db_file in db_files:
        if db_file.exists():
            try:
                db_file.unlink()
                print(f"   - Removed {db_file.name}")
                cleaned += 1
            except Exception as e:
                print(f"   - Failed to remove {db_file.name}: {e}")
    if cleaned == 0:
        print("   - No previous database files found.")


async def run_pipeline_and_sync():
    print("\n[+] Initializing Scraper DB and running ETL pipeline...")
    os.environ["SCRAPER_DB_PATH"] = str(SCRAPER_DIR / "scraper.db")
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{BACKEND_DIR / 'estagio.db'}"

    # Imports after env set
    from src.main import init_db
    from src.services.etl import run_pipeline
    from src.db.database import AsyncSessionLocal as ScraperSession
    from src.db.models import ScrapedJob
    from app.db.database import AsyncSessionLocal as BackendSession
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus
    from sqlalchemy.future import select

    # Init scraper tables
    await init_db()

    # Run ETL scrapers
    await run_pipeline()

    # Query scraped jobs from scraper DB
    async with ScraperSession() as session:
        res = await session.execute(select(ScrapedJob))
        scraped_jobs = res.scalars().all()
        print(f"\n[+] Total jobs scraped: {len(scraped_jobs)}")

        if not scraped_jobs:
            print("[!] No jobs scraped during pipeline execution.")
            return

        # Ingest directly into Backend DB
        print("[+] Ingesting scraped jobs into Backend DB...")
        async with BackendSession() as backend_session:
            inserted = 0
            sources_cache = {}
            for j in scraped_jobs:
                from urllib.parse import urlparse
                source_name = urlparse(j.source_url).netloc or "Scraper"
                if source_name not in sources_cache:
                    existing_source = await backend_session.scalar(
                        select(Source).where(Source.name == source_name)
                    )
                    if not existing_source:
                        existing_source = Source(
                            name=source_name,
                            type="scraper",
                            base_url=j.source_url,
                            status=SourceStatus.ACTIVE,
                        )
                        backend_session.add(existing_source)
                        await backend_session.flush()
                    sources_cache[source_name] = existing_source

                src = sources_cache[source_name]

                # Check duplicate
                dup = await backend_session.scalar(
                    select(Job).where(Job.source_url == j.source_url)
                )
                if dup:
                    continue

                modality = j.modality if isinstance(j.modality, JobModality) else JobModality(j.modality)
                area = j.area if isinstance(j.area, JobArea) else JobArea(j.area)

                new_job = Job(
                    title=j.title,
                    company=j.company,
                    location=j.location,
                    modality=modality,
                    area=area,
                    description=j.description,
                    salary=j.salary,
                    salary_min_cents=j.salary_min_cents,
                    salary_max_cents=j.salary_max_cents,
                    company_logo=j.company_logo,
                    source_url=j.source_url,
                    source_id=j.source_id,
                    posted_at=j.posted_at,
                    status=JobStatus.ACTIVE,
                    source_uuid=src.id,
                )
                backend_session.add(new_job)
                j.synced = True
                inserted += 1

            await backend_session.commit()
            await session.commit()
            print(f"[+] Successful ingestion: {inserted} jobs stored in backend DB.")


def main():
    clean_databases()

    print("\n[+] Running Alembic migrations for Backend DB...")
    import subprocess

    res = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(BACKEND_DIR),
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(f"[!] Alembic migration failed:\n{res.stderr}")
        sys.exit(1)
    print("[+] Backend schema created successfully via Alembic.")

    asyncio.run(run_pipeline_and_sync())


if __name__ == "__main__":
    main()
