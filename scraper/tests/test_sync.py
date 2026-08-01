import uuid
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
import httpx
from src.db.models import ScrapedJob, Source
from src.services.sync import sync_to_backend, sync_expirations
from estagio_shared.taxonomy import JobArea, JobModality, SourceStatus


@pytest_asyncio.fixture
async def setup_scraper_db(tmp_path, monkeypatch):

    from src.config import settings
    db_file = tmp_path / "scraper_test.db"
    monkeypatch.setattr(settings, "SCRAPER_DB_PATH", str(db_file))

    from src.db.database import engine, Base, AsyncSessionLocal
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        source = Source(name="Test", type="json", base_url="https://test.io", status=SourceStatus.ACTIVE)
        session.add(source)
        await session.commit()

        job = ScrapedJob(
            id=uuid.uuid4(),
            title="Estágio Python Sync",
            company="Sync Corp",
            location="São Paulo",
            modality=JobModality.REMOTE,
            area=JobArea.TI_SOFTWARE,
            description="Descrição da vaga de teste para sync",
            source_url="https://test.io/job/sync1",
            source_id="sync1",
            source_uuid=source.id,
            synced=False,
        )
        session.add(job)
        await session.commit()

    yield db_file

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_sync_to_backend_marks_synced_on_success(setup_scraper_db):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"inserted": 1, "duplicated": 0, "errors": []}

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        res = await sync_to_backend("http://backend:8000", "test-key")

    assert res["inserted"] == 1

    from src.db.database import AsyncSessionLocal
    from sqlalchemy.future import select
    async with AsyncSessionLocal() as session:
        job = (await session.execute(select(ScrapedJob))).scalars().first()
        assert job.synced is True


@pytest.mark.asyncio
async def test_sync_to_backend_does_not_mark_on_http_error(setup_scraper_db):
    with patch("httpx.AsyncClient.post", side_effect=httpx.HTTPError("Connection refused")):
        res = await sync_to_backend("http://backend:8000", "test-key")

    assert res["inserted"] == 0
    assert len(res["errors"]) == 1

    from src.db.database import AsyncSessionLocal
    from sqlalchemy.future import select
    async with AsyncSessionLocal() as session:
        job = (await session.execute(select(ScrapedJob))).scalars().first()
        assert job.synced is False


@pytest.mark.asyncio
async def test_sync_expirations_sends_correct_payload():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"expired": 2}

    with patch("httpx.AsyncClient.post", return_value=mock_resp) as mock_post:
        res = await sync_expirations("http://backend:8000", "key", ["https://url1", "https://url2"])

    assert res["expired"] == 2
    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {"expired_urls": ["https://url1", "https://url2"]}
