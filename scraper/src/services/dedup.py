from rapidfuzz import fuzz


def is_url_duplicate(source_url: str, existing_urls: set[str]) -> bool:
    """Verificação rápida O(1) por URL exata."""
    return source_url in existing_urls


def is_fuzzy_duplicate(new_job: dict, existing_jobs: list[dict], threshold: float = 85.0) -> bool:
    """
    Verifica se uma nova vaga é similar a alguma existente via fuzzy matching.
    Deve ser chamada APÓS is_url_duplicate (que é O(1)).
    """
    if not existing_jobs:
        return False

    new_str = f"{new_job.get('title', '')} {new_job.get('company', '')} {new_job.get('location', '')}".lower()

    for job in existing_jobs:
        existing_str = f"{job.get('title', '')} {job.get('company', '')} {job.get('location', '')}".lower()
        similarity = fuzz.token_sort_ratio(new_str, existing_str)

        if similarity >= threshold:
            return True

    return False


def is_duplicate(new_job: dict, existing_jobs: list[dict], existing_urls: set[str] | None = None, threshold: float = 85.0) -> bool:
    """Verificação combinada: URL exata (O(1)) + fuzzy (O(n)).

    Se existing_urls for fornecido, usa set lookup primeiro.
    Mantém compatibilidade retroativa com chamadas existentes.
    """
    url = new_job.get("source_url", "")
    if existing_urls is not None:
        if url in existing_urls:
            return True
    else:
        # Fallback legado: verifica URL na lista (O(n))
        for job in existing_jobs:
            if url == job.get("source_url"):
                return True

    return is_fuzzy_duplicate(new_job, existing_jobs, threshold)
