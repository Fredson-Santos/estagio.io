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
    """Formata o JSON retornado pela Gupy para o formato completo do nosso banco de dados."""
    title = raw_job.get("name", "Vaga Gupy")
    company = raw_job.get("careerPageName", "Empresa Confidencial")
    
    city = raw_job.get("city") or ""
    state = raw_job.get("state") or ""
    location = f"{city}, {state}".strip(", ")
    
    modality = _map_modality(raw_job.get("workplaceType", ""))
    
    if modality == JobModality.REMOTE:
        location = "Remoto"
        
    description = raw_job.get("description", "").strip()
    
    # Extração de salário
    from src.services.job_validator import parse_salary, parse_salary_cents, parse_duration_months
    raw_salary_obj = raw_job.get("salary") or raw_job.get("salaryRange")
    salary = parse_salary(raw_salary_obj)
    salary_min_cents, salary_max_cents = parse_salary_cents(raw_salary_obj or salary)

    # URL da vaga no portal da Gupy
    source_url = raw_job.get("jobUrl", "")
    source_id = str(raw_job.get("id", ""))
    
    published_date_str = raw_job.get("publishedDate")
    posted_at = None
    if published_date_str:
        try:
            posted_at = datetime.fromisoformat(published_date_str.replace("Z", "+00:00"))
        except ValueError:
            pass

    deadline_str = raw_job.get("applicationDeadline")
    deadline = None
    if deadline_str:
        try:
            deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
        except ValueError:
            pass

    # Skills e pré-requisitos
    skills = raw_job.get("skills", [])
    skills_names = [s.get("name") for s in skills if isinstance(s, dict) and s.get("name")]
    requirements = ", ".join(skills_names) if skills_names else None

    # PCD
    badges = raw_job.get("badges", {})
    is_pcd = bool(raw_job.get("disabilities")) or bool(badges.get("isPWD"))

    # Tipo de contrato & duração
    raw_type = raw_job.get("type", "")
    contract_type = "Estágio" if "intern" in raw_type.lower() or "estagio" in raw_type.lower() else (raw_type or "Estágio")
    duration_months = parse_duration_months(f"{title} {description}")

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
        "company_logo":     trunc(raw_job.get("careerPageLogo"), 1000),
        "source_url":       trunc(source_url, 1000),
        "source_id":        trunc(source_id, 255),
        "posted_at":        posted_at,
        "benefits":         None,
        "requirements":     trunc(requirements, 2000),
        "deadline":         deadline,
        "is_pcd":           is_pcd,
        "contract_type":    trunc(contract_type, 50),
        "duration_months":  duration_months,
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

async def run_gupy_scraper(limit: int = 500) -> list[dict]:
    import asyncio
    from src.services.job_validator import validate_job, safe_str
    raw_jobs = await fetch_gupy_jobs(limit=limit)
    parsed_jobs = [parse_gupy_job(job) for job in raw_jobs]
    
    # 1. Filtra preliminarmente apenas chaves básicas para enriquecimento
    candidates = [
        j for j in parsed_jobs 
        if j.get("title") and j.get("company") and j.get("source_url")
    ]

    # 2. Enriquece concorrentemente com a descrição completa do HTML nativo da Gupy
    if candidates:
        print(f"[Gupy Scraper] Buscando HTML nativo de {len(candidates)} vagas...")
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            tasks = [_enrich_job_html(client, j) for j in candidates]
            candidates = await asyncio.gather(*tasks)

    # 3. Valida a qualidade final das vagas com a descrição preenchida
    valid_jobs = []
    for j in candidates:
        is_valid, reason = validate_job(j)
        if is_valid:
            valid_jobs.append(j)
        else:
            print(f"[Gupy Scraper] Vaga '{safe_str(j.get('title'))}' descartada: {reason}")

    return valid_jobs


GUPY_COMPANIES_URL = "https://employability-portal.gupy.io/api/v1/jobs/companies"

async def fetch_gupy_companies(query: str = "estagio", limit: int = 1000) -> list[dict]:
    """Busca empresas com vagas de estágio na Gupy."""
    params = {"jobName": query, "limit": limit, "sortBy": "company", "sortOrder": "asc"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(GUPY_COMPANIES_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])
        except Exception as exc:
            print(f"[Gupy Companies] Erro ao buscar empresas: {exc}")
            return []


GUPY_VAGAJA_API_URL = "https://candidato-ja.api.gupy.io/api/public/jobs"

