from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func, text
from typing import Optional
from uuid import UUID

from app.db.database import get_db
from app.db.models import Job, JobClick
from app.schemas.job import JobResponse, PaginatedJobResponse, JobUpdate
from estagio_shared.taxonomy import JobArea, JobModality
from app.core.rate_limit import limiter
from app.core.security import verify_admin_key

router = APIRouter()


@router.get("", response_model=PaginatedJobResponse)
@limiter.limit("60/minute")
async def list_jobs(
    request: Request,
    q: Optional[str] = None,
    area: Optional[JobArea] = None,
    location: Optional[str] = None,
    modality: Optional[JobModality] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    featured: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    query = select(Job).options(joinedload(Job.source)).where(Job.is_active == True)

    if q:
        if db.bind and db.bind.dialect.name == "postgresql":
            # PostgreSQL: use the search_vector GIN index for full-text search
            query = query.where(
                text("jobs.search_vector @@ websearch_to_tsquery('portuguese', unaccent(:q))")
            ).params(q=q)
        else:
            # SQLite / other dialects: fall back to ILIKE on title and company
            from sqlalchemy import or_
            safe_q = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            query = query.where(or_(
                Job.title.ilike(f"%{safe_q}%", escape="\\"),
                Job.company.ilike(f"%{safe_q}%", escape="\\")
            ))
    if modality:
        query = query.where(Job.modality == modality)
    if location:
        safe_loc = location.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        if db.bind and db.bind.dialect.name == "postgresql":
            query = query.where(
                text("unaccent(jobs.location) ILIKE unaccent(:loc)")
            ).params(loc=f"%{safe_loc}%")
        else:
            query = query.where(Job.location.ilike(f"%{safe_loc}%", escape="\\"))

    if featured:
        query = query.where(Job.is_featured == True)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    query = query.order_by(
        Job.posted_at.desc().nulls_last()
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/locations", response_model=list[str])
@limiter.limit("60/minute")
async def list_locations(
    request: Request,
    q: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Retorna lista de cidades distintas das vagas ativas para autocomplete."""
    query = (
        select(Job.location)
        .where(Job.is_active == True, Job.location.isnot(None), Job.location != "")
        .distinct()
    )
    if q:
        safe_q = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        if db.bind and db.bind.dialect.name == "postgresql":
            query = query.where(
                func.unaccent(Job.location).ilike(func.unaccent(f"%{safe_q}%"))
            )
        else:
            query = query.where(Job.location.ilike(f"%{safe_q}%", escape="\\"))
    query = query.order_by(Job.location).limit(limit)
    result = await db.execute(query)
    return [row[0] for row in result.fetchall()]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    job = await db.scalar(select(Job).options(joinedload(Job.source)).where(Job.id == job_id))
    
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
        
    return job

@router.patch("/{job_id}", response_model=JobResponse, dependencies=[Depends(verify_admin_key)])
async def update_job(
    job_id: UUID,
    payload: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    job = await db.scalar(select(Job).options(joinedload(Job.source)).where(Job.id == job_id))

    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    await db.commit()
    await db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_admin_key)])
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    job = await db.scalar(select(Job).where(Job.id == job_id))

    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    job.is_active = False
    await db.commit()


@router.post("/{job_id}/click", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def register_click(
    request: Request,
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    job = await db.scalar(select(Job).where(Job.id == job_id, Job.is_active == True))
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")

    referrer = (request.headers.get("referer") or "")[:255]
    click = JobClick(job_id=job.id, referrer=referrer)
    db.add(click)
    await db.commit()

