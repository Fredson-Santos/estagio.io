from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.core.taxonomy import JobArea, JobModality, JobStatus

class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    modality: JobModality
    area: JobArea
    description: Optional[str] = None
    source_url: str
    posted_at: Optional[datetime] = None

class JobResponse(JobBase):
    id: UUID
    scraped_at: datetime
    is_active: bool
    status: JobStatus
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedJobResponse(BaseModel):
    items: List[JobResponse]
    total: int
    skip: int
    limit: int
