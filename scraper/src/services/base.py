"""Helpers compartilhados entre todos os scrapers.

Portado seletivamente do scraper-api/services/base.py, adaptado para a
taxonomia do estagio_shared e arquitetura async do estagio.io.
"""
import json
import re
from datetime import datetime, timezone
from typing import Any

from estagio_shared.taxonomy import JobModality

from src.services.matcher import regex_fallback_classify

# Mapeamento de sigla de estado → nome completo
STATES_MAP: dict[str, str] = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AM": "Amazonas",
    "AP": "Amapá",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MG": "Minas Gerais",
    "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso",
    "PA": "Pará",
    "PB": "Paraíba",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "PR": "Paraná",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RO": "Rondônia",
    "RR": "Roraima",
    "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina",
    "SE": "Sergipe",
    "SP": "São Paulo",
    "TO": "Tocantins",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_val(val: Any) -> Any:
    if isinstance(val, str):
        return re.sub(r"[\ud800-\udfff]", "", val)
    return val


def dump_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=True)


def clean_html(raw_html: str | None) -> str:
    if not raw_html or not isinstance(raw_html, str):
        return ""
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean_val(clean)


def parse_location_obj(
    city_val: str | None = None,
    state_val: str | None = None,
    raw_loc_str: str | None = None,
    modality: str | JobModality = "ON_SITE",
) -> dict[str, str | None]:
    city = clean_val(city_val)
    state = clean_val(state_val)

    if not city and raw_loc_str:
        raw_clean = clean_val(raw_loc_str)
        match_sigla = re.search(r"([A-Za-zÀ-ÿ\s]+)[-/,\s]+([A-Z]{2})\b", raw_clean)
        if match_sigla:
            city = match_sigla.group(1).strip()
            state = match_sigla.group(2).strip()
        else:
            city = raw_clean.strip()

    if city and not state:
        match_st = re.search(r"\b([A-Z]{2})\b", raw_loc_str or "")
        if match_st:
            state = match_st.group(1)

    return {"city": city, "state": state, "country": "BR"}


def normalize_location(city: str | None, state: str | None) -> str:
    """Retorna localização normalizada no formato 'Cidade, UF' ou 'UF'.

    - A sigla de estado é mantida em maiúsculas (ex: 'SP', 'MG').
    - Se não houver cidade, retorna apenas a sigla do estado.
    - Se não houver nenhum dos dois, retorna string vazia.
    """
    city_clean = (city or "").strip()
    state_clean = (state or "").strip().upper()

    # Normaliza: se o valor recebido for o nome por extenso (ex: "São Paulo"),
    # converte de volta para a sigla usando o mapa invertido.
    if state_clean and state_clean not in STATES_MAP:
        inverse = {v.upper(): k for k, v in STATES_MAP.items()}
        state_clean = inverse.get(state_clean, state_clean)

    if city_clean and state_clean:
        return f"{city_clean}, {state_clean}"
    if city_clean:
        return city_clean
    return state_clean


def format_modality_enum(modality_str: str | None) -> JobModality:
    if not modality_str:
        return JobModality.ONSITE
    s = str(modality_str).upper()
    if "REMOTE" in s or "REMOTO" in s or "HOME" in s:
        return JobModality.REMOTE
    if "HYBRID" in s or "HÍBRIDO" in s or "HIBRIDO" in s:
        return JobModality.HYBRID
    return JobModality.ONSITE


def format_contract_enum(type_str: str | None) -> str:
    if not type_str:
        return "INTERNSHIP"
    s = str(type_str).upper()
    if "ESTÁGIO" in s or "ESTAGIO" in s or "INTERN" in s:
        return "INTERNSHIP"
    if "TRAINEE" in s:
        return "TRAINEE"
    if "CLT" in s or "EFETIVO" in s or "FULL" in s:
        return "FULL_TIME"
    return "INTERNSHIP"


def format_iso_datetime(dt_str: str | None) -> datetime | None:
    if not dt_str:
        return None
    try:
        dt_str_clean = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str_clean)
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(dt_str, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            pass
    return None


def parse_string_list(val: Any) -> list[str]:
    if not val:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if x and str(x).strip()]
    if isinstance(val, str):
        return [x.strip() for x in re.split(r"[,;\n]+", val) if x.strip()]
    return []


def extract_areas_and_category(
    title: str,
    description: str = "",
    raw_area: str | None = None,
) -> tuple[str, list[str]]:
    text = f"{title or ''} {description or ''}".lower()

    is_program = False
    if any(k in text for k in ["programa de estágio", "programa de estagio", "banco de talentos", "programa estagiário"]):
        is_program = True
    elif title and "programa" in title.lower():
        is_program = True

    category = "INTERNSHIP_PROGRAM" if is_program else "INTERNSHIP"

    areas: list[str] = []
    if raw_area and isinstance(raw_area, str) and raw_area.strip() and raw_area.strip() != "-":
        areas = regex_fallback_classify(raw_area.strip())

    return category, areas


def format_company_name(name: str | None) -> str:
    if not name:
        return "Empresa não informada"
    cleaned = re.sub(r"\s*\(.*?\)", "", str(name)).strip()
    return cleaned if cleaned else str(name).strip()
