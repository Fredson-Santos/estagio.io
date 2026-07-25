from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from typing import Optional
from uuid import UUID

from estagio_shared.db.database import get_db
from estagio_shared.db.models import Job
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
        from sqlalchemy import or_
        # Sanitiza wildcards do LIKE para evitar queries abusivas
        safe_q = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(or_(
            Job.title.ilike(f"%{safe_q}%", escape="\\"),
            Job.company.ilike(f"%{safe_q}%", escape="\\")
        ))
    if modality:
        query = query.where(Job.modality == modality)
    if location:
        safe_loc = location.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(Job.location.ilike(f"%{safe_loc}%", escape="\\"))
    if featured:
        query = query.where(Job.is_featured == True)
        
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Get items
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
