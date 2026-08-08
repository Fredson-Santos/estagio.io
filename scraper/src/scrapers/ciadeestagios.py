"""Scraper da Cia de Estágios.

Portado do scraper-api/services/ciadeestagios.py, adaptado para async
(httpx) e o formato de dados do estagio.io (ScrapedJob).
"""
import logging

import httpx

from estagio_shared.taxonomy import JobArea, JobModality

from src.services.base import (
    clean_html,
    clean_val,
    format_company_name,
    format_iso_datetime,
    format_modality_enum,
    normalize_location,
    parse_location_obj,
    parse_string_list,
)
from src.services.job_validator import (
    parse_duration_months,
    parse_salary,
    parse_salary_cents,
    trunc,
)

logger = logging.getLogger(__name__)

CIADEESTAGIOS_API_URL = "https://sgce.ciadeestagios.com.br/api/listar.vagas.publicas"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


async def fetch_ciadeestagios_jobs() -> list[dict]:
    """Busca todas as vagas públicas da Cia de Estágios."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(CIADEESTAGIOS_API_URL, headers=HEADERS)
            resp.raise_for_status()
            data = resp.json()
            return data.get("vagas", [])
        except Exception as exc:
            logger.warning("Erro ao buscar vagas da Cia de Estágios: %s", exc)
            return []


def _detect_modality(activities: str, title: str) -> JobModality:
    act_lower = activities.lower()
    title_lower = title.lower()
    if "híbrido" in act_lower or "hibrido" in act_lower or "híbrido" in title_lower:
        return JobModality.HYBRID
    if "home office" in act_lower or "remoto" in act_lower or "remoto" in title_lower:
        return JobModality.REMOTE
    return JobModality.ONSITE


def parse_ciadeestagios_job(raw: dict) -> dict:
    """Converte uma vaga bruta da Cia de Estágios para o formato ScrapedJob."""
    title = clean_val(raw.get("name")) or "Vaga sem título"
    company = format_company_name(raw.get("company"))
    activities = clean_html(raw.get("activities") or "")
    link = clean_val(raw.get("link")) or f"https://ciadeestagios.com.br/vaga/{raw.get('id')}"
    stipend = clean_val(raw.get("stipend"))

    modality = _detect_modality(activities, title)

    loc_obj = parse_location_obj(
        raw_loc_str=raw.get("localization"), modality=modality.value
    )
    city = loc_obj.get("city") or ""
    state = loc_obj.get("state") or ""
    location = normalize_location(city, state) if city else "Não informado"
    if modality == JobModality.REMOTE:
        location = "Remoto"

    salary = parse_salary(stipend)
    salary_min_cents, salary_max_cents = parse_salary_cents(stipend or salary)

    benefits = parse_string_list(raw.get("benefits"))
    requirements = parse_string_list(raw.get("requirements"))

    is_pcd = "pcd" in title.lower() or "pcd" in activities.lower()

    contract_type = "Estágio"
    raw_type = raw.get("type")
    if raw_type:
        if "trainee" in str(raw_type).lower():
            contract_type = "Trainee"
        elif "clt" in str(raw_type).lower() or "efetivo" in str(raw_type).lower():
            contract_type = "CLT"

    duration_months = parse_duration_months(clean_val(raw.get("period")))

    posted_at = format_iso_datetime(clean_val(raw.get("start_date")))
    deadline = format_iso_datetime(clean_val(raw.get("end_date")))

    from src.scrapers.gupy import _guess_area

    area = _guess_area(title, activities)

    return {
        "title": trunc(title, 255),
        "company": trunc(company, 255),
        "location": trunc(location, 255),
        "modality": modality,
        "area": area,
        "description": activities[:4000] if len(activities) > 4000 else activities,
        "salary": trunc(salary, 255),
        "salary_min_cents": salary_min_cents,
        "salary_max_cents": salary_max_cents,
        "company_logo": trunc(clean_val(raw.get("card_image")), 1000),
        "source_url": trunc(link, 1000),
        "source_id": trunc(str(raw.get("id", "")), 255),
        "posted_at": posted_at,
        "benefits": trunc(", ".join(benefits) if benefits else None, 2000),
        "requirements": trunc(", ".join(requirements) if requirements else None, 2000),
        "deadline": deadline,
        "is_pcd": is_pcd,
        "contract_type": trunc(contract_type, 50),
        "duration_months": duration_months,
    }


async def run_ciadeestagios_scraper() -> list[dict]:
    """Pipeline completo: fetch + parse + validate."""
    from src.services.job_validator import validate_job, safe_str

    raw_jobs = await fetch_ciadeestagios_jobs()
    logger.info("Cia de Estágios: %d vagas brutas recebidas.", len(raw_jobs))

    parsed_jobs = [parse_ciadeestagios_job(job) for job in raw_jobs]
    valid_jobs: list[dict] = []
    for j in parsed_jobs:
        is_valid, reason = validate_job(j)
        if is_valid:
            valid_jobs.append(j)
        else:
            logger.info(
                "[Cia de Estágios] Vaga '%s' descartada: %s",
                safe_str(j.get("title")),
                reason,
            )

    logger.info("Cia de Estágios: %d vagas válidas.", len(valid_jobs))
    return valid_jobs
