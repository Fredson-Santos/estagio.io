import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import case, func

from app.core.config import settings
from app.db.database import get_db
from app.db.models import Job, Source
from app.schemas.admin import AdminStats, ScraperRunResponse
from app.core.security import verify_admin_key

router = APIRouter(dependencies=[Depends(verify_admin_key)])


@router.get("/stats", response_model=AdminStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    job_stats = await db.execute(
        select(
            func.count(Job.id).label("total"),
            func.count(case((Job.is_active.is_(True), Job.id))).label("active"),
            func.count(case((Job.is_featured.is_(True), Job.id))).label("featured"),
            func.max(Job.scraped_at).label("last_scraped"),
        )
    )
    row = job_stats.one()
    sources = await db.scalar(select(func.count()).select_from(Source)) or 0

    return AdminStats(
        total_jobs=row.total or 0,
        active_jobs=row.active or 0,
        featured_jobs=row.featured or 0,
        sources=sources,
        last_scraped_at=row.last_scraped,
    )


@router.post("/scrapers/run", response_model=ScraperRunResponse, status_code=202)
async def run_scrapers():
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.post(
                f"{settings.SCRAPER_URL}/run",
                headers={"X-Admin-Key": settings.ADMIN_API_KEY or ""},
            )
            resp.raise_for_status()
        except httpx.HTTPError:
            raise HTTPException(status_code=502, detail="Scraper indisponível")
    return ScraperRunResponse(message="Pipeline de scrapers disparado", status="triggered")

