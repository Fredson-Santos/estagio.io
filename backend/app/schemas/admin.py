from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdminStats(BaseModel):
    total_jobs: int
    active_jobs: int
    featured_jobs: int
    sources: int
    last_scraped_at: Optional[datetime] = None


class ScraperRunResponse(BaseModel):
    message: str
    status: str
