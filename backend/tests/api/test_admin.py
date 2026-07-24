import uuid
from unittest.mock import patch

from estagio_shared.db.models import Job


async def test_stats_requires_auth(client):
    response = await client.get("/api/v1/admin/stats")
    assert response.status_code == 401


async def test_stats_returns_counts(client, seed_job, admin_headers):
    response = await client.get("/api/v1/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs"] == 1
    assert data["active_jobs"] == 1
    assert data["featured_jobs"] == 0
    assert data["sources"] == 1


async def test_scrapers_run_requires_auth(client):
    response = await client.post("/api/v1/admin/scrapers/run")
    assert response.status_code == 401


async def test_scrapers_run_triggers(client, admin_headers):
    with patch("estagio_shared.services.etl.run_pipeline", new=lambda: None):
        response = await client.post("/api/v1/admin/scrapers/run", headers=admin_headers)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "triggered"


async def test_patch_job_featured(client, seed_job, admin_headers):
    response = await client.patch(
        f"/api/v1/jobs/{seed_job.id}",
        json={"is_featured": True},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_featured"] is True


async def test_patch_job_unauthorized(client, seed_job):
    response = await client.patch(
        f"/api/v1/jobs/{seed_job.id}",
        json={"is_featured": True},
    )
    assert response.status_code == 401


async def test_patch_job_not_found(client, admin_headers):
    response = await client.patch(
        f"/api/v1/jobs/{uuid.uuid4()}",
        json={"is_featured": True},
        headers=admin_headers,
    )
    assert response.status_code == 404


async def test_delete_job_soft_deletes(client, seed_job, admin_headers, db_session):
    response = await client.delete(f"/api/v1/jobs/{seed_job.id}", headers=admin_headers)
    assert response.status_code == 204

    from sqlalchemy.future import select
    result = await db_session.execute(select(Job).where(Job.id == seed_job.id))
    job = result.scalars().first()
    assert job.is_active is False


async def test_delete_job_unauthorized(client, seed_job):
    response = await client.delete(f"/api/v1/jobs/{seed_job.id}")
    assert response.status_code == 401
