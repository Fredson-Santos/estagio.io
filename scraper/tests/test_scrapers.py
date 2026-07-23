import pytest
from estagio_shared.services.scrapers.gupy import parse_gupy_job, _guess_area
from estagio_shared.services.scrapers.eureca import parse_eureca_job
from estagio_shared.services.dedup import is_duplicate
from estagio_shared.taxonomy import JobArea, JobModality

def test_guess_area():
    assert _guess_area("Desenvolvedor Python Backend", "Python, SQL, APIs") == JobArea.TI_SOFTWARE
    assert _guess_area("Estágio em Marketing", "SEO e Google Ads") == JobArea.MARKETING
    assert _guess_area("Estágio em RH", "Recrutamento e seleção") == JobArea.RH

def test_parse_gupy_job():
    raw_json = {
        "id": 123456,
        "name": "Estagiário de Dados",
        "careerPageName": "Tech Corp",
        "city": "São Paulo",
        "state": "SP",
        "workplaceType": "hybrid",
        "description": "Limpeza de dados e SQL",
        "jobUrl": "https://techcorp.gupy.io/jobs/123456",
        "publishedDate": "2026-07-15T14:00:00.000Z",
        "careerPageLogo": "https://logo.gupy.io/tech.png"
    }
    
    parsed = parse_gupy_job(raw_json)
    
    assert parsed["title"] == "Estagiário de Dados"
    assert parsed["company"] == "Tech Corp"
    assert parsed["location"] == "São Paulo, SP"
    assert parsed["modality"] == JobModality.HYBRID
    assert parsed["area"] == JobArea.DADOS
    assert parsed["source_url"] == "https://techcorp.gupy.io/jobs/123456"
    assert parsed["company_logo"] == "https://logo.gupy.io/tech.png"

def test_parse_eureca_job():
    raw_json = {
        "id": "123456",
        "name": "Estagiário de Dados",
        "companyName": "Tech Corp",
        "locations": {"states":["SP"],"cities":["São Paulo"]},
        "workModel": "hibrido",
        "description": "Limpeza de dados e SQL",
        "createdAt": "2026-07-15 14:00:00+00",
        "companyLogoUrl": "https://eureca.me/logo.png"
    }
    
    parsed = parse_eureca_job(raw_json)
    
    assert parsed["title"] == "Estagiário de Dados"
    assert parsed["company"] == "Tech Corp"
    assert parsed["location"] == "São Paulo - SP"
    assert parsed["modality"] == JobModality.HYBRID
    assert parsed["area"] == JobArea.DADOS
    assert parsed["source_url"] == "https://oportunidades.eureca.me/oportunidade/123456"
    assert parsed["company_logo"] == "https://eureca.me/logo.png"

def test_dedup_logic():
    existing = [
        {"title": "Estagiário de Dados", "company": "Tech Corp", "location": "São Paulo, SP", "source_url": "https://techcorp.gupy.io/jobs/123456"}
    ]
    
    # Exatamente igual (baseado na URL)
    assert is_duplicate({"title": "Estagiário", "company": "Tech", "location": "SP", "source_url": "https://techcorp.gupy.io/jobs/123456"}, existing) == True
    
    # Quase igual (sem a URL idêntica, mas nome muito parecido)
    assert is_duplicate({"title": "Estagio de Dados", "company": "Tech Corp", "location": "Sao Paulo, SP", "source_url": "https://techcorp.gupy.io/jobs/654321"}, existing) == True
    
    # Diferente
    assert is_duplicate({"title": "Desenvolvedor Backend", "company": "Google", "location": "Remoto", "source_url": "https://google.com/jobs"}, existing) == False
