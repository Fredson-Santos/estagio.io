"""Scraper da Abler.

Portado do scraper-api/services/abler.py, adaptado para async (httpx) e
o formato de dados do estagio.io (ScrapedJob).

Faz scraping público via cookie __pgt → x-proxy-guard-token contra a
Candidate API (candidatos.abler.com.br/api/candidate/v2/vacancies).
"""
import asyncio
import logging

import httpx

from estagio_shared.taxonomy import JobArea, JobModality

from src.services.base import (
    clean_html,
    clean_val,
    format_iso_datetime,
    normalize_location,
    parse_location_obj,
)
from src.services.job_validator import (
    parse_duration_months,
    parse_salary,
    parse_salary_cents,
    trunc,
)

logger = logging.getLogger(__name__)

ABLER_CANDIDATE_URL = "https://candidatos.abler.com.br/vagas?q=estagio"
ABLER_CANDIDATE_API = "https://candidatos.abler.com.br/api/candidate/v2/vacancies"

REQUEST_DELAY = 0.5
MAX_PAGES = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://candidatos.abler.com.br/vagas?q=estagio",
}


def _detect_modality(wpt_str: str, desc: str) -> JobModality:
    s = (wpt_str or "").lower()
    d = (desc or "").lower()
    if "home" in s or "remot" in s or "remot" in d:
        return JobModality.REMOTE
    if "presencial" in s:
        return JobModality.ONSITE
    return JobModality.HYBRID


def _parse_company(company_raw) -> str:
    if isinstance(company_raw, str) and company_raw.strip():
        return clean_val(company_raw)
    if isinstance(company_raw, dict):
        return clean_val(company_raw.get("name") or company_raw.get("trade_name") or "Empresa Abler")
    return "Empresa Abler"


def parse_abler_job(attr: dict, v_id: str, link: str, company: str, logo: str | None, modality_hint: JobModality | None = None) -> dict:
    title = clean_val(attr.get("title")) or "Vaga de Estágio Abler"
    desc = clean_html(attr.get("description") or "")

    city = clean_val(attr.get("city"))
    state = clean_val(attr.get("state"))
    wpt = attr.get("workplacetype", [])
    wpt_str = " ".join(wpt) if isinstance(wpt, list) else str(wpt or "")

    modality = modality_hint or _detect_modality(wpt_str, desc)

    loc_obj = parse_location_obj(
        city_val=city,
        state_val=state,
        raw_loc_str=f"{city}, {state}" if city else None,
        modality=modality.value,
    )
    city_val = loc_obj.get("city") or ""
    state_val = loc_obj.get("state") or ""
    location = normalize_location(city_val, state_val) if city_val else "Não informado"
    if modality == JobModality.REMOTE:
        location = "Remoto"

    is_pcd = "pcd" in title.lower() or "pcd" in desc.lower()

    sal_display = clean_val(attr.get("salary_display"))
    sal_min = attr.get("salary_min")
    sal_max = attr.get("salary_max")
    
    raw_sal = sal_display
    if not raw_sal:
        if sal_min and sal_max:
            raw_sal = f"R$ {sal_min} - R$ {sal_max}"
        elif sal_min:
            raw_sal = f"R$ {sal_min}"
        elif sal_max:
            raw_sal = f"Até R$ {sal_max}"
        else:
            raw_sal = None

    salary = parse_salary(raw_sal)
    salary_min_cents, salary_max_cents = parse_salary_cents(raw_sal or salary)
    if sal_min and not salary_min_cents:
        try:
            salary_min_cents = int(float(sal_min) * 100)
        except (ValueError, TypeError):
            pass
    if sal_max and not salary_max_cents:
        try:
            salary_max_cents = int(float(sal_max) * 100)
        except (ValueError, TypeError):
            pass

    contract_raw = clean_val(attr.get("contracting_regime")) or "estágio"
    contract_type = "Estágio"
    if "trainee" in contract_raw.lower():
        contract_type = "Trainee"
    elif "clt" in contract_raw.lower() or "efetivo" in contract_raw.lower():
        contract_type = "CLT"

    duration_months = parse_duration_months(f"{title} {desc}")

    posted_at = format_iso_datetime(
        clean_val(attr.get("published_at") or attr.get("updated_at") or attr.get("created_at"))
    )

    from src.scrapers.gupy import _guess_area

    area = _guess_area(title, desc)

    return {
        "title": trunc(title, 255),
        "company": trunc(company, 255),
        "location": trunc(location, 255),
        "modality": modality,
        "area": area,
        "description": desc[:4000] if len(desc) > 4000 else desc,
        "salary": trunc(salary, 255),
        "salary_min_cents": salary_min_cents,
        "salary_max_cents": salary_max_cents,
        "company_logo": trunc(logo, 1000),
        "source_url": trunc(link, 1000),
        "source_id": trunc(v_id, 255),
        "posted_at": posted_at,
        "benefits": None,
        "requirements": None,
        "deadline": None,
        "is_pcd": is_pcd,
        "contract_type": trunc(contract_type, 50),
        "duration_months": duration_months,
    }


