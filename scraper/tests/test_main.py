from datetime import datetime, timedelta, timezone
import uuid
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from src.main import create_app, _cleanup_job, _check_expired_job
from src.db.models import ScrapedJob, Source
from estagio_shared.taxonomy import JobArea, JobModality, SourceStatus


@pytest.fixture
def client(monkeypatch):
    from src.config import settings
    monkeypatch.setattr(settings, "BACKEND_API_KEY", "secret-key")
    app = create_app()
    return TestClient(app)


def test_run_endpoint_requires_auth(client):
    response = client.post("/run")
    assert response.status_code == 401


def test_run_endpoint_accepts_valid_key(client):
    with patch("src.main._etl_job", new_callable=AsyncMock):
        response = client.post("/run", headers={"X-Admin-Key": "secret-key"})
    assert response.status_code == 202
    assert response.json()["status"] == "triggered"


def test_run_endpoint_rejects_wrong_key(client):
    response = client.post("/run", headers={"X-Admin-Key": "wrong-key"})
    assert response.status_code == 401


def test_run_endpoint_when_key_empty_returns_503(monkeypatch):
    from src.config import settings
    monkeypatch.setattr(settings, "BACKEND_API_KEY", "")
    app = create_app()
    client = TestClient(app)
    response = client.post("/run", headers={"X-Admin-Key": "any-key"})
    assert response.status_code == 503
    assert response.json()["detail"] == "BACKEND_API_KEY não configurada"


@pytest.mark.asyncio
async def test_cleanup_job_deletes_old_synced(tmp_path, monkeypatch):
    from src.config import settings
    db_file = tmp_path / "scraper_main_test.db"
    monkeypatch.setattr(settings, "SCRAPER_DB_PATH", str(db_file))

    from src.db.database import engine, Base, AsyncSessionLocal
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        source = Source(name="Test", type="json", base_url="https://test.io", status=SourceStatus.ACTIVE)
        session.add(source)
        await session.commit()

        now = datetime.now(timezone.utc)
        old_date = now - timedelta(days=35)

        # 1. Antiga + synced (deve ser deletada)
        j1 = ScrapedJob(
            id=uuid.uuid4(), title="J1", company="C", modality=JobModality.REMOTE,
            area=JobArea.TI_SOFTWARE, source_url="https://1", source_id="1",
            source_uuid=source.id, synced=True, scraped_at=old_date
        )
        # 2. Recente + synced (deve permanecer)
        j2 = ScrapedJob(
            id=uuid.uuid4(), title="J2", company="C", modality=JobModality.REMOTE,
            area=JobArea.TI_SOFTWARE, source_url="https://2", source_id="2",
            source_uuid=source.id, synced=True, scraped_at=now
        )
        # 3. Antiga + NOT synced (deve permanecer)
        j3 = ScrapedJob(
            id=uuid.uuid4(), title="J3", company="C", modality=JobModality.REMOTE,
            area=JobArea.TI_SOFTWARE, source_url="https://3", source_id="3",
            source_uuid=source.id, synced=False, scraped_at=old_date
        )
        session.add_all([j1, j2, j3])
        await session.commit()

    await _cleanup_job()

    from sqlalchemy.future import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ScrapedJob))
        jobs = result.scalars().all()
        urls = [j.source_url for j in jobs]
        assert "https://1" not in urls
        assert "https://2" in urls
        assert "https://3" in urls


@pytest.mark.asyncio
async def test_check_expired_job_calls_sync_expirations(tmp_path, monkeypatch):
    from src.config import settings
    db_file = tmp_path / "scraper_expired_test.db"
    monkeypatch.setattr(settings, "SCRAPER_DB_PATH", str(db_file))

    from src.db.database import engine, Base, AsyncSessionLocal
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        source = Source(name="Test", type="json", base_url="https://test.io", status=SourceStatus.ACTIVE)
        session.add(source)
        await session.commit()

        job = ScrapedJob(
            id=uuid.uuid4(), title="J1", company="C", modality=JobModality.REMOTE,
            area=JobArea.TI_SOFTWARE, source_url="https://test.io/expired", source_id="1",
            source_uuid=source.id, synced=True
        )
        session.add(job)
        await session.commit()

    with patch("src.main.check_expired_urls", return_value=["https://test.io/expired"]) as mock_check, \
         patch("src.main.sync_expirations", return_value={"expired": 1}) as mock_sync:
        await _check_expired_job()

    mock_check.assert_called_once()
    mock_sync.assert_called_once()
