from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class IngestJobItem(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    modality: str
    area: str
    description: Optional[str] = None
    salary: Optional[str] = None
    salary_min_cents: Optional[int] = None
    salary_max_cents: Optional[int] = None
    company_logo: Optional[str] = None
    source_url: str
    source_id: str
    posted_at: Optional[datetime] = None
    source_name: Optional[str] = None

    benefits: Optional[str] = None
    requirements: Optional[str] = None
    deadline: Optional[datetime] = None
    is_pcd: bool = False
    contract_type: Optional[str] = None
    duration_months: Optional[int] = None


class IngestRequest(BaseModel):
    items: list[IngestJobItem]


class IngestResponse(BaseModel):
    inserted: int
    duplicated: int
    errors: list[str]


class ExpireRequest(BaseModel):
    expired_urls: list[str]


class ExpireResponse(BaseModel):
    expired: int
