from rapidfuzz import fuzz

def is_duplicate(new_job: dict, existing_jobs: list[dict], threshold: float = 85.0) -> bool:
    """
    Verifica se uma nova vaga já existe em uma lista de vagas usando similaridade de string.
    Considera o título, empresa e localização.
    """
    if not existing_jobs:
        return False

    new_str = f"{new_job.get('title', '')} {new_job.get('company', '')} {new_job.get('location', '')}".lower()

    for job in existing_jobs:
        # Se for a mesma URL, é duplicada óbvia
        if new_job.get('source_url') == job.get('source_url'):
            return True

        existing_str = f"{job.get('title', '')} {job.get('company', '')} {job.get('location', '')}".lower()
        similarity = fuzz.token_sort_ratio(new_str, existing_str)
        
        if similarity >= threshold:
            return True
            
    return False
