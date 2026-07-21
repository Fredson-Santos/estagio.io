import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_extract_success(mocker):
    # Mocking _get_llm_client and extract_job
    mocker.patch("api._get_llm_client", return_value=("mock_client", "mock_model"))
    
    mock_result = {
        "cargo": "Desenvolvedor",
        "empresa": "Tech",
        "plataforma": "LinkedIn",
        "localizacao": "Remoto",
        "modalidade": "Remoto",
        "tipo_contrato": "CLT",
        "salario": "Não informado",
        "descricao_resumida": "Vaga legal.",
        "url": "https://linkedin.com/vaga",
        "data_extracao": "2023-01-01T00:00:00"
    }
    mocker.patch("api.extract_job", return_value=mock_result)

    response = client.post("/extract", json={"url": "https://linkedin.com/vaga"})
    assert response.status_code == 200
    data = response.json()
    assert data["cargo"] == "Desenvolvedor"
    assert data["empresa"] == "Tech"
    assert data["url"] == "https://linkedin.com/vaga"

def test_extract_llm_client_error(mocker):
    mocker.patch("api._get_llm_client", side_effect=SystemExit("Erro API_KEY"))
    
    response = client.post("/extract", json={"url": "https://linkedin.com/vaga"})
    assert response.status_code == 503
    assert "Erro API_KEY" in response.json()["detail"]
