import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.core.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

def utcnow():
    return datetime.now(timezone.utc)

class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. json, html
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    last_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[SourceStatus] = mapped_column(SQLEnum(SourceStatus, name="sourcestatus"), default=SourceStatus.ACTIVE, nullable=False)

    jobs = relationship("Job", back_populates="source")

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    modality: Mapped[JobModality] = mapped_column(SQLEnum(JobModality, name="jobmodality"), nullable=False)
    area: Mapped[JobArea] = mapped_column(SQLEnum(JobArea, name="jobarea"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False) # ID na fonte de origem
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    status: Mapped[JobStatus] = mapped_column(SQLEnum(JobStatus, name="jobstatus"), default=JobStatus.ACTIVE, nullable=False)

    source_uuid: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source = relationship("Source", back_populates="jobs")
    clicks = relationship("JobClick", back_populates="job")

class JobClick(Base):
    __tablename__ = "job_clicks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    referrer: Mapped[str] = mapped_column(String(255), nullable=True)

    job = relationship("Job", back_populates="clicks")
