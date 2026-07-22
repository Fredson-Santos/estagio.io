import httpx
import re
from datetime import datetime, timezone

from app.core.taxonomy import JobArea, JobModality

GUPY_API_URL = "https://employability-portal.gupy.io/api/v1/jobs"

async def fetch_gupy_jobs(query: str = "estágio", limit: int = 2000) -> list[dict]:
    """Busca vagas de estágio na Gupy usando a API pública (Portal)."""
    all_jobs = []
    chunk_size = 100
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for offset in range(0, limit, chunk_size):
            params = {
                "jobName": query,
                "limit": min(chunk_size, limit - offset),
                "offset": offset,
            }
            try:
                resp = await client.get(GUPY_API_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                jobs = data.get("data", [])
                
                if not jobs:
                    break
                    
                all_jobs.extend(jobs)
            except Exception as exc:
                print(f"Erro ao buscar vagas na Gupy no offset {offset}: {exc}")
                break
                
    return all_jobs

def _map_modality(workplace_type: str) -> JobModality:
    mapping = {
        "remote": JobModality.REMOTE,
        "hybrid": JobModality.HYBRID,
        "onsite": JobModality.ONSITE
    }
    return mapping.get(workplace_type.lower(), JobModality.ONSITE)

def _guess_area(title: str, description: str) -> JobArea:
    """Classificação determinística (sem LLM) básica para economizar custo."""
    text = f"{title} {description}".lower()
    if any(re.search(rf"\b{x}\b", text) for x in ["desenvolvedor", "software", "backend", "frontend", "ti", "tecnologia", "programador", "sistemas", "devops"]):
        return JobArea.TI_SOFTWARE
    if any(re.search(rf"\b{x}\b", text) for x in ["dados", "data analyst", "data science", "engenharia de dados"]):
        return JobArea.DADOS
    if any(re.search(rf"\b{x}\b", text) for x in ["design", "ux", "ui", "produto"]):
        return JobArea.DESIGN
    if any(re.search(rf"\b{x}\b", text) for x in ["marketing", "comunicação", "growth"]):
        return JobArea.MARKETING
    if any(re.search(rf"\b{x}\b", text) for x in ["rh", "recursos humanos", "recrutamento", "pessoas"]):
        return JobArea.RH
    if any(re.search(rf"\b{x}\b", text) for x in ["finanças", "contábil", "financeiro"]):
        return JobArea.FINANCAS
    if any(re.search(rf"\b{x}\b", text) for x in ["direito", "jurídico", "legal"]):
        return JobArea.DIREITO
    if any(re.search(rf"\b{x}\b", text) for x in ["administração", "negócios", "comercial", "vendas"]):
        return JobArea.NEGOCIOS
    return JobArea.OUTROS

def parse_gupy_job(raw_job: dict) -> dict:
    """Formata o JSON retornado pela Gupy para o formato do nosso banco de dados."""
    title = raw_job.get("name", "Vaga Gupy")
    company = raw_job.get("careerPageName", "Empresa Confidencial")
    
    city = raw_job.get("city") or ""
    state = raw_job.get("state") or ""
    location = f"{city}, {state}".strip(", ")
    
    modality = _map_modality(raw_job.get("workplaceType", ""))
    
    if modality == JobModality.REMOTE:
        location = "Remoto"
        
    description = raw_job.get("description", "").strip()
    
    # Extração de salário caso fornecido na API da Gupy
    salary = raw_job.get("salary") or raw_job.get("salaryRange") or None
    if isinstance(salary, dict):
        salary = salary.get("name") or salary.get("label") or str(salary)

    # URL da vaga no portal da Gupy
    source_url = raw_job.get("jobUrl", "")
    
    # Extrai o ID da URL se possível, ou usa o ID interno
    source_id = str(raw_job.get("id", ""))
    
    published_date_str = raw_job.get("publishedDate")
    posted_at = None
    if published_date_str:
        try:
            posted_at = datetime.fromisoformat(published_date_str.replace("Z", "+00:00"))
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
        "company_logo": raw_job.get("careerPageLogo"),
        "source_url": source_url,
        "source_id": source_id,
        "posted_at": posted_at,
    }

async def run_gupy_scraper(limit: int = 50) -> list[dict]:
    from app.services.job_validator import validate_job
    raw_jobs = await fetch_gupy_jobs(limit=limit)
    parsed_jobs = [parse_gupy_job(job) for job in raw_jobs]
    valid_jobs = []
    for j in parsed_jobs:
        is_valid, reason = validate_job(j)
        if is_valid:
            valid_jobs.append(j)
        else:
            print(f"[Gupy Scraper] Vaga '{j.get('title')}' descartada: {reason}")
    return valid_jobs

