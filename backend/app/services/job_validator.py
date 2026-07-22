"""
job_validator.py - Módulo de validação de qualidade de vagas.
Garante que apenas vagas com informações completas e de qualidade sejam aceitas.
"""

import re
from typing import Tuple, Dict, Any
from app.core.taxonomy import JobModality

INVALID_PLACEHOLDERS = {
    "n/a", "na", "não informado", "nao informado", "não especificado",
    "nao especificado", "desconhecido", "indefinido", "vaga gupy", "vaga eureca",
    "empresa confidencial"
}

def safe_str(text: Any) -> str:
    """Converte o texto para string e remove caracteres que falham no print do console Windows (CP1252)."""
    if text is None:
        return ""
    return str(text).encode("ascii", errors="replace").decode("ascii")


def parse_salary(salary_obj: Any) -> Any:
    """
    Normaliza e formata a informação de salário.
    Retorna uma string amigável (ex: 'R$ 1.500,00') ou None se for undisclosed/inválido.
    """
    if not salary_obj:
        return None

    if isinstance(salary_obj, str):
        salary_str = salary_obj.strip()
        if not salary_str or salary_str.lower() in ["none", "null", "undisclosed", "a combinar", "não informado", "nao informado"]:
            return None
        if salary_str.startswith("{") or "undisclosed" in salary_str.lower() or "'display'" in salary_str:
            return None
        return salary_str

    if isinstance(salary_obj, dict):
        display = str(salary_obj.get("display", "")).lower()
        if display == "undisclosed" or "undisclosed" in str(salary_obj):
            return None

        label = salary_obj.get("name") or salary_obj.get("label") or salary_obj.get("text")
        if label and isinstance(label, str) and not label.startswith("{"):
            return label.strip()

        min_cents = salary_obj.get("minCents")
        max_cents = salary_obj.get("maxCents")
        cents = salary_obj.get("cents") or salary_obj.get("value")

        if cents and isinstance(cents, (int, float)) and cents > 0:
            val = cents / 100 if cents > 100 else cents
            return f"R$ {val:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

        if min_cents and max_cents and isinstance(min_cents, (int, float)) and min_cents > 0:
            min_val = min_cents / 100
            max_val = max_cents / 100
            return f"R$ {min_val:,.0f} - R$ {max_val:,.0f}".replace(",", ".")
        elif min_cents and isinstance(min_cents, (int, float)) and min_cents > 0:
            min_val = min_cents / 100
            return f"A partir de R$ {min_val:,.0f}".replace(",", ".")

        return None

    return None



def validate_job(job: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida se uma vaga possui todas as informações necessárias exigidas pelo frontend.
    
    Retorna (True, "") se a vaga for válida, ou (False, motivo) se for inválida.
    """
    if not isinstance(job, dict):
        return False, "Dados da vaga em formato inválido"

    # Check for scraper error flag
    if job.get("erro"):
        return False, f"Vaga possui erro de extração: {job.get('erro')}"

    # 1. Título
    title = str(job.get("title") or "").strip()
    if not title or title.lower() in INVALID_PLACEHOLDERS or len(title) < 3:
        return False, "Título da vaga ausente ou inválido"

    # 2. Empresa
    company = str(job.get("company") or "").strip()
    if not company or company.lower() in INVALID_PLACEHOLDERS:
        return False, "Empresa ausente ou inválida"

    # 3. URL da fonte
    source_url = str(job.get("source_url") or "").strip()
    if not source_url or source_url == "#" or not (source_url.startswith("http://") or source_url.startswith("https://")):
        return False, "URL da vaga ausente ou inválida"

    # 4. Descrição
    description = str(job.get("description") or "").strip()
    plain_desc = re.sub(r'<[^>]+>', '', description).strip()
    if not plain_desc or plain_desc.lower() in INVALID_PLACEHOLDERS or len(plain_desc) < 30:
        return False, "Descrição da vaga ausente, insuficiente ou inválida (mínimo 30 caracteres)"

    # 5. Modalidade & Localização
    modality = job.get("modality")
    location = str(job.get("location") or "").strip()
    location_lower = location.lower()

    # Se for remoto, a localização pode ser "Remoto"
    if modality == JobModality.REMOTE or location_lower in ["remoto", "home office", "teletrabalho"]:
        pass # Vaga remota válida
    else:
        # Se for presencial (ONSITE) ou híbrido (HYBRID), EXIGE informação de localização real
        if not location or location_lower in INVALID_PLACEHOLDERS or location_lower in ["remoto"]:
            return False, "Vaga presencial/híbrida sem informação válida de localização (cidade/estado)"

    return True, ""
