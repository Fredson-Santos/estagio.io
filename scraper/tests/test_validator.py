import pytest
from src.services.job_validator import validate_job
from estagio_shared.taxonomy import JobModality, JobArea


def test_validate_valid_onsite_job():
    job = {
        "title": "Estágio em Desenvolvimento Python",
        "company": "Tech Solutions",
        "location": "São Paulo, SP",
        "modality": JobModality.ONSITE,
        "area": JobArea.TI_SOFTWARE,
        "description": "Atuar no desenvolvimento e manutenção de sistemas Python backend com FastAPI.",
        "source_url": "https://gupy.io/vaga/123",
    }
    is_valid, reason = validate_job(job)
    assert is_valid is True
    assert reason == ""

def test_validate_valid_remote_job():
    job = {
        "title": "Estágio em Data Analytics",
        "company": "Data Corp",
        "location": "Remoto",
        "modality": JobModality.REMOTE,
        "area": JobArea.DADOS,
        "description": "Análise de dados com SQL, PowerBI e Python para apoiar a tomada de decisão.",
        "source_url": "https://eureca.me/oportunidade/456",
    }
    is_valid, reason = validate_job(job)
    assert is_valid is True
    assert reason == ""

def test_reject_job_without_title():
    job = {
        "title": "N/A",
        "company": "Tech Corp",
        "location": "São Paulo, SP",
        "modality": JobModality.ONSITE,
        "description": "Descrição válida da vaga com mais de 30 caracteres.",
        "source_url": "https://gupy.io/vaga/123",
    }
    is_valid, reason = validate_job(job)
    assert is_valid is False
    assert "Título" in reason

def test_reject_job_without_company():
    job = {
        "title": "Estágio em RH",
        "company": "Não informado",
        "location": "Rio de Janeiro, RJ",
        "modality": JobModality.ONSITE,
        "description": "Descrição válida da vaga com mais de 30 caracteres para testes de validação.",
        "source_url": "https://gupy.io/vaga/123",
    }
    is_valid, reason = validate_job(job)
    assert is_valid is False
    assert "Empresa" in reason

def test_reject_onsite_job_without_location():
    job = {
        "title": "Estágio em Marketing",
        "company": "Agência X",
        "location": "Não informado",
        "modality": JobModality.ONSITE,
        "description": "Descrição com conteúdo suficiente para passar na validação de descrição.",
        "source_url": "https://gupy.io/vaga/123",
    }
    is_valid, reason = validate_job(job)
    assert is_valid is False
    assert "localização" in reason

def test_reject_job_without_description():
    job = {
        "title": "Estágio em Finanças",
        "company": "Banco Y",
        "location": "São Paulo, SP",
        "modality": JobModality.HYBRID,
        "description": "Curto",
        "source_url": "https://gupy.io/vaga/123",
    }
    is_valid, reason = validate_job(job)
    assert is_valid is False
    assert "Descrição" in reason

def test_reject_job_with_error():
    job = {
        "title": "Estágio em Vendas",
        "company": "Empresa Z",
        "location": "Curitiba, PR",
        "modality": JobModality.ONSITE,
        "description": "Descrição da vaga longa suficiente para passar pelo filtro básico.",
        "source_url": "https://gupy.io/vaga/123",
        "erro": "Erro ao acessar a página HTML",
    }
    is_valid, reason = validate_job(job)
    assert is_valid is False
    assert "erro" in reason.lower()
