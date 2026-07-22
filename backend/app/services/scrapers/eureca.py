import httpx
from datetime import datetime
from bs4 import BeautifulSoup

from app.core.taxonomy import JobArea, JobModality
from app.services.scrapers.gupy import _guess_area

EURECA_API_URL = "https://candidate-api.eureca.me/v2/opportunities"

async def fetch_eureca_jobs(limit: int = 200) -> list[dict]:
    """Busca vagas na Eureca usando a API."""
    all_jobs = []
    chunk_size = 10
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        page = 1
        while True:
            params = {
                "pageSize": chunk_size,
                "page": page,
            }
            try:
                resp = await client.get(EURECA_API_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                jobs = data.get("items", [])
                
                if not jobs:
                    break
                    
                all_jobs.extend(jobs)
                
                if len(jobs) < chunk_size or len(all_jobs) >= limit:
                    break
                    
                page += 1
            except Exception as exc:
                print(f"Erro ao buscar vagas na Eureca na página {page}: {exc}")
                break
                
    return all_jobs[:limit]

def _map_modality(work_model: str) -> JobModality:
    mapping = {
        "remoto": JobModality.REMOTE,
        "hibrido": JobModality.HYBRID,
        "presencial": JobModality.ONSITE
    }
    if not work_model:
        return JobModality.ONSITE
    return mapping.get(work_model.lower(), JobModality.ONSITE)

def parse_eureca_job(raw_job: dict) -> dict:
    """Formata o JSON retornado pela Eureca para o formato do nosso banco de dados."""
    title = raw_job.get("name", "Vaga Eureca")
    company = raw_job.get("companyName", "Empresa Confidencial")
    
    locations = raw_job.get("locations", {})
    cities = locations.get("cities", [])
    states = locations.get("states", [])
    
    city_str = ", ".join(cities) if cities else ""
    state_str = ", ".join(states) if states else ""
    location = f"{city_str} - {state_str}".strip(" -")
    if not location:
        location = "Não informado"
        
    modality = _map_modality(raw_job.get("workModel", ""))
    if modality == JobModality.REMOTE:
        location = "Remoto"
        
    raw_description = raw_job.get("description", "")
    description = raw_description.strip() if raw_description else ""
        
    # Extração de bolsa auxílio / remuneração da Eureca caso presente
    from app.services.job_validator import parse_salary
    salary = parse_salary(raw_job.get("stipend") or raw_job.get("salary") or raw_job.get("remuneration"))

    # URL da vaga na Eureca
    source_url = f"https://oportunidades.eureca.me/oportunidade/{raw_job.get('id', '')}"
    
    source_id = str(raw_job.get("id", ""))
    
    created_at_str = raw_job.get("createdAt")
    posted_at = None
    if created_at_str:
        try:
            # createdAt ex: "2026-06-28 21:29:05.143498+00"
            posted_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00").replace("+00", "+00:00"))
        except ValueError:
            pass
            
    return {
        "title": title,
        "company": company,
        "location": location,
        "modality": modality,
        "area": _guess_area(title, description),
        "description": description[:4000] if len(description) > 4000 else description,
        "salary": salary,
        "company_logo": raw_job.get("companyLogoUrl"),
        "source_url": source_url,
        "source_id": source_id,
        "posted_at": posted_at,
    }

async def run_eureca_scraper(limit: int = 50) -> list[dict]:
    from app.services.job_validator import validate_job, safe_str
    raw_jobs = await fetch_eureca_jobs(limit=limit)
    parsed_jobs = [parse_eureca_job(job) for job in raw_jobs]
    valid_jobs = []
    for j in parsed_jobs:
        is_valid, reason = validate_job(j)
        if is_valid:
            valid_jobs.append(j)
        else:
            print(f"[Eureca Scraper] Vaga '{safe_str(j.get('title'))}' descartada: {reason}")
    return valid_jobs

