import uuid


async def test_read_jobs(client):
    response = await client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert isinstance(data["items"], list)


async def test_read_job_not_found(client):
    random_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/jobs/{random_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Vaga não encontrada"}


async def test_read_jobs_with_q(client):
    response = await client.get("/api/v1/jobs?q=desenvolvedor")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


async def test_read_jobs_with_modality_filter(client):
    response = await client.get("/api/v1/jobs?modality=REMOTE")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for item in data["items"]:
        assert item["modality"] == "REMOTE"


async def test_read_jobs_with_wildcard_in_q(client):
    response = await client.get("/api/v1/jobs?q=%25%25%25%25%25")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


async def test_featured_filter_returns_only_featured(client, seed_featured_jobs):
    response = await client.get("/api/v1/jobs?featured=true")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    # Seed cria 2 vagas em destaque e 1 comum
    assert data["total"] == 2
    for item in data["items"]:
        assert item["is_featured"] is True


async def test_featured_filter_count_without_flag(client, seed_featured_jobs):
    # Sem o filtro featured, todas as 3 vagas ativas devem retornar
    response = await client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    featured_count = sum(1 for item in data["items"] if item["is_featured"])
    assert featured_count == 2


async def test_read_jobs_ordered_by_posted_at_desc(db_session, client):
    from datetime import datetime, timedelta, timezone
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

    source = Source(name="Test", type="json", base_url="https://test.io", status=SourceStatus.ACTIVE)
    db_session.add(source)
    await db_session.commit()

    now = datetime.now(timezone.utc)
    # Vaga 1 (mais antiga, mas em destaque)
    job1 = Job(
        id=uuid.uuid4(), title="Vaga Antiga Destaque", company="A", location="SP",
        modality=JobModality.REMOTE, area=JobArea.TI_SOFTWARE, description="desc",
        source_url="http://1", source_id="1", posted_at=now - timedelta(days=2),
        source_uuid=source.id, status=JobStatus.ACTIVE, is_active=True, is_featured=True
    )
    # Vaga 2 (mais recente, não destaque)
    job2 = Job(
        id=uuid.uuid4(), title="Vaga Recente Comum", company="B", location="SP",
        modality=JobModality.REMOTE, area=JobArea.TI_SOFTWARE, description="desc",
        source_url="http://2", source_id="2", posted_at=now - timedelta(days=1),
        source_uuid=source.id, status=JobStatus.ACTIVE, is_active=True, is_featured=False
    )
    db_session.add_all([job1, job2])
    await db_session.commit()

    response = await client.get("/api/v1/jobs")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 2
    # A vaga 2 (mais recente) deve vir em primeiro lugar
    assert items[0]["title"] == "Vaga Recente Comum"
    assert items[1]["title"] == "Vaga Antiga Destaque"


async def test_register_click_success(client, seed_job, db_session):
    response = await client.post(f"/api/v1/jobs/{seed_job.id}/click", headers={"Referer": "https://estagio.io"})
    assert response.status_code == 204

    from sqlalchemy.future import select
    from app.db.models import JobClick
    result = await db_session.execute(select(JobClick).where(JobClick.job_id == seed_job.id))
    clicks = result.scalars().all()
    assert len(clicks) == 1
    assert clicks[0].referrer == "https://estagio.io"


async def test_register_click_not_found(client):
    random_id = str(uuid.uuid4())
    response = await client.post(f"/api/v1/jobs/{random_id}/click")
    assert response.status_code == 404


