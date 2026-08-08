import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import case, func, text
from typing import Optional
from uuid import UUID

from app.db.database import get_db
from app.db.models import Job, JobClick, Source
from app.schemas.job import JobResponse, PaginatedJobResponse, JobUpdate
from app.schemas.platform import PlatformResponse
from estagio_shared.taxonomy import JobArea, JobModality
from app.core.rate_limit import limiter
from app.core.security import verify_admin_key

router = APIRouter()


# --- Normalização de plataformas -------------------------------------------
# O campo Source.name no banco possui mais de 600 entradas individuais devido
# aos subdomínios (ex: bmw.gupy.io, bauducco.gupy.io). Este dicionário e a
# função de fallback agrupam essas entradas em plataformas amigáveis.

_PLATFORM_KNOWN: list[tuple[str, str, str]] = [
    # (substring case-insensitive encontrada em Source.name, slug, name amigável)
    ("gupy", "gupy", "Gupy"),
    ("ciadeestagios", "ciadeestagios", "Cia de Estágios"),
    ("cia de estagios", "ciadeestagios", "Cia de Estágios"),
    ("eureca", "eureca", "Eureca"),
    ("abler", "abler", "Abler"),
    ("vaga-ja", "vaga-ja", "Vaga Já"),
    ("vaga ja", "vaga-ja", "Vaga Já"),
]


def _slugify(value: str) -> str:
    """Converte texto em slug ASCII minúsculo (ex: 'Cia de Estágios' -> 'cia-de-estagios')."""
    slug = value.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "plataforma"


def _normalize_platform(source_name: str) -> tuple[str, str]:
    """Retorna (slug, name amigável) para um Source.name, agregando subdomínios."""
    if not source_name:
        return ("plataforma", "Plataforma")

    lower = source_name.lower()

    for needle, slug, friendly in _PLATFORM_KNOWN:
        if needle in lower:
            return (slug, friendly)

    # Fallback dinâmico: extrai domínio "limpo" se source_name parece uma URL/host.
    host_match = re.search(r"([a-z0-9-]+\.[a-z]{2,})(?:/|$)", lower)
    if host_match:
        host = host_match.group(1)
        # descarta subdomínio tı́pico (empresa.gupy.io já tratado acima, então aqui
        # pega só ramos não-mapeados e usa a parte principal do host)
        parts = host.split(".")
        if len(parts) >= 2:
            label = parts[-2]
        else:
            label = host
        friendly = label.capitalize()
        return (_slugify(label), friendly)

    # último fallback: capitaliza o próprio Source.name
    return (_slugify(source_name), source_name.strip().capitalize())


@router.get("", response_model=PaginatedJobResponse)
@limiter.limit("60/minute")
async def list_jobs(
    request: Request,
    q: Optional[str] = None,
    area: Optional[JobArea] = None,
    location: Optional[str] = None,
    modality: Optional[JobModality] = None,
    platform: Optional[str] = Query(None, description="Slug ou nome (parcial) da plataforma"),
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

    if platform:
        # JOIN explícito com Source -- muito mais performático que EXISTS()
        # em PostgreSQL. Combina com slug (ex: "gupy") ou nome parcial.
        query = query.join(Job.source).where(
            func.lower(Source.name).contains(platform.lower())
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    if q and db.bind and db.bind.dialect.name == "postgresql":
        # Ordena por relevância (ts_rank) primeiro, depois por data
        query = query.order_by(
            text(
                "ts_rank(jobs.search_vector, websearch_to_tsquery('portuguese', unaccent(:rank_q))) DESC"
            ).bindparams(rank_q=q),
            Job.posted_at.desc().nulls_last(),
        )
    elif q:
        # SQLite: correspondência exata no título tem prioridade sobre company
        safe_q_rank = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.order_by(
            case(
                (Job.title.ilike(f"%{safe_q_rank}%", escape="\\"), 0),
                else_=1,
            ),
            Job.posted_at.desc().nulls_last(),
        )
    else:
        query = query.order_by(Job.posted_at.desc().nulls_last())

    query = query.offset(skip).limit(limit)

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


@router.get("/platforms", response_model=list[PlatformResponse])
@limiter.limit("60/minute")
async def list_platforms(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Agrega vagas ativas por plataforma, normaliza nomes e retorna contagem.

    Exemplo: agrupa bmw.gupy.io / bauducco.gupy.io sob slug 'gupy' / name 'Gupy'.
    A tabela Source contém N entradas individuais por subdomínio, então aqui
    aplicamos normalização para entregar ao filtro do frontend uma lista limpa.
    """
    stmt = (
        select(Source.name, func.count(Job.id).label("count"))
        .join(Job, Job.source_uuid == Source.id)
        .where(Job.is_active == True)
        .group_by(Source.name)
    )
    rows = (await db.execute(stmt)).all()

    # Agrega contagens por plataforma normalizada e ordena por count desc.
    aggregated: dict[tuple[str, str], int] = {}
    for source_name, count in rows:
        slug, friendly = _normalize_platform(source_name)
        key = (slug, friendly)
        aggregated[key] = aggregated.get(key, 0) + int(count)

    return [
        PlatformResponse(slug=key[0], name=key[1], count=cnt)
        for key, cnt in sorted(aggregated.items(), key=lambda x: (-x[1], x[0][1]))
    ]


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

