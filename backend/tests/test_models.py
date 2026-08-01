import uuid
from datetime import datetime, timezone

import pytest

from app.db.database import Base
from app.db.models import Job, Source, TrackedJob, User
from estagio_shared.taxonomy import (
    JobArea,
    JobModality,
    JobStatus,
    SourceStatus,
    TrackingStatus,
)


def test_job_areas_exist():
    assert hasattr(JobArea, "TI_SOFTWARE")
    assert hasattr(JobArea, "DADOS")
    assert hasattr(JobArea, "DESIGN")
    assert JobArea.TI_SOFTWARE.value == "TI_SOFTWARE"


def test_job_modalities_exist():
    assert hasattr(JobModality, "REMOTE")
    assert hasattr(JobModality, "HYBRID")
    assert hasattr(JobModality, "ONSITE")
    assert JobModality.REMOTE.value == "REMOTE"


def test_job_statuses_exist():
    assert hasattr(JobStatus, "ACTIVE")
    assert hasattr(JobStatus, "CLOSED")


def test_source_statuses_exist():
    assert hasattr(SourceStatus, "ACTIVE")
    assert hasattr(SourceStatus, "INACTIVE")
    assert hasattr(SourceStatus, "ERROR")


def test_tracking_statuses_exist():
    assert hasattr(TrackingStatus, "SAVED")
    assert hasattr(TrackingStatus, "APPLIED")
    assert hasattr(TrackingStatus, "INTERVIEW")
    assert hasattr(TrackingStatus, "OFFER")
    assert hasattr(TrackingStatus, "HIRED")
    assert hasattr(TrackingStatus, "REJECTED")
    assert TrackingStatus.SAVED.value == "SAVED"


@pytest.mark.asyncio
async def test_user_model_creates_correctly(db_session):
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        hashed_password="hashed",
        plan="free",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    assert user.id is not None
    assert user.email == "user@example.com"
    assert user.plan == "free"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_tracked_job_with_internal_job(db_session):
    source = Source(name="Gupy", type="json", base_url="https://gupy.io", status=SourceStatus.ACTIVE)
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)

    job = Job(
        id=uuid.uuid4(),
        title="Estagio Backend",
        company="ACME",
        modality=JobModality.REMOTE,
        area=JobArea.TI_SOFTWARE,
        source_url="https://example.com/job/1",
        source_id="gupy-1",
        source_uuid=source.id,
        status=JobStatus.ACTIVE,
        is_active=True,
        is_featured=False,
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    user = User(
        id=uuid.uuid4(),
        email="user2@example.com",
        hashed_password="hashed",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    tracked = TrackedJob(
        id=uuid.uuid4(),
        user_id=user.id,
        job_id=job.id,
        status=TrackingStatus.APPLIED,
    )
    db_session.add(tracked)
    await db_session.commit()
    await db_session.refresh(tracked)
    assert tracked.job_id == job.id
    assert tracked.status == TrackingStatus.APPLIED


@pytest.mark.asyncio
async def test_tracked_job_with_external_url(db_session):
    user = User(
        id=uuid.uuid4(),
        email="user3@example.com",
        hashed_password="hashed",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    tracked = TrackedJob(
        id=uuid.uuid4(),
        user_id=user.id,
        job_id=None,
        external_url="https://externo.com/vaga",
        external_title="Vaga Externa",
        external_company="Outra Empresa",
        external_logo=None,
        status=TrackingStatus.SAVED,
    )
    db_session.add(tracked)
    await db_session.commit()
    await db_session.refresh(tracked)
    assert tracked.job_id is None
    assert tracked.external_url == "https://externo.com/vaga"
    assert tracked.external_title == "Vaga Externa"
    assert tracked.status == TrackingStatus.SAVED


def test_tracked_job_status_enum_values():
    assert {s.value for s in TrackingStatus} == {
        "SAVED", "APPLIED", "INTERVIEW", "OFFER", "HIRED", "REJECTED"
    }
