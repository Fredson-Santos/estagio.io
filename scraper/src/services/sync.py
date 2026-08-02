import logging
from urllib.parse import urlparse
import httpx
from sqlalchemy.future import select
from src.db.database import AsyncSessionLocal
from src.db.models import ScrapedJob

logger = logging.getLogger(__name__)


async def sync_to_backend(backend_url: str, api_key: str, batch_size: int = 100) -> dict:
    """Envia todas as vagas com synced=False em lotes para POST /api/v1/ingest no backend."""
    total_inserted = 0
    total_duplicated = 0
    errors: list[str] = []

    headers = {"X-Admin-Key": api_key}
    url = f"{backend_url.rstrip('/')}/api/v1/ingest"

    while True:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ScrapedJob).where(ScrapedJob.synced == False).limit(batch_size)
            )
            jobs = result.scalars().all()
            if not jobs:
                break

            items = []
            for j in jobs:
                items.append({
                    "title": j.title,
                    "company": j.company,
                    "location": j.location,
                    "modality": j.modality.value if hasattr(j.modality, "value") else str(j.modality),
                    "area": j.area.value if hasattr(j.area, "value") else str(j.area),
                    "description": j.description,
                    "salary": j.salary,
                    "salary_min_cents": j.salary_min_cents,
                    "salary_max_cents": j.salary_max_cents,
                    "company_logo": j.company_logo,
                    "source_url": j.source_url,
                    "source_id": j.source_id,
                    "posted_at": j.posted_at.isoformat() if j.posted_at else None,
                    "benefits": j.benefits,
                    "requirements": j.requirements,
                    "deadline": j.deadline.isoformat() if j.deadline else None,
                    "is_pcd": j.is_pcd,
                    "contract_type": j.contract_type,
                    "duration_months": j.duration_months,
                })

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json={"items": items}, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()

                    for j in jobs:
                        j.synced = True
                    await session.commit()

                    total_inserted += data.get("inserted", 0)
                    total_duplicated += data.get("duplicated", 0)
                    if data.get("errors"):
                        errors.extend(data["errors"])
                    logger.info("sync_to_backend: lote de %d vagas sincronizado (inseridos: %d).", len(jobs), data.get("inserted", 0))
            except httpx.HTTPError as exc:
                logger.error("sync_to_backend falhou ao conectar ao backend: %s", exc)
                errors.append(str(exc))
                break

    return {"inserted": total_inserted, "duplicated": total_duplicated, "errors": errors}



async def sync_expirations(backend_url: str, api_key: str, expired_urls: list[str]) -> dict:
    """Envia URLs de vagas expiradas para POST /api/v1/expire no backend."""
    if not expired_urls:
        return {"expired": 0}

    headers = {"X-Admin-Key": api_key}
    url = f"{backend_url.rstrip('/')}/api/v1/expire"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json={"expired_urls": expired_urls}, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            logger.info("sync_expirations: %d vagas expiradas no backend.", data.get("expired", 0))
            return data
    except httpx.HTTPError as exc:
        logger.error("sync_expirations falhou ao enviar expiradas: %s", exc)
        return {"expired": 0, "error": str(exc)}
