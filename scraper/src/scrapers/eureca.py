import asyncio
import httpx
from datetime import datetime
from bs4 import BeautifulSoup

from estagio_shared.taxonomy import JobArea, JobModality
from src.scrapers.gupy import _guess_area
from src.services.base import normalize_location
from src.services.job_validator import trunc

EURECA_OPPORTUNITIES_URL = "https://candidate-api.eureca.me/v2/opportunities"
EURECA_OPPORTUNITY_DETAIL_URL = "https://candidate-api.eureca.me/opportunities/{opp_id}"
EURECA_PROGRAMS_URL = "https://candidate-api.eureca.me/v2/programs"


async def fetch_eureca_jobs(limit: int = 200) -> list[dict]:
    """Busca vagas na Eureca usando a API."""
    all_jobs = []
    chunk_size = 50

    async with httpx.AsyncClient(timeout=15.0) as client:
        page = 1
        while True:
            params = {
                "pageSize": chunk_size,
                "page": page,
            }
            try:
                resp = await client.get(EURECA_OPPORTUNITIES_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                jobs = data.get("items", [])
                total_count = data.get("totalCount", 0)

                if not jobs:
                    break

                all_jobs.extend(jobs)

                if len(jobs) < chunk_size or len(all_jobs) >= limit or page * chunk_size >= total_count:
                    break

                page += 1
            except Exception as exc:
                print(f"Erro ao buscar vagas na Eureca na página {page}: {exc}")
                break

    return all_jobs[:limit]


async def _fetch_eureca_detail(client: httpx.AsyncClient, opp_id: str) -> dict:
    """Busca o detalhe de uma oportunidade específica na Eureca."""
    url = EURECA_OPPORTUNITY_DETAIL_URL.format(opp_id=opp_id)
    try:
        resp = await client.get(url, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        print(f"Erro ao buscar detalhe da oportunidade {opp_id}: {exc}")
        return {}


async def fetch_eureca_programs() -> list[dict]:
    """Busca programas da Eureca usando a API."""
    params = {"pageSize": 100, "page": 1}
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(EURECA_PROGRAMS_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])
        except Exception as exc:
            print(f"Erro ao buscar programas Eureca: {exc}")
            return []

def _map_modality(work_model: str) -> JobModality:
    mapping = {
        "remoto": JobModality.REMOTE,
        "hibrido": JobModality.HYBRID,
        "presencial": JobModality.ONSITE
    }
    if not work_model:
        return JobModality.ONSITE
    return mapping.get(work_model.lower(), JobModality.ONSITE)

def parse_eureca_job(item: dict, detail: dict | None = None) -> dict:
    """Formata o JSON retornado pela Eureca para o formato completo do nosso banco de dados.

    Args:
        item: dados resumidos da listagem /v2/opportunities.
        detail: dados detalhados da rota /opportunities/{id} (opcional).
    """
    d = detail or {}
    # Merge: detail takes precedence but item is the fallback
    title = d.get("title") or item.get("name") or item.get("title") or "Vaga Eureca"
    company = d.get("companyName") or item.get("companyName") or item.get("programName") or "Empresa Confidencial"

    # Location: detail uses cityName/stateAcronym; item uses locations dict
    city_val = d.get("cityName") or ""
    state_val = d.get("stateAcronym") or ""

    if not city_val:
        locations = item.get("locations", {})
        cities = locations.get("cities", [])
        states = locations.get("states", [])
        city_val = ", ".join(cities) if cities else ""
        state_val = ", ".join(states) if states or not state_val else state_val

    location = normalize_location(city_val, state_val) if (city_val or state_val) else "Várias Localidades"

    # Modality: detail uses isRemoteWork; item uses workModel
    is_remote = d.get("isRemoteWork") or item.get("isRemoteWork") or False
    if is_remote:
        modality = JobModality.REMOTE
    else:
        modality = _map_modality(item.get("workModel", ""))
    if modality == JobModality.REMOTE:
        location = "Remoto"

    # Description: detail may have description or aboutOpportunity
    raw_description = d.get("description") or d.get("aboutOpportunity") or item.get("description") or ""
    description = raw_description.strip() if raw_description else ""

    # Salary: detail uses salary; item uses stipend/salary/remuneration
    from src.services.job_validator import parse_salary, parse_salary_cents, parse_duration_months
    salary_dict = d.get("salary") or item.get("salary") or {}
    salary = parse_salary(d.get("salary") or item.get("stipend") or salary_dict or item.get("remuneration"))
    salary_min_cents, salary_max_cents = parse_salary_cents(salary_dict or salary)

    # URL da vaga na Eureca
    opp_id = str(item.get("id", ""))
    source_url = f"https://app.eureca.me/vagas/{opp_id}"
    source_id = opp_id

    created_at_str = item.get("createdAt") or d.get("createdAt")
    posted_at = None
    if created_at_str:
        try:
            posted_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00").replace("+00", "+00:00"))
        except ValueError:
            pass

    end_applying_str = item.get("endApplying") or d.get("endApplying")
    deadline = None
    if end_applying_str:
        try:
            deadline = datetime.fromisoformat(end_applying_str.replace("Z", "+00:00").replace("+00", "+00:00"))
        except ValueError:
            pass

    # Diversidade / PCD
    diversity = item.get("diversity", [])
    is_pcd = any("pcd" in str(x).lower() or "deficiência" in str(x).lower() for x in diversity)
    if not is_pcd and d.get("isPcd"):
        is_pcd = True

    contract_type_key = d.get("contractTypeKey") or item.get("contractTypeKey") or "Estágio"
    contract_type = "Estágio" if "estagio" in contract_type_key.lower() else contract_type_key.capitalize()
    duration_months = parse_duration_months(f"{title} {description}")

    logo = d.get("logo") or d.get("banner") or item.get("companyLogoUrl")

    return {
        "title":            trunc(title, 255),
        "company":          trunc(company, 255),
        "location":         trunc(location, 255),
        "modality":         modality,
        "area":             _guess_area(title, description),
        "description":      description[:4000] if len(description) > 4000 else description,
        "salary":           trunc(salary, 255),
        "salary_min_cents": salary_min_cents,
        "salary_max_cents": salary_max_cents,
        "company_logo":     trunc(logo, 1000),
        "source_url":       trunc(source_url, 1000),
        "source_id":        trunc(source_id, 255),
        "posted_at":        posted_at,
        "benefits":         None,
        "requirements":     trunc(", ".join(diversity) if diversity else None, 2000),
        "deadline":         deadline,
        "is_pcd":           is_pcd,
        "contract_type":    trunc(contract_type, 50),
        "duration_months":  duration_months,
    }


async def run_eureca_scraper(limit: int = 50) -> list[dict]:
    """Pipeline completo: fetch vagas + fetch detalhes concorrente + parse + validate."""
    from src.services.job_validator import validate_job, safe_str

    raw_jobs = await fetch_eureca_jobs(limit=limit)
    print(f"[Eureca Scraper] {len(raw_jobs)} vagas brutas recebidas da listagem.")

    # Busca os detalhes de cada oportunidade concorrentemente
    async with httpx.AsyncClient(timeout=10.0) as client:
        semaphore = asyncio.Semaphore(10)

        async def fetch_detail(opp_id: str) -> dict:
            async with semaphore:
                return await _fetch_eureca_detail(client, opp_id)

        tasks = [fetch_detail(str(item.get("id", ""))) for item in raw_jobs]
        details = await asyncio.gather(*tasks)

    parsed_jobs = [parse_eureca_job(item, detail) for item, detail in zip(raw_jobs, details)]
    valid_jobs: list[dict] = []
    for j in parsed_jobs:
        is_valid, reason = validate_job(j)
        if is_valid:
            valid_jobs.append(j)
        else:
            print(f"[Eureca Scraper] Vaga '{safe_str(j.get('title'))}' descartada: {reason}")

    print(f"[Eureca Scraper] {len(valid_jobs)} vagas válidas.")
    return valid_jobs
