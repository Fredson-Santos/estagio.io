import uuid
from datetime import datetime, timezone

import pytest

from app.db.models import Job, Source
from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus


def _make_item(**overrides) -> dict:
    base = {
        "title": "Estagio Backend",
        "company": "ACME",
        "location": "Sao Paulo",
        "modality": "REMOTE",
        "area": "TI_SOFTWARE",
        "description": "Descricao da vaga",
        "salary": "R$ 2000",
        "company_logo": "https://logo.png",
        "source_url": "https://example.com/job/1",
        "source_id": "gupy-1",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "source_name": "Gupy",
    }
    base.update(overrides)
    return base


async def test_ingest_unauthorized(client):
    response = await client.post("/api/v1/ingest", json={"items": []})
    assert response.status_code == 401


async def test_ingest_empty_returns_zero(client, admin_headers):
    response = await client.post(
        "/api/v1/ingest", json={"items": []}, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {"inserted": 0, "duplicated": 0, "errors": []}


async def test_ingest_inserts_new_job(client, admin_headers, db_session):
    item = _make_item()
    response = await client.post(
        "/api/v1/ingest", json={"items": [item]}, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["inserted"] == 1
    assert data["duplicated"] == 0
    assert data["errors"] == []

    from sqlalchemy.future import select
    result = await db_session.execute(select(Job).where(Job.source_url == item["source_url"]))
    job = result.scalars().first()
    assert job is not None
    assert job.title == "Estagio Backend"
    assert job.is_active is True
    assert job.status == JobStatus.ACTIVE


async def test_ingest_inserts_job_with_extra_fields(client, admin_headers, db_session):
    item = _make_item(
        benefits="VR + VT",
        requirements="Python",
        deadline=datetime.now(timezone.utc).isoformat(),
        is_pcd=True,
        contract_type="estagio",
        duration_months=12,
        salary_min_cents=200000,
        salary_max_cents=300000,
    )
    response = await client.post(
        "/api/v1/ingest", json={"items": [item]}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["inserted"] == 1

    from sqlalchemy.future import select
    result = await db_session.execute(select(Job).where(Job.source_url == item["source_url"]))
    job = result.scalars().first()
    assert job.benefits == "VR + VT"
    assert job.requirements == "Python"
    assert job.is_pcd is True
    assert job.contract_type == "estagio"
    assert job.duration_months == 12
    assert job.salary_min_cents == 200000
    assert job.salary_max_cents == 300000


async def test_ingest_dedup_by_source_url(client, admin_headers):
    item = _make_item()
    payload = {"items": [item]}

    first = await client.post("/api/v1/ingest", json=payload, headers=admin_headers)
    assert first.json() == {"inserted": 1, "duplicated": 0, "errors": []}

    second = await client.post("/api/v1/ingest", json=payload, headers=admin_headers)
    assert second.json() == {"inserted": 0, "duplicated": 1, "errors": []}


async def test_ingest_invalid_area_returns_error(client, admin_headers):
    item = _make_item(area="INVALID_AREA")
    response = await client.post(
        "/api/v1/ingest", json={"items": [item]}, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["inserted"] == 0
    assert data["duplicated"] == 0
    assert len(data["errors"]) == 1
    assert "area invalida" in data["errors"][0]


async def test_ingest_creates_source_if_missing(client, admin_headers, db_session):
    item = _make_item(source_name="NovoPortal")
    response = await client.post(
        "/api/v1/ingest", json={"items": [item]}, headers=admin_headers
    )
    assert response.json()["inserted"] == 1

    from sqlalchemy.future import select
    result = await db_session.execute(select(Source).where(Source.name == "NovoPortal"))
    source = result.scalars().first()
    assert source is not None
    assert source.type == "ingest"


async def test_ingest_derives_source_from_host_when_name_missing(client, admin_headers, db_session):
    item = _make_item(source_url="https://meusite.com/vaga/123", source_name=None)
    response = await client.post(
        "/api/v1/ingest", json={"items": [item]}, headers=admin_headers
    )
    assert response.json()["inserted"] == 1

    from sqlalchemy.future import select
    result = await db_session.execute(select(Source).where(Source.name == "meusite.com"))
    source = result.scalars().first()
    assert source is not None


async def test_expire_unauthorized(client):
    response = await client.post("/api/v1/expire", json={"expired_urls": []})
    assert response.status_code == 401


async def test_expire_empty_returns_zero(client, admin_headers):
    response = await client.post(
        "/api/v1/expire", json={"expired_urls": []}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json() == {"expired": 0}


async def test_expire_marks_jobs_inactive(client, admin_headers, seed_job, db_session):
    response = await client.post(
        "/api/v1/expire",
        json={"expired_urls": [seed_job.source_url]},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json() == {"expired": 1}

    from sqlalchemy.future import select
    result = await db_session.execute(select(Job).where(Job.id == seed_job.id))
    job = result.scalars().first()
    assert job.is_active is False
    assert job.status == JobStatus.CLOSED
    assert job.closed_at is not None


async def test_expire_ignores_already_inactive(client, admin_headers, seed_job, db_session):
    seed_job.is_active = False
    await db_session.commit()

    response = await client.post(
        "/api/v1/expire",
        json={"expired_urls": [seed_job.source_url]},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json() == {"expired": 0}
