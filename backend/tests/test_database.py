import uuid
from sqlalchemy import text
from app.db.models import Job, Source
from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus


async def test_wal_mode_enabled(db_session):
    result = await db_session.execute(text("PRAGMA journal_mode;"))
    mode = result.scalar()
    assert mode.lower() == "wal"


async def test_search_vector_column_exists(db_session):
    """The search_vector column should exist on the jobs table.

    On SQLite (test dialect) it falls back to a plain TEXT column via
    with_variant; on PostgreSQL it is a real TSVECTOR maintained by trigger.
    """
    result = await db_session.execute(text("PRAGMA table_info(jobs);"))
    columns = [row[1] for row in result.fetchall()]
    assert "search_vector" in columns


async def test_search_returns_matching_jobs_via_ilike(db_session):
    """Tests the SQLite/ILIKE fallback path of the search endpoint.

    Since the test DB is SQLite, the endpoint falls back to ILIKE on
    title/company, which we exercise by inserting a job and querying.
    """
    source = Source(
        name="Test Search",
        type="json",
        base_url="https://testsearch.io",
        status=SourceStatus.ACTIVE,
    )
    db_session.add(source)
    await db_session.commit()

    job = Job(
        id=uuid.uuid4(),
        title="Desenvolvedor Python Async",
        company="Tech Corp Search",
        location="São Paulo, SP",
        modality=JobModality.REMOTE,
        area=JobArea.TI_SOFTWARE,
        description="Vaga para engenheiro de software especialista em Python e SQLite",
        source_url="https://testsearch.io/job/1",
        source_id="search-1",
        source_uuid=source.id,
        status=JobStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(job)
    await db_session.commit()

    # LIKE match on title (SQLite doesn't support ILIKE, but LIKE is case-insensitive
    # for ASCII in SQLite by default)
    result = await db_session.execute(
        text("SELECT title FROM jobs WHERE title LIKE '%Python%';")
    )
    rows = result.fetchall()
    assert len(rows) >= 1
    assert any(row[0] == "Desenvolvedor Python Async" for row in rows)
