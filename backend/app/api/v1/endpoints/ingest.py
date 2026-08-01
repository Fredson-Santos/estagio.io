from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_admin_key
from app.db.database import get_db
from app.db.models import Job, Source
from app.schemas.ingest import (
    ExpireRequest,
    ExpireResponse,
    IngestJobItem,
    IngestRequest,
    IngestResponse,
)
from app.services.dedup import find_existing_urls
from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

router = APIRouter()


def _validate_enums(item: IngestJobItem) -> str | None:
    """Retorna mensagem de erro se area/modality invalidos, senao None."""
    try:
        JobArea(item.area)
    except ValueError:
        return f"area invalida: {item.area}"
    try:
        JobModality(item.modality)
    except ValueError:
        return f"modality invalida: {item.modality}"
    return None


async def _get_or_create_source(
    session: AsyncSession, name: str | None, source_url: str
) -> Source:
    """Cria Source se name fornecido; senao deriva do host da source_url."""
    if not name:
        from urllib.parse import urlparse

        host = urlparse(source_url).netloc or "unknown"
        name = host
    existing = await session.scalar(select(Source).where(Source.name == name))
    if existing:
        return existing
    source = Source(
        name=name,
        type="ingest",
        base_url="",
        status=SourceStatus.ACTIVE,
    )
    session.add(source)
    await session.flush()
    return source


@router.post("/ingest", response_model=IngestResponse, dependencies=[Depends(verify_admin_key)])
async def ingest_jobs(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db),
):
    inserted = 0
    duplicated = 0
    errors: list[str] = []

    urls = [item.source_url for item in request.items]
    existing_urls = await find_existing_urls(db, urls)

    sources_cache: dict[str, Source] = {}

    for idx, item in enumerate(request.items):
        err = _validate_enums(item)
        if err:
            errors.append(f"item[{idx}]: {err}")
            continue

        if item.source_url in existing_urls:
            duplicated += 1
            continue

        source = sources_cache.get(item.source_name or "")
        if source is None:
            source = await _get_or_create_source(db, item.source_name, item.source_url)
            sources_cache[item.source_name or source.name] = source

        job = Job(
            title=item.title,
            company=item.company,
            location=item.location,
            modality=JobModality(item.modality),
            area=JobArea(item.area),
            description=item.description,
            salary=item.salary,
            company_logo=item.company_logo,
            source_url=item.source_url,
            source_id=item.source_id,
            posted_at=item.posted_at,
            source_uuid=source.id,
            status=JobStatus.ACTIVE,
            is_active=True,
            is_featured=False,
            benefits=item.benefits,
            requirements=item.requirements,
            deadline=item.deadline,
            is_pcd=item.is_pcd,
            contract_type=item.contract_type,
            duration_months=item.duration_months,
            salary_min_cents=item.salary_min_cents,
            salary_max_cents=item.salary_max_cents,
        )
        db.add(job)
        try:
            await db.flush()
            existing_urls.add(item.source_url)
            inserted += 1
        except IntegrityError:
            await db.rollback()
            duplicated += 1
            existing_urls.add(item.source_url)

    await db.commit()
    return IngestResponse(inserted=inserted, duplicated=duplicated, errors=errors)


@router.post("/expire", response_model=ExpireResponse, dependencies=[Depends(verify_admin_key)])
async def expire_jobs(
    request: ExpireRequest,
    db: AsyncSession = Depends(get_db),
):
    if not request.expired_urls:
        return ExpireResponse(expired=0)

    result = await db.execute(
        update(Job)
        .where(Job.source_url.in_(request.expired_urls), Job.is_active == True)
        .values(
            is_active=False,
            status=JobStatus.CLOSED,
            closed_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    return ExpireResponse(expired=result.rowcount or 0)
