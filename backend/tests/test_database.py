import uuid
from sqlalchemy import text
from app.db.models import Job, Source
from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus


async def test_wal_mode_enabled(db_session):
    result = await db_session.execute(text("PRAGMA journal_mode;"))
    mode = result.scalar()
    assert mode.lower() == "wal"


async def test_fts5_table_exists(db_session):
    result = await db_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs_fts';")
    )
    name = result.scalar()
    assert name == "jobs_fts"


async def test_fts5_triggers_exist(db_session):
    result = await db_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'jobs_fts_%';")
    )
    triggers = [row[0] for row in result.fetchall()]
    assert "jobs_fts_insert" in triggers
    assert "jobs_fts_delete" in triggers
    assert "jobs_fts_update" in triggers


async def test_fts5_indexes_job_on_insert(db_session):
    source = Source(name="Test FTS", type="json", base_url="https://testfts.io", status=SourceStatus.ACTIVE)
    db_session.add(source)
    await db_session.commit()

    job = Job(
        id=uuid.uuid4(),
        title="Desenvolvedor Python Async",
        company="Tech Corp FTS",
        location="São Paulo, SP",
        modality=JobModality.REMOTE,
        area=JobArea.TI_SOFTWARE,
        description="Vaga para engenheiro de software especialista em Python e SQLite",
        source_url="https://testfts.io/job/1",
        source_id="fts-1",
        source_uuid=source.id,
        status=JobStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(job)
    await db_session.commit()

    result = await db_session.execute(
        text("SELECT title, company FROM jobs_fts WHERE jobs_fts MATCH 'Python';")
    )
    rows = result.fetchall()
    assert len(rows) >= 1
    assert any(row[0] == "Desenvolvedor Python Async" for row in rows)
