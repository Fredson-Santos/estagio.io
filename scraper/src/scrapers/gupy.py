import httpx
import re
from datetime import datetime, timezone

from estagio_shared.taxonomy import JobArea, JobModality
from src.services.job_validator import trunc

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
    """
    Classificação determinística precisa (Title-First & Multi-Stage).
    Prioriza o Título para evitar que palavras soltas na descrição causem falsos positivos.
    Identifica vagas de programas de estágio com múltiplas áreas.
    """
    title_lower = (title or "").lower()
    desc_lower = (description or "").lower()

    # 0. Checagem de Programa de Estágio (Multi-Áreas)
    program_keywords = [
        "programa de estágio", "programa de estagio", "estágio corporativo", "estagio corporativo",
        "diversas áreas", "diversas areas", "várias áreas", "varias areas", "banco de talentos",
        "estágio generalista", "estagio generalista", "multi-áreas", "multi-areas"
    ]
    if any(k in title_lower for k in program_keywords):
        return JobArea.PROGRAMA_ESTAGIO

    if "programa" in title_lower or "estágio" in title_lower or "estagio" in title_lower:
        matched_areas = 0
        if re.search(r"\b(marketing|comunicação)\b", desc_lower): matched_areas += 1
        if re.search(r"\b(ti|tecnologia|desenvolvimento|software)\b", desc_lower): matched_areas += 1
        if re.search(r"\b(administração|negócios|comercial)\b", desc_lower): matched_areas += 1
        if re.search(r"\b(finanças|financeiro|contábil)\b", desc_lower): matched_areas += 1
        if re.search(r"\b(rh|recursos humanos)\b", desc_lower): matched_areas += 1
        if re.search(r"\b(engenharia)\b", desc_lower): matched_areas += 1

        if matched_areas >= 3:
            return JobArea.PROGRAMA_ESTAGIO

    # 1. FASE 1: TITLE-FIRST MATCHING (Prioridade Absoluta ao Título)
    title_rules = [
        (JobArea.TI_SOFTWARE, [r"\b(desenvolvedor|dev|software|backend|frontend|fullstack|programador|sistemas|devops|web|mobile|qa|tester|infraestrutura)\b", r"\b(ti|tecnologia)\b"]),
        (JobArea.DADOS, [r"\b(dados|data analyst|data science|bi|business intelligence|data engineer|engenharia de dados)\b"]),
        (JobArea.DESIGN, [r"\b(design|designer|ux|ui|product design|arte|criativo)\b"]),
        (JobArea.MARKETING, [r"\b(marketing|mkt|seo|sem|growth|mídias sociais|social media|copywriter|branding)\b"]),
        (JobArea.RH, [r"\b(rh|recursos humanos|recrutamento|seleção|people|talent|gestão de pessoas)\b"]),
        (JobArea.FINANCAS, [r"\b(finanças|financeiro|contabilidade|contábil|auditoria|tributário|tesouraria|fiscal)\b"]),
        (JobArea.DIREITO, [r"\b(direito|jurídico|legal|advocacia|compliance)\b"]),
        (JobArea.ENGENHARIA_OUTRAS, [r"\b(engenharia|engenheiro|eng|produção|mecânica|elétrica|civil|química)\b"]),
        (JobArea.NEGOCIOS, [r"\b(administração|adm|negócios|comercial|vendas|sales|operações|inside sales|gestão)\b"]),
    ]

    for area, patterns in title_rules:
        if any(re.search(pat, title_lower) for pat in patterns):
            return area

    # 2. FASE 2: DESCRIPTION CONTEXTUAL MATCHING (Apenas para Títulos Genéricos)
    desc_rules = [
        (JobArea.TI_SOFTWARE, [r"\b(atuará com desenvolvimento|programação em|stack tecnológica|desenvolvimento de software|código clean|banco de dados relacional|desenvolvedor)\b"]),
        (JobArea.DADOS, [r"\b(análise de dados|ciência de dados|modelos de dados|dashboards em power bi|sql avançado|pipeline de dados)\b"]),
        (JobArea.DESIGN, [r"\b(criação de wireframes|prototipagem|figma|design de interface|experiência do usuário)\b"]),
        (JobArea.MARKETING, [r"\b(área de marketing|estratégias de marketing|campanhas de marketing|redes sociais e inbound|gestão de tráfego)\b"]),
        (JobArea.RH, [r"\b(área de recursos humanos|processos seletivos|atividades de rh|admissão e integração|clima organizacional)\b"]),
        (JobArea.FINANCAS, [r"\b(área financeira|contas a pagar|contas a receber|conciliação bancária|demonstrativos contábeis)\b"]),
        (JobArea.DIREITO, [r"\b(área jurídica|elaboração de contratos|processos judiciais|consultoria jurídica)\b"]),
        (JobArea.ENGENHARIA_OUTRAS, [r"\b(área de engenharia|processos produtivos|linhas de produção|projetos de engenharia)\b"]),
        (JobArea.NEGOCIOS, [r"\b(área comercial|prospecção de clientes|processos administrativos|suporte à gestão|vendas b2b)\b"]),
    ]

    for area, patterns in desc_rules:
        if any(re.search(pat, desc_lower) for pat in patterns):
            return area

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
    from src.services.job_validator import parse_salary
    salary = parse_salary(raw_job.get("salary") or raw_job.get("salaryRange"))

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
        "title":       trunc(title, 255),
        "company":     trunc(company, 255),
        "location":    trunc(location, 255),
        "modality":    modality,
        "area":        _guess_area(title, description),
        "description": description[:4000] if len(description) > 4000 else description,
        "salary":      trunc(salary, 255),
        "company_logo": trunc(raw_job.get("careerPageLogo"), 1000),
        "source_url":  trunc(source_url, 1000),
        "source_id":   trunc(source_id, 255),
        "posted_at":   posted_at,
    }

async def _enrich_job_html(client: httpx.AsyncClient, job: dict) -> dict:
    url = job.get("source_url")
    if not url or not url.startswith("http"):
        return job
    try:
        resp = await client.get(url, timeout=10.0)
        if resp.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            sections = soup.find_all("div", {"data-testid": "text-section"})
            if sections:
                job["description"] = "\n".join([str(s) for s in sections])
    except Exception:
        pass
    return job

async def run_gupy_scraper(limit: int = 50) -> list[dict]:
    import asyncio
    from src.services.job_validator import validate_job, safe_str
    raw_jobs = await fetch_gupy_jobs(limit=limit)
    parsed_jobs = [parse_gupy_job(job) for job in raw_jobs]
    valid_jobs = []
    for j in parsed_jobs:
        is_valid, reason = validate_job(j)
        if is_valid:
            valid_jobs.append(j)
        else:
            print(f"[Gupy Scraper] Vaga '{safe_str(j.get('title'))}' descartada: {reason}")

    # Enriquece concorrentemente as vagas válidas com o HTML nativo das páginas da Gupy
    if valid_jobs:
        print(f"[Gupy Scraper] Buscando HTML nativo de {len(valid_jobs)} vagas...")
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            tasks = [_enrich_job_html(client, j) for j in valid_jobs]
            valid_jobs = await asyncio.gather(*tasks)

    return valid_jobs
