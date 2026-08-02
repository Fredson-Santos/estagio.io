import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from estagio_shared.taxonomy import (
    JobArea,
    JobModality,
    JobStatus,
    SourceStatus,
    TrackingStatus,
)


def utcnow():
    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    last_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[SourceStatus] = mapped_column(
        SQLEnum(SourceStatus, name="sourcestatus"),
        default=SourceStatus.ACTIVE,
        nullable=False,
    )

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
    salary: Mapped[str] = mapped_column(String(255), nullable=True)
    company_logo: Mapped[str] = mapped_column(String(1000), nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[JobStatus] = mapped_column(SQLEnum(JobStatus, name="jobstatus"), default=JobStatus.ACTIVE, nullable=False)

    benefits: Mapped[str] = mapped_column(Text, nullable=True)
    requirements: Mapped[str] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_pcd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contract_type: Mapped[str] = mapped_column(String(50), nullable=True)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=True)
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    salary_min_cents: Mapped[int] = mapped_column(Integer, nullable=True)
    salary_max_cents: Mapped[int] = mapped_column(Integer, nullable=True)

    search_vector = Column(TSVECTOR().with_variant(Text(), "sqlite", "mysql"))

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


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    tracked_jobs = relationship("TrackedJob", back_populates="user", cascade="all, delete-orphan")


class TrackedJob(Base):
    __tablename__ = "tracked_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    external_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    external_title: Mapped[str] = mapped_column(String(255), nullable=True)
    external_company: Mapped[str] = mapped_column(String(255), nullable=True)
    external_logo: Mapped[str] = mapped_column(String(1000), nullable=True)
    status: Mapped[TrackingStatus] = mapped_column(
        SQLEnum(TrackingStatus, name="trackingstatus"),
        default=TrackingStatus.SAVED,
        nullable=False,
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    tracked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="tracked_jobs")
    job = relationship("Job")
