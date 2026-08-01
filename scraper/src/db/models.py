import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from estagio_shared.taxonomy import (
    JobArea,
    JobModality,
    SourceStatus,
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

    jobs = relationship("ScrapedJob", back_populates="source")


class ScrapedJob(Base):
    __tablename__ = "scraped_jobs"

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

    benefits: Mapped[str] = mapped_column(Text, nullable=True)
    requirements: Mapped[str] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_pcd: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    contract_type: Mapped[str] = mapped_column(String(50), nullable=True)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=True)
    salary_min_cents: Mapped[int] = mapped_column(Integer, nullable=True)
    salary_max_cents: Mapped[int] = mapped_column(Integer, nullable=True)

    synced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    source_uuid: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source = relationship("Source", back_populates="jobs")
