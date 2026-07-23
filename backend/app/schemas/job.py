from pydantic import BaseModel, ConfigDict, model_validator
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
    salary: Optional[str] = None
    company_logo: Optional[str] = None
    source_url: str
    posted_at: Optional[datetime] = None
    source_name: Optional[str] = None

from datetime import datetime, timezone, timedelta

class JobResponse(JobBase):
    id: UUID
    scraped_at: datetime
    is_active: bool
    status: JobStatus
    is_new: Optional[bool] = None
    
    @model_validator(mode='after')
    def compute_is_new(self) -> 'JobResponse':
        if self.posted_at:
            now = datetime.now(timezone.utc)
            posted_at_utc = self.posted_at
            if posted_at_utc.tzinfo is None:
                posted_at_utc = posted_at_utc.replace(tzinfo=timezone.utc)
            self.is_new = (now - posted_at_utc) <= timedelta(days=3)
        else:
            self.is_new = False

        if not self.source_name and hasattr(self, 'source') and getattr(self, 'source', None):
            self.source_name = getattr(self.source, 'name', None)
        return self

    model_config = ConfigDict(from_attributes=True)

class PaginatedJobResponse(BaseModel):
    items: List[JobResponse]
    total: int
    skip: int
    limit: int
