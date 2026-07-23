import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_jobs():
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert isinstance(data["items"], list)

def test_read_job_not_found():
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/jobs/{random_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Vaga não encontrada"}

def test_read_jobs_with_q():
    response = client.get("/api/v1/jobs?q=desenvolvedor")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_read_jobs_with_area_filter():
    """Valida que o filtro por área aceita os valores do enum JobArea."""
    response = client.get("/api/v1/jobs?area=TI_SOFTWARE")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for item in data["items"]:
        assert item["area"] == "TI_SOFTWARE"

def test_read_jobs_with_modality_filter():
    """Valida que o filtro por modalidade aceita os valores do enum JobModality."""
    response = client.get("/api/v1/jobs?modality=REMOTE")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for item in data["items"]:
        assert item["modality"] == "REMOTE"

def test_read_jobs_with_invalid_area():
    """Valida que um valor inválido de área retorna erro de validação."""
    response = client.get("/api/v1/jobs?area=INVALIDO")
    assert response.status_code == 422

def test_read_jobs_with_wildcard_in_q():
    """Valida que wildcards LIKE no parâmetro q não causam erro."""
    response = client.get("/api/v1/jobs?q=%25%25%25%25%25")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
