import pytest
from src.scrapers.gupy import parse_gupy_job, parse_gupy_vagaja_job, _guess_area, _is_internship_vagaja
from src.scrapers.eureca import parse_eureca_job
from src.scrapers.ciadeestagios import parse_ciadeestagios_job
from src.scrapers.abler import parse_abler_job
from src.services.dedup import is_duplicate
from src.services.base import parse_location_obj, format_modality_enum, clean_html, format_company_name, extract_areas_and_category
from estagio_shared.taxonomy import JobArea, JobModality


def test_guess_area():
    assert _guess_area("Desenvolvedor Python Backend", "Python, SQL, APIs") == JobArea.TI_SOFTWARE
    assert _guess_area("Estágio em Marketing", "SEO e Google Ads") == JobArea.MARKETING
    assert _guess_area("Estágio em RH", "Recrutamento e seleção") == JobArea.RH
    # Caso crítico: Administração que cita marketing e TI na descrição deve permanecer NEGOCIOS
    assert _guess_area("Estágio em Administração", "Atuará com interface com equipes de marketing e TI.") == JobArea.NEGOCIOS
    assert _guess_area("Estágio em Recursos Humanos", "Interface com desenvolvedores e sistemas de TI.") == JobArea.RH
    # Casos de Programa de Estágio Multi-Áreas
    assert _guess_area("Programa de Estágio 2026 - Diversas Áreas", "Vagas em TI, Marketing, RH e Finanças") == JobArea.PROGRAMA_ESTAGIO
    assert _guess_area("Estágio Corporativo", "Oportunidades em várias áreas da empresa") == JobArea.PROGRAMA_ESTAGIO

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
    assert parsed["source_url"] == "https://app.eureca.me/vagas/123456"
    assert parsed["company_logo"] == "https://eureca.me/logo.png"


def test_parse_eureca_job_varias_localidades():
    raw_json = {
        "id": "789101",
        "name": "Trainee em Marketing/Produtos",
        "companyName": "L'Oréal",
        "locations": {},
        "workModel": "hibrido",
        "description": "Programa de trainee abrangente para diversas áreas de marketing",
        "createdAt": "2026-07-15 14:00:00+00",
        "companyLogoUrl": "https://eureca.me/logo.png"
    }

    parsed = parse_eureca_job(raw_json)

    assert parsed["location"] == "Várias Localidades"
    from src.services.job_validator import validate_job
    is_valid, reason = validate_job(parsed)
    assert is_valid is True
    assert reason == ""



def test_parse_eureca_job_with_detail():
    """Testa merge de dados de detalhe da listagem."""
    item_json = {
        "id": "abc123",
        "name": "Estágio em TI",
        "companyName": "Empresa Confidencial",
        "locations": {"states": ["SP"], "cities": ["Campinas"]},
        "workModel": "presencial",
        "createdAt": "2026-08-01T00:00:00+00:00",
    }
    detail_json = {
        "id": "abc123",
        "title": "Estágio em Desenvolvimento de Software",
        "companyName": "Tech Corp LTDA",
        "cityName": "Campinas",
        "stateAcronym": "SP",
        "isRemoteWork": True,
        "description": "Atuar com desenvolvimento Python e SQL",
        "salary": "R$ 1.500,00",
        "contractTypeKey": "estagio",
        "logo": "https://eureca.me/logo_detail.png",
    }
    
    parsed = parse_eureca_job(item_json, detail_json)
    # Detail tem prioridade
    assert parsed["title"] == "Estágio em Desenvolvimento de Software"
    assert parsed["company"] == "Tech Corp LTDA"
    # Modality vem de isRemoteWork (detail)
    assert parsed["modality"] == JobModality.REMOTE
    assert parsed["location"] == "Remoto"
    assert parsed["description"] == "Atuar com desenvolvimento Python e SQL"
    assert parsed["company_logo"] == "https://eureca.me/logo_detail.png"
    assert parsed["area"] == JobArea.TI_SOFTWARE


