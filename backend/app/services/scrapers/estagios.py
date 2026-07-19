import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import os
from datetime import datetime, timezone
from app.services.extractor import process_job_url
from app.core.taxonomy import JobArea, JobModality

async def get_ciee_mock() -> List[Dict]:
    return [{
        "title": "Estágio em Administração (Mock)",
        "company": "CIEE Parceiros",
        "location": "Curitiba, PR",
        "modality": JobModality.ONSITE,
        "area": JobArea.NEGOCIOS,
        "description": "Auxiliar nas rotinas administrativas e atendimento ao público.",
        "source_url": "https://portal.ciee.org.br/vagas/123",
        "source_id": "ciee-123",
        "posted_at": datetime.now(timezone.utc)
    }]

async def get_nube_mock() -> List[Dict]:
    return [{
        "title": "Estágio de Front-End (Mock)",
        "company": "Startup Nube",
        "location": "Remoto",
        "modality": JobModality.REMOTE,
        "area": JobArea.TI_SOFTWARE,
        "description": "Vaga para desenvolvedor front-end estágio usando React e Tailwind.",
        "source_url": "https://www.nube.com.br/vagas/456",
        "source_id": "nube-456",
        "posted_at": datetime.now(timezone.utc)
    }]

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
        print(f"Erro ao buscar URLs do Vagas.com: {e}")
    return urls[:2] # Limita a 2 para não estourar API do LLM

async def scrape_secondary_platforms() -> Dict[str, List[Dict]]:
    """Orquestra a busca de vagas em plataformas secundárias."""
    results = {
        "CIEE": await get_ciee_mock(),
        "Nube": await get_nube_mock(),
        "Vagas.com.br": []
    }
    
    # Exemplo de fluxo real via LLM para Vagas.com.br
    has_llm_key = bool(os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"))
    if has_llm_key:
        print("Chave de API detectada. Iniciando LLM Extraction para Vagas.com.br...")
        vagascom_urls = await get_vagascom_urls()
        for url in vagascom_urls:
            try:
                job_data = await process_job_url(url)
                # Garantindo conversão das enums caso o LLM retorne string plana
                if isinstance(job_data.get("area"), str):
                    job_data["area"] = JobArea(job_data["area"])
                if isinstance(job_data.get("modality"), str):
                    job_data["modality"] = JobModality(job_data["modality"])
                    
                job_data["source_id"] = url.split('/')[-2] if '/v' in url else url
                job_data["posted_at"] = datetime.now(timezone.utc)
                results["Vagas.com.br"].append(job_data)
            except Exception as e:
                print(f"Falha ao processar URL com LLM: {url} -> {e}")
    else:
        print("Sem chave de API LLM. Inserindo mock para Vagas.com.br...")
        results["Vagas.com.br"].append({
            "title": "Estágio em TI (Mock LLM Offline)",
            "company": "Empresa Vagas.com",
            "location": "São Paulo, SP",
            "modality": JobModality.HYBRID,
            "area": JobArea.TI_SOFTWARE,
            "description": "Vaga simulada devido a falta de chave de API LLM.",
            "source_url": "https://www.vagas.com.br/vagas/v12345/mock",
            "source_id": "v12345",
            "posted_at": datetime.now(timezone.utc)
        })

    return results
