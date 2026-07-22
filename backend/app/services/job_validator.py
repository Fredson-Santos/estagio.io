"""
job_validator.py - Módulo de validação de qualidade de vagas.
Garante que apenas vagas com informações completas e de qualidade sejam aceitas.
"""

from typing import Tuple, Dict, Any
from app.core.taxonomy import JobModality

INVALID_PLACEHOLDERS = {
    "n/a", "na", "não informado", "nao informado", "não especificado",
    "nao especificado", "desconhecido", "indefinido", "vaga gupy", "vaga eureca",
    "empresa confidencial"
}

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
    if not description or description.lower() in INVALID_PLACEHOLDERS or len(description) < 30:
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