def test_parse_ciadeestagios_job():
    raw_json = {
        "id": 456,
        "company": "Empresa Cia de Estágios",
        "name": "Estágio em Marketing",
        "localization": "São Paulo, SP",
        "link": "https://ciadeestagios.com.br/vaga/456",
        "activities": "<p>Atuar com campanhas de marketing digital</p>",
        "stipend": "R$ 1.200,00",
        "type": "estagio",
        "period": "6 meses",
        "start_date": "2026-08-01",
        "end_date": "2026-12-31",
        "benefits": "Vale-transporte, Vale-alimentação",
        "requirements": "Conhecimento em marketing",
        "card_image": "https://cia.com.br/logo.png",
    }
    
    parsed = parse_ciadeestagios_job(raw_json)
    
    assert parsed["title"] == "Estágio em Marketing"
    assert parsed["company"] == "Empresa Cia de Estágios"
    assert parsed["location"].startswith("São Paulo")
    assert parsed["modality"] == JobModality.ONSITE
    assert parsed["area"] == JobArea.MARKETING
    assert parsed["source_url"] == "https://ciadeestagios.com.br/vaga/456"
    assert "campanhas de marketing digital" in parsed["description"]
    assert parsed["is_pcd"] == False
    assert parsed["contract_type"] == "Estágio"
    assert parsed["duration_months"] == 6


def test_parse_abler_job():
    attr = {
        "title": "Estágio em Dados",
        "description": "<p>Análise de dados e SQL</p>",
        "city": "Belo Horizonte",
        "state": "MG",
        "workplacetype": ["home"],
        "salary_display": "R$ 1.800,00",
        "contracting_regime": "estágio",
    }
    link = "https://candidatos.abler.com.br/vagas/estagio-dados"
    
    parsed = parse_abler_job(
        attr, v_id="abler789", link=link, company="Tech Abler", logo="https://abler.com/logo.png"
    )
    
    assert parsed["title"] == "Estágio em Dados"
    assert parsed["company"] == "Tech Abler"
    assert parsed["location"] == "Remoto"
    assert parsed["modality"] == JobModality.REMOTE
    assert parsed["area"] == JobArea.DADOS
    assert parsed["source_url"] == link
    assert parsed["source_id"] == "abler789"
    assert "Análise de dados e SQL" in parsed["description"]
    assert parsed["is_pcd"] == False
    assert parsed["contract_type"] == "Estágio"


def test_parse_abler_job_pcd():
    attr = {
        "title": "Estágio PCD - Direito",
        "description": "Atuar com elaboração de contratos",
        "workplacetype": [],
        "contracting_regime": "estagio",
    }
    parsed = parse_abler_job(attr, "v1", "https://abler/v1", "Jurídico SA", None)
    assert parsed["is_pcd"] == True
    assert parsed["area"] == JobArea.DIREITO


def test_parse_abler_job_no_salary_fallback():
    attr = {
        "title": "Estágio em TI",
        "description": "Vaga com descrição longa detalhada sobre as atividades do estagiário.",
        "workplacetype": ["home"],
    }
    parsed = parse_abler_job(attr, "v2", "https://abler/v2", "Empresa X", None)
    assert parsed["salary"] is None
    assert parsed["salary_min_cents"] is None


def test_parse_abler_job_salary_min():
    attr = {
        "title": "Estágio em Engenharia",
        "description": "Desenvolvimento de projetos",
        "salary_min": 1500,
        "salary_max": 2000,
    }
    parsed = parse_abler_job(attr, "v3", "https://abler/v3", "Engenharia SA", None)
    assert parsed["salary"] == "R$ 1500 - R$ 2000"
    assert parsed["salary_min_cents"] == 150000
    assert parsed["salary_max_cents"] == 200000



