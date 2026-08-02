import asyncio
import os
import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.db.database import Base, get_db
from app.db.models import Job, Source
from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_ADMIN_KEY = "test-admin-key"


from sqlalchemy import text


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def engine(tmp_path):
    db_file = tmp_path / "test.db"
    test_db_url = f"sqlite+aiosqlite:///{db_file}"
    eng = create_async_engine(test_db_url, echo=False)
    async with eng.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL;"))
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()



@pytest.fixture(scope="function")
async def db_session(engine):
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session, monkeypatch):
    from app.main import app
    from app.core.config import settings

    monkeypatch.setattr(settings, "ADMIN_API_KEY", TEST_ADMIN_KEY)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers():
    return {"X-Admin-Key": TEST_ADMIN_KEY}


@pytest.fixture
async def seed_job(db_session):
    source = Source(
        name="Gupy",
        type="json",
        base_url="https://portal.gupy.io",
        status=SourceStatus.ACTIVE,
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)

    job = Job(
        id=uuid.uuid4(),
        title="Estágio Backend",
        company="ACME",
        location="São Paulo",
        modality=JobModality.HYBRID,
        area=JobArea.TI_SOFTWARE,
        description="Descrição",
        source_url="https://example.com/job/1",
        source_id="gupy-1",
        posted_at=datetime.now(timezone.utc),
        source_uuid=source.id,
        status=JobStatus.ACTIVE,
        is_active=True,
        is_featured=False,
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job


@pytest.fixture
async def seed_featured_jobs(db_session):
    """Cria 3 vagas ativas: 2 em destaque e 1 comum, compartilhando 1 source."""
    source = Source(
        name="Gupy",
        type="json",
        base_url="https://portal.gupy.io",
        status=SourceStatus.ACTIVE,
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)

    jobs = []
    specs = [
        ("Estágio Backend", "ACME", JobModality.HYBRID, True),
        ("Estágio Frontend", "Beta", JobModality.REMOTE, True),
        ("Estágio DevOps", "Gamma", JobModality.ONSITE, False),
    ]
    for i, (title, company, modality, is_featured) in enumerate(specs):
        job = Job(
            id=uuid.uuid4(),
            title=title,
            company=company,
            location="São Paulo",
            modality=modality,
            area=JobArea.TI_SOFTWARE,
            description="Descrição",
            source_url=f"https://example.com/job/{i}",
            source_id=f"gupy-{i}",
            posted_at=datetime.now(timezone.utc),
            source_uuid=source.id,
            status=JobStatus.ACTIVE,
            is_active=True,
            is_featured=is_featured,
        )
        db_session.add(job)
        jobs.append(job)

    await db_session.commit()
    for j in jobs:
        await db_session.refresh(j)
    return jobs
