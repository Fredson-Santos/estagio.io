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

@pytest.mark.asyncio
async def test_read_jobs_with_q():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/jobs?q=desenvolvedor")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

@pytest.mark.asyncio
async def test_read_jobs_with_area_filter():
    """Valida que o filtro por área aceita os valores do enum JobArea."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/jobs?area=TI_SOFTWARE")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # Todas as vagas retornadas devem ter a área filtrada
    for item in data["items"]:
        assert item["area"] == "TI_SOFTWARE"

@pytest.mark.asyncio
async def test_read_jobs_with_modality_filter():
    """Valida que o filtro por modalidade aceita os valores do enum JobModality."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/jobs?modality=REMOTE")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for item in data["items"]:
        assert item["modality"] == "REMOTE"

@pytest.mark.asyncio
async def test_read_jobs_with_invalid_area():
    """Valida que um valor inválido de área retorna erro de validação."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/jobs?area=INVALIDO")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_read_jobs_with_wildcard_in_q():
    """Valida que wildcards LIKE no parâmetro q não causam erro."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/jobs?q=%25%25%25%25%25")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
