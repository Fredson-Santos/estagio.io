"""Classificação de áreas de vagas via LLM (Groq) + regex fallback.

Portado do scraper-api/services/matcher.py, adaptado para async (httpx) e
para a taxonomia do estagio_shared (JobArea enum).
"""
import asyncio
import json
import logging
import re
from typing import Dict, List

import httpx
from sqlalchemy.future import select

from estagio_shared.taxonomy import JobArea

from src.config import settings
from src.db.database import AsyncSessionLocal
from src.db.models import ScrapedJob

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
Você é um classificador de áreas de vagas de estágio.
Sua função é receber um JSON com a chave 'title' representando o título da vaga e retornar a classificação em um JSON com a chave 'areas'.

Áreas válidas (utilize exclusivamente estes códigos em maiúsculo):
- "IT": TI, Software, Desenvolvimento, Programação, Engenharia de Software, Web, Cloud, DevOps
- "DATA": Ciência de Dados, Analytics, Business Intelligence (BI), Power BI, SQL, IA
- "ENGINEERING": Engenharia, Projetos Industriais, Automação
- "OPERATIONS": Manufatura, Produção, Logística, Operações, Supply Chain
- "MARKETING": Marketing, Trade Marketing, Comunicação, Mídias Sociais, Branding, SEO
- "FINANCE": Finanças, Contabilidade, Tesouraria, Auditoria, Controladoria, Fiscal
- "HUMAN_RESOURCES": Recursos Humanos, RH, Gestão de Pessoas, People & Culture
- "LEGAL": Direito, Jurídico Corporativo, Compliance
- "DESIGN": Design Gráfico, UX/UI Design, Product Design
- "BUSINESS": Administração, Compras, Comercial, Vendas, Negócios, Consultoria, Planejamento
"""

REGEX_AREA_PATTERNS: list[tuple[str, list[str]]] = [
    ("IT", [r"\bti\b", r"\bsoftware\b", r"\bdesenvolv", r"\bprogramaç", r"\bweb\b", r"\bcloud\b", r"\bdevops\b", r"\bsistemas\b", r"\btecnologia\b", r"\binformática\b"]),
    ("DATA", [r"\bdados\b", r"\bdata\b", r"\banalytics\b", r"\bintelligence\b", r"\bbi\b", r"\bpower bi\b", r"\bsql\b", r"\bia\b", r"\bmachine learning\b"]),
    ("ENGINEERING", [r"\bengenhar", r"\beng\b", r"\bprojetos industriais\b", r"\bautomação\b", r"\bmanutenção industrial\b", r"\bobras\b", r"\belétrica\b", r"\bmecânica\b", r"\bcivil\b", r"\bquímica\b"]),
    ("MARKETING", [r"\bmarketing\b", r"\bcomunicação\b", r"\bmídias\b", r"\bmidias\b", r"\bbranding\b", r"\bseo\b", r"\bconteúdo\b", r"\bredes sociais\b"]),
    ("FINANCE", [r"\bfinan", r"\bcontáb", r"\bcontab", r"\btesouraria\b", r"\bauditoria\b", r"\bcontroladoria\b", r"\bfiscal\b", r"\bcrédito\b", r"\bcobrança\b"]),
    ("BUSINESS", [r"\badministra", r"\badm\b", r"\bcompras\b", r"\bcomercial\b", r"\bvendas\b", r"\bnegócios\b", r"\bnegocios\b", r"\bconsultoria\b", r"\bplanejamento\b", r"\batendimento\b"]),
    ("HUMAN_RESOURCES", [r"\brecursos humanos\b", r"\brh\b", r"\bgestão de pessoas\b", r"\bpeople\b", r"\btalentos\b", r"\bdepartamento pessoal\b", r"\bdp\b"]),
    ("DESIGN", [r"\bdesign\b", r"\bux\b", r"\bui\b", r"\bproduto\b", r"\bgrafico\b", r"\bgráfico\b"]),
    ("LEGAL", [r"\bdireito\b", r"\bjurídic\b", r"\bjuridico\b", r"\bcompliance\b"]),
    ("OPERATIONS", [r"\blogística\b", r"\blogistica\b", r"\boperaç", r"\bsupply chain\b", r"\boperacion\b", r"\balmoxarifado\b", r"\bprodução\b"]),
]

_AREA_MAP: Dict[str, JobArea] = {
    "IT": JobArea.TI_SOFTWARE,
    "DATA": JobArea.DADOS,
    "ENGINEERING": JobArea.ENGENHARIA_OUTRAS,
    "OPERATIONS": JobArea.OUTROS,
    "MARKETING": JobArea.MARKETING,
    "FINANCE": JobArea.FINANCAS,
    "BUSINESS": JobArea.NEGOCIOS,
    "HUMAN_RESOURCES": JobArea.RH,
    "LEGAL": JobArea.DIREITO,
    "DESIGN": JobArea.DESIGN,
}

ALLOWED_AREAS = list(_AREA_MAP.keys())


def _map_area_code(code: str) -> JobArea:
    return _AREA_MAP.get(code.upper(), JobArea.OUTROS)


def regex_fallback_classify(text: str) -> List[str]:
    if not text:
        return []
    text_lower = text.lower()
    areas: List[str] = []
    for area_code, patterns in REGEX_AREA_PATTERNS:
        for p in patterns:
            if re.search(p, text_lower):
                if area_code not in areas:
                    areas.append(area_code)
                break
    return areas


async def classify_job_areas_llm(title: str, max_retries: int = 3) -> List[str]:
    if not title or not isinstance(title, str):
        return []

    groq_key = settings.GROQ_API_KEY.get_secret_value() if settings.GROQ_API_KEY else None
    if not groq_key:
        return regex_fallback_classify(title)

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json",
    }
    user_payload = {"title": title}
    prompt = (
        f"Analise o seguinte título de vaga e retorne a classificação em formato JSON:\n"
        f"{json.dumps(user_payload, ensure_ascii=False)}"
    )
    payload = {
        "model": settings.GROQ_MODEL,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    settings.GROQ_ENDPOINT, headers=headers, json=payload
                )
                if response.status_code == 429:
                    wait_sec = (attempt + 1) * 3
                    await asyncio.sleep(wait_sec)
                    continue
                response.raise_for_status()
                res_json = response.json()
                content = res_json["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                raw_areas = parsed.get("areas", [])
                if isinstance(raw_areas, list):
                    return [str(a).upper() for a in raw_areas if str(a).upper() in ALLOWED_AREAS]
                return []
            except Exception:
                if attempt == max_retries - 1:
                    return regex_fallback_classify(title)
                await asyncio.sleep(2)
    return regex_fallback_classify(title)


async def classify_job_area_single(title: str) -> JobArea:
    """Classifica um único título e retorna o JobArea correspondente.

    Se LLM/regex identificar múltiplas áreas, retorna a primeira.
    Para títulos de programa de estágio, retorna PROGRAMA_ESTAGIO.
    """
    title_lower = (title or "").lower()
    program_keywords = [
        "programa de estágio", "programa de estagio",
        "diversas áreas", "várias áreas",
        "banco de talentos", "multi-áreas",
    ]
    if any(k in title_lower for k in program_keywords):
        return JobArea.PROGRAMA_ESTAGIO

    mode = settings.AREA_MATCHER_MODE.lower()
    if mode == "llm":
        codes = await classify_job_areas_llm(title)
    else:
        codes = regex_fallback_classify(title)

    if not codes:
        return JobArea.OUTROS
    return _map_area_code(codes[0])


async def process_db_area_matching() -> int:
    """Classifica vagas com area == OUTROS via LLM e atualiza no banco.

    Returns:
        Número de vagas atualizadas.
    """
    logger.info("Iniciando classificação de áreas via LLM/regex...")

    title_cache: Dict[str, JobArea] = {}
    updated_count = 0

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ScrapedJob).where(ScrapedJob.area == JobArea.OUTROS)
        )
        rows = result.scalars().all()

        if not rows:
            logger.info("Nenhuma vaga com area == OUTROS para classificar.")
            return 0

        logger.info("Classificando %d vagas com area == OUTROS...", len(rows))

        for job in rows:
            title_clean = (job.title or "").strip()
            if not title_clean:
                continue

            if title_clean in title_cache:
                area = title_cache[title_clean]
            else:
                area = await classify_job_area_single(title_clean)
                title_cache[title_clean] = area

            job.area = area
            updated_count += 1

            if updated_count % 20 == 0:
                await session.commit()

        await session.commit()

    logger.info(
        "Classificação concluída: %d vagas atualizadas (%d títulos distintos).",
        updated_count,
        len(title_cache),
    )
    return updated_count