async def fetch_gupy_vagaja_jobs(limit: int = 500) -> list[dict]:
    """Busca vagas no Gupy Vaga-Já (candidato-ja.api.gupy.io)."""
    all_jobs: list[dict] = []
    page = 1
    chunk_size = 50

    async with httpx.AsyncClient(timeout=15.0) as client:
        while len(all_jobs) < limit:
            params = {"page": page, "limit": chunk_size, "sort": "recent"}
            try:
                resp = await client.get(GUPY_VAGAJA_API_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                items = data.get("data", [])
                total_pages = data.get("totalPages", 1)
                if not items:
                    break
                all_jobs.extend(items)
                if page >= total_pages:
                    break
                page += 1
            except Exception as exc:
                print(f"[Gupy Vaga-Já] Erro na página {page}: {exc}")
                break

    return all_jobs[:limit]


def _is_internship_vagaja(title: str, desc: str, ws_name: str) -> bool:
    t = (title or "").lower()
    d = (desc or "").lower()
    w = (ws_name or "").lower()
    return (
        "estágio" in t or "estagio" in t or
        "estágio" in d or "estagio" in d or
        "estág" in w or "estag" in w
    )


def parse_gupy_vagaja_job(raw_item: dict) -> dict | None:
    """Converte uma vaga do Gupy Vaga-Já para o formato ScrapedJob.

    Retorna None se não for vaga de estágio.
    """
    title = raw_item.get("title") or "Vaga Gupy Vaga-Já"
    desc = (raw_item.get("description") or raw_item.get("summary") or "").strip()
    ws = raw_item.get("workScale", {})
    ws_name = ""
    if isinstance(ws, dict):
        ws_name = ws.get("name") or ws.get("description") or ""

    if not _is_internship_vagaja(title, desc, ws_name):
        return None

    v_id = str(raw_item.get("id", ""))
    company_obj = raw_item.get("company", {})
    if not isinstance(company_obj, dict):
        company_obj = {}
    company = company_obj.get("name") or company_obj.get("corporateName") or "Empresa Vaga-Já"
    logo = company_obj.get("logoUrl")

    addr = raw_item.get("companyAddress", {})
    if not isinstance(addr, dict):
        addr = {}
    city = addr.get("city") or ""
    state = addr.get("state") or ""

    avail = (raw_item.get("availability") or "").upper()
    if avail == "REMOTE" or "remot" in desc.lower():
        modality = JobModality.REMOTE
    elif avail == "ONSITE" or "presencial" in desc.lower():
        modality = JobModality.ONSITE
    else:
        modality = JobModality.HYBRID

    location = f"{city}, {state}".strip(", ") if city else "Não informado"
    if modality == JobModality.REMOTE:
        location = "Remoto"

    from src.services.job_validator import parse_salary, parse_salary_cents, parse_duration_months
    sal_min = raw_item.get("salaryMin")
    sal_display = raw_item.get("salaryDisplay") or (f"R$ {sal_min}" if sal_min else None)
    salary = parse_salary(sal_display)
    salary_min_cents, salary_max_cents = parse_salary_cents(sal_display or salary)
    if sal_min and not salary_min_cents:
        salary_min_cents = int(sal_min * 100)
        if not salary:
            salary = f"R$ {sal_min:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

    source_url = (
        raw_item.get("publicShortUrl")
        or raw_item.get("whatsappShortUrl")
        or f"https://web.vaga-ja.com/{raw_item.get('shortId') or v_id}"
    )

    is_pcd = "pcd" in title.lower() or "pcd" in desc.lower()
    published_at_str = raw_item.get("publishedAt")
    posted_at = None
    if published_at_str:
        try:
            posted_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
        except ValueError:
            pass

    deadline_str = raw_item.get("expirationDate")
    deadline = None
    if deadline_str:
        try:
            deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
        except ValueError:
            pass

    duration_months = parse_duration_months(f"{title} {desc}")
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
        "source_url": trunc(source_url, 1000),
        "source_id": trunc(v_id, 255),
        "posted_at": posted_at,
        "benefits": None,
        "requirements": None,
        "deadline": deadline,
        "is_pcd": is_pcd,
        "contract_type": trunc("Estágio", 50),
        "duration_months": duration_months,
    }


async def run_gupy_vagaja_scraper(limit: int = 500) -> list[dict]:
    """Pipeline completo do Gupy Vaga-Já: fetch + parse + validate."""
    from src.services.job_validator import validate_job, safe_str

    raw_jobs = await fetch_gupy_vagaja_jobs(limit=limit)
    logger_msg = f"[Gupy Vaga-Já] {len(raw_jobs)} vagas brutas recebidas."
    print(logger_msg)

    valid_jobs: list[dict] = []
    for raw in raw_jobs:
        parsed = parse_gupy_vagaja_job(raw)
        if parsed is None:
            continue
        is_valid, reason = validate_job(parsed)
        if is_valid:
            valid_jobs.append(parsed)
        else:
            print(f"[Gupy Vaga-Já] Vaga '{safe_str(parsed.get('title'))}' descartada: {reason}")

    print(f"[Gupy Vaga-Já] {len(valid_jobs)} vagas válidas.")
    return valid_jobs
