import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from openai import AsyncOpenAI

from app.core.taxonomy import JobArea, JobModality

SYSTEM_PROMPT = """\
Você é um assistente especializado em extrair informações de vagas de emprego.
Dado um texto bruto de uma página de vaga, retorne SOMENTE um objeto JSON válido
(sem markdown, sem explicações) com exatamente os seguintes campos:

{
  "title": "título/cargo da vaga",
  "company": "nome da empresa",
  "location": "cidade, estado (ou null se for remoto)",
  "modality": "um dos valores exatos: 'REMOTE', 'HYBRID', 'ONSITE'. Se não informado, deduzir pelo texto ou usar 'ONSITE' como padrão",
  "area": "um dos valores exatos da taxonomia: 'TI_SOFTWARE', 'DADOS', 'DESIGN', 'MARKETING', 'NEGOCIOS', 'RH', 'FINANCAS', 'ENGENHARIA_OUTRAS', 'DIREITO', 'OUTROS'",
  "description": "resumo limpo da descrição da vaga (max 500 caracteres)"
}

Retorne APENAS o JSON, sem nenhum texto adicional.
"""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
}

MAX_TEXT_CHARS = 6000

def _get_llm_client() -> tuple[AsyncOpenAI, str]:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não definida")
        return AsyncOpenAI(api_key=api_key), model or "gpt-4o-mini"

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não definida")
        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        ), model or "gemini-1.5-flash"

    raise ValueError(f"Provedor desconhecido: '{provider}'.")

async def scrape_page(url: str) -> str:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Erro HTTP ao acessar a URL: {exc}") from exc

    soup = BeautifulSoup(resp.text, "lxml")
    parts = []

    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe", "svg"]):
        tag.decompose()
        
    body_text = re.sub(r"\n{3,}", "\n\n", soup.get_text(separator="\n", strip=True))
    if body_text:
        parts.append("[Conteúdo da Página]\n" + body_text)

    full_text = "\n\n".join(parts)
    if len(full_text) > MAX_TEXT_CHARS:
        full_text = full_text[:MAX_TEXT_CHARS] + "\n\n[... conteúdo truncado ...]"
    return full_text

async def extract_with_llm(scraped_text: str, url: str) -> dict:
    client, model = _get_llm_client()
    
    user_message = (
        f"URL da vaga: {url}\n\n"
        f"--- CONTEÚDO RASPADO ---\n{scraped_text}"
    )
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
    except Exception as exc:
        raise RuntimeError(f"Erro na API da LLM: {exc}")

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE | re.MULTILINE)
    raw = re.sub(r"\s*```\s*$", "", raw, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"LLM retornou resposta inválida:\n{raw[:500]}")

async def process_job_url(url: str) -> dict:
    """Função de alto nível para buscar e processar uma vaga via LLM"""
    url = url.strip()
    text = await scrape_page(url)
    return await extract_with_llm(text, url)
