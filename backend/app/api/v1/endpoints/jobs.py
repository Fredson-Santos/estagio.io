from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from typing import Optional
from uuid import UUID

from app.db.database import get_db
from app.db.models import Job
from app.schemas.job import JobResponse, PaginatedJobResponse
from app.core.taxonomy import JobArea, JobModality
from app.core.rate_limit import limiter

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
    if area:
        query = query.where(Job.area == area)
    if modality:
        query = query.where(Job.modality == modality)
    if location:
        safe_loc = location.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(Job.location.ilike(f"%{safe_loc}%", escape="\\"))
        
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Get items
    if featured:
        from sqlalchemy import case
        priority_cases = case(
            (Job.title.ilike('%programa%'), 1),
            (Job.company.ilike('%vivo%'), 1),
            (Job.company.ilike('%bradesco%'), 1),
            (Job.company.ilike('%itaú%'), 1),
            (Job.company.ilike('%itau%'), 1),
            (Job.company.ilike('%natura%'), 1),
            (Job.company.ilike('%ambev%'), 1),
            (Job.company.ilike('%vale%'), 1),
            (Job.company.ilike('%globo%'), 1),
            (Job.company.ilike('%google%'), 1),
            (Job.company.ilike('%amazon%'), 1),
            (Job.company.ilike('%microsoft%'), 1),
            (Job.company.ilike('%nubank%'), 1),
            else_=0
        ).desc()
        query = query.order_by(priority_cases, Job.posted_at.desc().nulls_last()).offset(skip).limit(limit)
    else:
        query = query.order_by(Job.posted_at.desc().nulls_last()).offset(skip).limit(limit)
        
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
    result = await db.execute(select(Job).options(joinedload(Job.source)).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
        
    return job
