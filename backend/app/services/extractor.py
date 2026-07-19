import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from openai import AsyncOpenAI

from app.core.taxonomy import JobArea, JobModality
from app.services.scrapers.rules_manager import load_rules, save_rules

SYSTEM_PROMPT = """\
Você é um assistente especializado em extrair informações de vagas de emprego.
Dado o código HTML simplificado de uma página de vaga, retorne SOMENTE um objeto JSON válido
com exatamente as duas chaves abaixo: 'job_data' (os dados extraídos) e 'selectors' (os seletores CSS que você encontrou e usou para extrair aqueles dados).

{
  "job_data": {
    "title": "título/cargo da vaga",
    "company": "nome da empresa",
    "location": "cidade, estado (ou null se for remoto)",
    "modality": "um dos valores exatos: 'REMOTE', 'HYBRID', 'ONSITE'. Se não informado, deduzir pelo texto ou usar 'ONSITE' como padrão",
    "area": "um dos valores exatos da taxonomia: 'TI_SOFTWARE', 'DADOS', 'DESIGN', 'MARKETING', 'NEGOCIOS', 'RH', 'FINANCAS', 'ENGENHARIA_OUTRAS', 'DIREITO', 'OUTROS'",
    "description": "resumo limpo da descrição da vaga (max 500 caracteres)"
  },
  "selectors": {
    "title": "seletor css para o titulo (ex: h1.job-title)",
    "company": "seletor css para a empresa (ex: .company-name)",
    "location": "seletor css para localizacao",
    "description": "seletor css para a descricao"
  }
}

Se algum campo não puder ser determinado, use "Não informado" ou null.
Para os seletores, tente usar classes (ex: `.vaga-titulo`) que parecem estáveis, evitando IDs ou caminhos muito complexos que podem quebrar. Se não achar seletor para algum campo, passe null no selector.
Retorne APENAS o JSON, sem nenhum texto adicional.
"""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
}

MAX_HTML_CHARS = 12000

def _get_llm_client() -> tuple[AsyncOpenAI, str]:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "")
    
    # Suporte para GROQ (Usa API compatível com OpenAI)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        return AsyncOpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        ), model or "llama-3.1-8b-instant"

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("Chave de API não definida. Configure GROQ_API_KEY ou OPENAI_API_KEY no .env")

    if provider == "gemini":
        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        ), model or "gemini-1.5-flash"
    
    # default to openai
    return AsyncOpenAI(api_key=api_key), model or "gpt-4o-mini"

async def scrape_page_html(url: str) -> BeautifulSoup:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Erro HTTP ao acessar a URL: {exc}") from exc

    return BeautifulSoup(resp.text, "lxml")

def clean_html_for_llm(soup: BeautifulSoup) -> str:
    """Limpa o HTML mantendo as classes e a estrutura para o LLM achar os seletores CSS."""
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe", "svg", "img"]):
        tag.decompose()
        
    # Pega apenas o body se existir
    content = str(soup.body) if soup.body else str(soup)
    # Remove atributos excessivos que não ajudam com CSS selectors (ex: data-*, aria-*, style)
    content = re.sub(r'\s+(data-[a-zA-Z0-9\-]+|aria-[a-zA-Z0-9\-]+|style|width|height)="[^"]*"', '', content)
    
    if len(content) > MAX_HTML_CHARS:
        content = content[:MAX_HTML_CHARS] + "\n\n<!-- truncado -->"
    return content

def extract_via_rules(soup: BeautifulSoup, rules: dict) -> dict:
    """Tenta extrair os dados da vaga usando regras CSS cacheadas."""
    job_data = {}
    
    title_el = soup.select_one(rules.get("title", "")) if rules.get("title") else None
    if not title_el:
        return None # Falhou, Título é obrigatório
        
    company_el = soup.select_one(rules.get("company", "")) if rules.get("company") else None
    location_el = soup.select_one(rules.get("location", "")) if rules.get("location") else None
    desc_el = soup.select_one(rules.get("description", "")) if rules.get("description") else None
    
    # Formatação limpa
    job_data["title"] = title_el.get_text(strip=True)
    job_data["company"] = company_el.get_text(strip=True) if company_el else "Não informado"
    job_data["location"] = location_el.get_text(strip=True) if location_el else "Não informado"
    job_data["description"] = desc_el.get_text(strip=True)[:500] if desc_el else ""
    
    # Se conseguiu o básico, tenta inferir a área e modalidade localmente via regex (como fizemos na Gupy)
    from app.services.scrapers.gupy import _guess_area, _map_modality
    job_data["area"] = _guess_area(job_data["title"], job_data["description"])
    
    # Tenta descobrir modalidade lendo localizacao e titulo
    texto_modalidade = f"{job_data['location']} {job_data['title']} {job_data['description']}".lower()
    if "remoto" in texto_modalidade or "home office" in texto_modalidade:
        job_data["modality"] = JobModality.REMOTE
    elif "híbrido" in texto_modalidade or "hybrid" in texto_modalidade:
        job_data["modality"] = JobModality.HYBRID
    else:
        job_data["modality"] = JobModality.ONSITE
        
    return job_data

async def process_job_url(url: str) -> dict:
    """Função de alto nível para buscar e processar uma vaga Hibridamente."""
    url = url.strip()
    domain = urlparse(url).netloc
    
    print(f"[{domain}] Acessando URL da vaga...")
    soup = await scrape_page_html(url)
    
    # 1. Tentativa Rápida via Cache (BeautifulSoup)
    rules = load_rules(domain)
    if rules:
        print(f"[{domain}] Regras de CSS encontradas em cache. Tentando extração rápida...")
        job_data = extract_via_rules(soup, rules)
        if job_data:
            print(f"[{domain}] Sucesso na extração rápida!")
            job_data["source_url"] = url
            return job_data
        else:
            print(f"[{domain}] Regras falharam (site mudou). Fazendo fallback para LLM...")
    else:
        print(f"[{domain}] Sem regras salvas. Usando LLM para extrair e gerar regras...")

    # 2. Fallback via LLM (Auto-Healing)
    client, model = _get_llm_client()
    clean_html = clean_html_for_llm(soup)
    
    user_message = (
        f"URL da vaga: {url}\n\n"
        f"--- CONTEÚDO HTML (SIMPLIFICADO) ---\n{clean_html}"
    )
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
    except Exception as exc:
        raise RuntimeError(f"Erro na API da LLM: {exc}")

    raw = response.choices[0].message.content.strip()
    
    try:
        data = json.loads(raw)
        job_data = data.get("job_data", {})
        selectors = data.get("selectors", {})
        
        if selectors and job_data.get("title") and job_data.get("title") != "Não informado":
            print(f"[{domain}] LLM extraiu com sucesso e gerou novos seletores. Salvando regras...")
            save_rules(domain, selectors)
            
        job_data["source_url"] = url
        return job_data
    except json.JSONDecodeError:
        raise ValueError(f"LLM retornou resposta inválida:\n{raw[:500]}")
