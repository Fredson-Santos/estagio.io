import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime, timezone
import logging
from src.services.extractor import process_job_url
from src.config import settings
from estagio_shared.taxonomy import JobArea, JobModality

logger = logging.getLogger(__name__)

async def get_vagascom_urls() -> List[str]:
    """Exemplo real de extração de URLs (scraping HTML)."""
    urls = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://www.vagas.com.br/vagas-de-estagio", headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'lxml')
                for a in soup.find_all('a', class_='link-detalhes-vaga'):
                    urls.append("https://www.vagas.com.br" + a['href'])
    except Exception as e:
        logger.warning("Erro ao buscar URLs do Vagas.com: %s", e)
    return urls[:2] # Limita a 2 para não estourar API do LLM

async def get_superestagios_urls() -> List[str]:
    """Extrator de URLs do Super Estágios."""
    urls = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://www.superestagios.com.br/index/", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'lxml')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'processoSeletivo/processo.php' in href:
                        urls.append("https://www.superestagios.com.br/index/" + href.replace('../', ''))
    except httpx.ConnectError as e:
        logger.warning("SSL/ conexão falhou no SuperEstagios (provável cert auto-assinado): %s", e)
    except Exception as e:
        logger.warning("Erro ao buscar URLs do Super Estagios: %s", e)
    return list(set(urls))[:2]

async def scrape_secondary_platforms() -> Dict[str, List[Dict]]:
    """Orquestra a busca de vagas em plataformas secundárias de forma real."""
    results = {
        "Vagas.com.br": [],
        "SuperEstagios": []
    }
    
    # Verifica chave da API
    has_llm_key = bool(
        settings.GROQ_API_KEY or settings.OPENAI_API_KEY or settings.GEMINI_API_KEY
    )
    if has_llm_key:
        logger.info("Chave de API detectada. Iniciando LLM Extraction...")

        # 1. Vagas.com.br
        vagascom_urls = await get_vagascom_urls()
        for url in vagascom_urls:
            try:
                job_data = await process_job_url(url)
                if isinstance(job_data.get("area"), str):
                    job_data["area"] = JobArea(job_data["area"])
                if isinstance(job_data.get("modality"), str):
                    job_data["modality"] = JobModality(job_data["modality"])
                job_data["source_id"] = url.split('/')[-2] if '/v' in url else url
                job_data["posted_at"] = datetime.now(timezone.utc)
                results["Vagas.com.br"].append(job_data)
            except Exception as e:
                logger.warning("Falha LLM Vagas.com: %s -> %s", url, e)

        # 2. Super Estágios
        super_urls = await get_superestagios_urls()
        for url in super_urls:
            try:
                job_data = await process_job_url(url)
                if isinstance(job_data.get("area"), str):
                    job_data["area"] = JobArea(job_data["area"])
                if isinstance(job_data.get("modality"), str):
                    job_data["modality"] = JobModality(job_data["modality"])
                job_data["source_id"] = url.split('=')[-1] if '=' in url else url
                job_data["posted_at"] = datetime.now(timezone.utc)
                results["SuperEstagios"].append(job_data)
            except Exception as e:
                logger.warning("Falha LLM SuperEstagios: %s -> %s", url, e)
    else:
        logger.info("Sem chave de API LLM. Ignorando scrapers híbridos.")

    return results
