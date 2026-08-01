import logging
from urllib.parse import urlparse
import httpx
from sqlalchemy.future import select
from src.db.database import AsyncSessionLocal
from src.db.models import ScrapedJob

logger = logging.getLogger(__name__)


async def sync_to_backend(backend_url: str, api_key: str, batch_size: int = 100) -> dict:
    """Envia vagas com synced=False em lotes para POST /api/v1/ingest no backend."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ScrapedJob).where(ScrapedJob.synced == False).limit(batch_size)
        )
        jobs = result.scalars().all()
        if not jobs:
            return {"inserted": 0, "duplicated": 0, "errors": []}

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

        headers = {"X-Admin-Key": api_key}
        url = f"{backend_url.rstrip('/')}/api/v1/ingest"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json={"items": items}, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                for j in jobs:
                    j.synced = True
                await session.commit()
                logger.info("sync_to_backend: %d vagas sincronizadas com sucesso.", len(jobs))
                return data
        except httpx.HTTPError as exc:
            logger.error("sync_to_backend falhou ao conectar ao backend: %s", exc)
            return {"inserted": 0, "duplicated": 0, "errors": [str(exc)]}


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
