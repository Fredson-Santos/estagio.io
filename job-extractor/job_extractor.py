"""
job_extractor.py — Core do extrator de vagas
Usado como módulo pela api.py.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("❌  Instale as dependências: pip install -r requirements.txt")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
Você é um assistente especializado em extrair informações de vagas de emprego.
Dado um texto bruto de uma página de vaga, retorne SOMENTE um objeto JSON válido
(sem markdown, sem explicações) com exatamente os seguintes campos:

{
  "cargo": "título/cargo da vaga",
  "empresa": "nome da empresa",
  "plataforma": "nome da plataforma/site onde foi encontrada a vaga",
  "localizacao": "cidade, estado ou 'Remoto' / 'Híbrido'",
  "modalidade": "Presencial | Remoto | Híbrido | Não informado",
  "tipo_contrato": "CLT | PJ | Estágio | Freelance | Temporário | Não informado",
  "salario": "faixa salarial ou 'Não informado'",
  "descricao_resumida": "descrição completa e detalhada da vaga",
  "url": "URL original da vaga",
  "data_extracao": "data/hora da extração no formato ISO 8601"
}

Se algum campo não puder ser determinado, use "Não informado".
Retorne APENAS o JSON, sem nenhum texto adicional.
"""


def _get_llm_client() -> tuple[Any, str]:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "")

    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("❌  Instale o pacote openai: pip install openai")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            sys.exit("❌  Defina OPENAI_API_KEY no .env")
        return OpenAI(api_key=api_key), model or "gpt-4o-mini"

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            sys.exit("❌  Defina GEMINI_API_KEY no .env")
        return OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        ), model or "gemini-1.5-flash"

    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            sys.exit("❌  Defina OPENROUTER_API_KEY no .env")
        return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1"), \
               model or "openai/gpt-4o-mini"

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            sys.exit("❌  Defina GROQ_API_KEY no .env")
        return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1"), \
               model or "llama3-8b-8192"

    sys.exit(f"❌  Provedor desconhecido: '{provider}'. Use: openai | gemini | openrouter | groq")


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

MAX_TEXT_CHARS = 6000

PLATFORM_MAP = {
    "gupy.io": "Gupy", "indeed.com": "Indeed", "linkedin.com": "LinkedIn",
    "bebee.com": "BeBee", "catho.com.br": "Catho", "infojobs.com.br": "InfoJobs",
    "infojobs.net": "InfoJobs", "vagas.com.br": "Vagas.com", "trampos.co": "Trampos",
    "remotar.com.br": "Remotar", "programathor.com.br": "Programathor",
    "universia.net": "Universia", "lever.co": "Lever", "greenhouse.io": "Greenhouse",
    "workable.com": "Workable", "breezy.hr": "Breezy HR",
    "smartrecruiters.com": "SmartRecruiters",
}


def _detect_platform(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return "Desconhecida"
    for key, name in PLATFORM_MAP.items():
        if key in host:
            return name
    parts = host.replace("www.", "").split(".")
    return parts[-2].capitalize() if len(parts) >= 2 else host or "Desconhecida"


try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False


def _scrape_with_crawl4ai(url: str) -> str | None:
    if not CRAWL4AI_AVAILABLE:
        return None
    try:
        import asyncio
        from crawl4ai import AsyncWebCrawler

        async def _crawl():
            async with AsyncWebCrawler(verbose=False) as crawler:
                res = await crawler.arun(url=url)
                if res and getattr(res, "success", False) and getattr(res, "markdown", None):
                    return str(res.markdown).strip()
                return None

        try:
            markdown = asyncio.run(_crawl())
        except RuntimeError:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: asyncio.run(_crawl()))
                markdown = future.result()

        if markdown:
            if len(markdown) > MAX_TEXT_CHARS:
                markdown = markdown[:MAX_TEXT_CHARS] + "\n\n[... conteúdo truncado ...]"
            return f"[Conteúdo Crawl4AI - Markdown]\n{markdown}"
        return None
    except Exception as exc:
        print(f"[job-extractor] Crawl4AI falhou ({exc}), usando fallback estático...")
        return None


