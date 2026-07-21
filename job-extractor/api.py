"""
api.py — Job Extractor API
Inicia: uvicorn api:app --reload --host 0.0.0.0 --port 8000
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from job_extractor import _get_llm_client, extract_job

app = FastAPI(title="Job Extractor API", version="1.0.0")


class ExtractRequest(BaseModel):
    url: str


@app.post("/extract")
def extract(body: ExtractRequest):
    """Recebe uma URL de vaga e retorna as informações estruturadas em JSON."""
    try:
        client, model = _get_llm_client()
    except SystemExit as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    result = extract_job(body.url, client, model)
    return result