async def _fetch_abler_vacancies(client: httpx.AsyncClient) -> list[dict]:
    """Scraping público: obtém cookie __pgt e usa x-proxy-guard-token."""
    pgt: str | None = None
    try:
        resp = await client.get(ABLER_CANDIDATE_URL, timeout=10.0)
        pgt = client.cookies.get("__pgt")
    except Exception as exc:
        logger.warning("Abler: erro ao obter cookie __pgt: %s", exc)

    if not pgt:
        logger.warning("Abler: cookie __pgt não encontrado.")
        return []

    headers = {**HEADERS, "x-proxy-guard-token": pgt}
    all_items: list[dict] = []
    page = 1
    per_page = 50

    while page <= MAX_PAGES:
        params = {"page": page, "per_page": per_page, "q": "estagio", "provider": ""}
        try:
            resp = await client.get(ABLER_CANDIDATE_API, headers=headers, params=params, timeout=10.0)
            if resp.status_code != 200:
                logger.warning("Abler: status %d na página %d", resp.status_code, page)
                break
            data = resp.json()
            items = data.get("data", [])
            if not items:
                break
            all_items.extend(items)
            logger.info("Abler: página %d — %d vagas", page, len(items))
            meta = data.get("meta", {})
            last_page = meta.get("last", 1)
            if page >= last_page:
                break
            page += 1
            await asyncio.sleep(REQUEST_DELAY)
        except Exception as exc:
            logger.warning("Abler: erro na página %d: %s", page, exc)
            break

    return all_items


async def run_abler_scraper() -> list[dict]:
    from src.services.job_validator import validate_job, safe_str

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        raw_items = await _fetch_abler_vacancies(client)

    logger.info("Abler: %d vagas brutas recebidas.", len(raw_items))

    valid_jobs: list[dict] = []
    for item in raw_items:
        attr = item.get("attributes", {}) if isinstance(item, dict) else {}
        if not attr:
            attr = item

        v_id = str(item.get("id", ""))
        link = (
            clean_val(attr.get("url"))
            or f"https://candidatos.abler.com.br/vagas/{clean_val(attr.get('identifier')) or v_id}"
        )
        company = _parse_company(attr.get("company"))
        logo = clean_val(attr.get("logo"))

        try:
            job_data = parse_abler_job(attr, v_id, link, company, logo)
            is_valid, reason = validate_job(job_data)
            if is_valid:
                valid_jobs.append(job_data)
            else:
                logger.info("[Abler] Vaga '%s' descartada: %s", safe_str(job_data.get("title")), reason)
        except Exception as exc:
            logger.warning("[Abler] Erro ao processar vaga %s: %s", v_id, exc)

    logger.info("Abler: %d vagas válidas.", len(valid_jobs))
    return valid_jobs