def _scrape_page_legacy(url: str) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        raise RuntimeError(f"HTTP {status} ao acessar a URL") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Erro de rede: {exc}") from exc

    soup = BeautifulSoup(resp.text, "lxml")
    parts: list[str] = []

    # 1. JSON-LD (schema.org JobPosting)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            for item in (data if isinstance(data, list) else [data]):
                if isinstance(item, dict) and "JobPosting" in item.get("@type", ""):
                    parts.append("[JSON-LD JobPosting]\n" + json.dumps(item, ensure_ascii=False, indent=2))
        except (json.JSONDecodeError, TypeError):
            continue

    # 2. Meta tags
    meta_fields = {
        "og:title": None, "og:description": None, "og:site_name": None,
        "twitter:title": None, "twitter:description": None, "description": None,
    }
    for tag in soup.find_all("meta"):
        prop = tag.get("property") or tag.get("name") or ""
        if prop.lower() in meta_fields and tag.get("content"):
            meta_fields[prop.lower()] = tag["content"]
    meta_text = "\n".join(f"{k}: {v}" for k, v in meta_fields.items() if v)
    if meta_text:
        parts.append("[Meta Tags]\n" + meta_text)

    # 3. Título da página
    if soup.title and soup.title.string:
        parts.append(f"[Título da Página]\n{soup.title.string.strip()}")

    # 4. Texto do body
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe", "svg"]):
        tag.decompose()
    body_text = re.sub(r"\n{3,}", "\n\n", soup.get_text(separator="\n", strip=True))
    if body_text:
        parts.append("[Conteúdo da Página]\n" + body_text)

    full_text = "\n\n".join(parts)
    if len(full_text) > MAX_TEXT_CHARS:
        full_text = full_text[:MAX_TEXT_CHARS] + "\n\n[... conteúdo truncado ...]"
    return full_text


def _scrape_page(url: str) -> str:
    crawl_result = _scrape_with_crawl4ai(url)
    if crawl_result:
        return crawl_result
    return _scrape_page_legacy(url)



# ---------------------------------------------------------------------------
# Extração via LLM
# ---------------------------------------------------------------------------

def _extract_with_llm(scraped_text: str, url: str, platform: str,
                      client: Any, model: str) -> dict:
    user_message = (
        f"URL da vaga: {url}\n"
        f"Plataforma detectada: {platform}\n"
        f"Data/hora da extração: {datetime.now().astimezone().isoformat()}\n\n"
        f"--- CONTEÚDO RASPADO ---\n{scraped_text}"
    )
    kwargs: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.0,
        "max_tokens": 2048,
    }
    try:
        kwargs["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(**kwargs)
    except Exception:
        kwargs.pop("response_format", None)
        response = client.chat.completions.create(**kwargs)

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE | re.MULTILINE)
    raw = re.sub(r"\s*```\s*$", "", raw, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"LLM retornou resposta inválida:\n{raw[:500]}")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def extract_job(url: str, client: Any, model: str) -> dict:
    """Extrai informações de uma vaga a partir da URL."""
    url = url.strip()
    platform = _detect_platform(url)

    try:
        scraped = _scrape_page(url)
    except RuntimeError as exc:
        return _error_result(url, platform, str(exc))

    try:
        result = _extract_with_llm(scraped, url, platform, client, model)
        result.setdefault("url", url)
        result.setdefault("data_extracao", datetime.now().astimezone().isoformat())
        result.pop("erro", None)
        return result
    except Exception as exc:
        return _error_result(url, platform, f"Erro na LLM: {exc}")


def _error_result(url: str, platform: str, erro: str) -> dict:
    return {
        "cargo": "N/A", "empresa": "N/A", "plataforma": platform,
        "localizacao": "N/A", "modalidade": "N/A", "tipo_contrato": "N/A",
        "salario": "N/A", "descricao_resumida": "N/A",
        "url": url, "data_extracao": datetime.now().astimezone().isoformat(),
        "erro": erro,
    }
