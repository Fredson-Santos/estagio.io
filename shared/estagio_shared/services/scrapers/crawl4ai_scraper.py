"""
crawl4ai_scraper.py — Servico de scraping utilizando Crawl4AI
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from estagio_shared.taxonomy import JobArea, JobModality

try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    AsyncWebCrawler = None
    CRAWL4AI_AVAILABLE = False


def _guess_area(title: str, description: str) -> JobArea:
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


def _guess_modality(text: str) -> JobModality:
    text_lower = text.lower()
    if "remoto" in text_lower or "home office" in text_lower or "remote" in text_lower:
        return JobModality.REMOTE
    if "híbrido" in text_lower or "hibrido" in text_lower or "hybrid" in text_lower:
        return JobModality.HYBRID
    return JobModality.ONSITE


def parse_crawl4ai_markdown(url: str, markdown: str) -> dict[str, Any]:
    """Parse basico do markdown extraido pelo Crawl4AI para extrair informacoes estruturadas."""
    lines = [line.strip() for line in markdown.splitlines() if line.strip()]
    
    title = "Estágio"
    for line in lines:
        if line.startswith("#"):
            title = line.lstrip("# ").strip()
            break
        elif "estágio" in line.lower() or "vaga" in line.lower() or "desenvolvedor" in line.lower():
            title = line.strip()
            break

    netloc = urlparse(url).netloc
    company = netloc.replace("www.", "").split(".")[0].capitalize() if netloc else "Empresa Desconhecida"
    
    modality = _guess_modality(markdown)
    location = "Remoto" if modality == JobModality.REMOTE else "Não informado"
    area = _guess_area(title, markdown)
    
    # Limita tamanho da descricao
    description = markdown[:4000] if len(markdown) > 4000 else markdown
    
    return {
        "title": title,
        "company": company,
        "location": location,
        "modality": modality,
        "area": area,
        "description": description,
        "salary": None,
        "company_logo": None,
        "source_url": url,
        "source_id": url.split("/")[-1] or url,
        "posted_at": datetime.now(timezone.utc),
    }


async def run_crawl4ai_scraper(urls: list[str]) -> list[dict[str, Any]]:
    """Raspagem em lote usando AsyncWebCrawler do Crawl4AI."""
    results: list[dict[str, Any]] = []
    
    if not CRAWL4AI_AVAILABLE:
        print("[crawl4ai_scraper] Módulo crawl4ai não está instalado. Usando fallback estático...")
        return results

    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            for url in urls:
                res = await crawler.arun(url=url)
                if res and getattr(res, "success", False) and getattr(res, "markdown", None):
                    parsed_job = parse_crawl4ai_markdown(url, str(res.markdown))
                    results.append(parsed_job)
                else:
                    print(f"[crawl4ai_scraper] Falha ao raspar URL: {url}")
    except Exception as exc:
        print(f"[crawl4ai_scraper] Erro durante raspagem com Crawl4AI: {exc}")

    return results