def test_parse_gupy_vagaja_job():
    raw_item = {
        "id": "vagaja123",
        "title": "Estagiário de Design",
        "description": "Atuar com Figma e prototipagem",
        "workScale": {"name": "Estágio 20h/semana"},
        "company": {"name": "Design Studio", "logoUrl": "https://logo.ds.io/d.png"},
        "companyAddress": {"city": "Curitiba", "state": "PR"},
        "availability": "REMOTE",
        "salaryMin": 1500,
        "publicShortUrl": "https://vagaja.io/s/abc123",
        "publishedAt": "2026-07-20T10:00:00.000Z",
    }
    
    parsed = parse_gupy_vagaja_job(raw_item)
    assert parsed is not None
    assert parsed["title"] == "Estagiário de Design"
    assert parsed["company"] == "Design Studio"
    assert parsed["location"] == "Remoto"
    assert parsed["modality"] == JobModality.REMOTE
    assert parsed["area"] == JobArea.DESIGN
    assert parsed["source_url"] == "https://vagaja.io/s/abc123"
    assert parsed["source_id"] == "vagaja123"


def test_parse_gupy_vagaja_job_not_internship():
    raw_item = {
        "id": "not_intern",
        "title": "Desenvolvedor Sênior Backend",
        "description": "Atuar com Java e Spring",
        "workScale": {"name": "CLT 40h/semana"},
    }
    parsed = parse_gupy_vagaja_job(raw_item)
    assert parsed is None


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


# === Testes dos helpers em base.py ===

def test_parse_location_obj_city_state():
    loc = parse_location_obj(city_val="São Paulo", state_val="SP")
    assert loc["city"] == "São Paulo"
    assert loc["state"] == "SP"
    assert loc["country"] == "BR"

def test_parse_location_obj_raw_str():
    loc = parse_location_obj(raw_loc_str="Rio de Janeiro - RJ")
    assert loc["city"] is not None
    assert loc["state"] == "RJ"

def test_format_modality_enum():
    assert format_modality_enum("remote") == JobModality.REMOTE
    assert format_modality_enum("HOME OFFICE") == JobModality.REMOTE
    assert format_modality_enum("híbrido") == JobModality.HYBRID
    assert format_modality_enum("presencial") == JobModality.ONSITE
    assert format_modality_enum(None) == JobModality.ONSITE

def test_clean_html():
    assert clean_html("<p>Hello <b>world</b></p>") == "Hello world"
    assert clean_html(None) == ""
    assert clean_html("  text  ") == "text"

def test_format_company_name():
    assert format_company_name("Tech Corp LTDA (EPP)") == "Tech Corp LTDA"
    assert format_company_name(None) == "Empresa não informada"
    assert format_company_name("Plain Company") == "Plain Company"

def test_extract_areas_and_category_program():
    category, areas = extract_areas_and_category("Programa de Estágio 2026", "Vagas em várias áreas")
    assert category == "INTERNSHIP_PROGRAM"

def test_extract_areas_and_category_internship():
    category, _ = extract_areas_and_category("Estágio em TI", "Desenvolvimento")
    assert category == "INTERNSHIP"


# === Testes do matcher (regex_fallback_classify) ===

def test_regex_fallback_classify():
    from src.services.matcher import regex_fallback_classify
    
    areas = regex_fallback_classify("desenvolvimento de software backend")
    assert "IT" in areas
    
    areas = regex_fallback_classify("analista de dados e BI")
    assert "DATA" in areas
    
    areas = regex_fallback_classify("marketing digital e SEO")
    assert "MARKETING" in areas
    
    areas = regex_fallback_classify("estágio em recursos humanos")
    assert "HUMAN_RESOURCES" in areas
    
    # Multi-área
    areas = regex_fallback_classify("desenvolvimento de software e análise de dados")
    assert "IT" in areas
    assert "DATA" in areas
    
    # Vazio/nada
    assert regex_fallback_classify(None) == []
    assert regex_fallback_classify("asdf qwerty") == []
