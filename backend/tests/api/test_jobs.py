import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_read_jobs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_read_job_not_found():
    random_id = str(uuid.uuid4())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/jobs/{random_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Vaga não encontrada"}
