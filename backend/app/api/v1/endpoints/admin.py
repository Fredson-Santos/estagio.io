from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import Job, Source
from app.schemas.admin import AdminStats, ScraperRunResponse
from app.core.security import verify_admin_key

router = APIRouter(dependencies=[Depends(verify_admin_key)])


@router.get("/stats", response_model=AdminStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_jobs = await db.scalar(select(func.count()).select_from(Job)) or 0
    active_jobs = await db.scalar(select(func.count()).select_from(Job).where(Job.is_active == True)) or 0
    featured_jobs = await db.scalar(select(func.count()).select_from(Job).where(Job.is_featured == True)) or 0
    sources = await db.scalar(select(func.count()).select_from(Source)) or 0
    last_scraped_at = await db.scalar(select(func.max(Job.scraped_at)))

    return AdminStats(
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        featured_jobs=featured_jobs,
        sources=sources,
        last_scraped_at=last_scraped_at,
    )


@router.post("/scrapers/run", response_model=ScraperRunResponse, status_code=202)
async def run_scrapers(background_tasks: BackgroundTasks):
    from estagio_shared.services.etl import run_pipeline
    background_tasks.add_task(run_pipeline)
    return ScraperRunResponse(message="Pipeline de scrapers disparado", status="triggered")
