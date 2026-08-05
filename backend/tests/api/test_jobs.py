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


# --- Testes do endpoint /locations ---

async def test_list_locations_empty(client):
    """Sem vagas, deve retornar lista vazia."""
    response = await client.get("/api/v1/jobs/locations")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_locations_returns_distinct_cities(client, db_session):
    """Deve retornar cidades distintas das vagas ativas."""
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

    source = Source(name="TestSrc", type="json", base_url="https://test.io", status=SourceStatus.ACTIVE)
    db_session.add(source)
    await db_session.commit()

    # Dois jobs em "São Paulo", um em "Recife"
    for i, city in enumerate(["São Paulo", "São Paulo", "Recife"]):
        job = Job(
            id=_uuid.uuid4(), title=f"Vaga {i}", company="X", location=city,
            modality=JobModality.REMOTE, area=JobArea.TI_SOFTWARE, description="d",
            source_url=f"http://t/{i}", source_id=f"t-{i}",
            posted_at=datetime.now(timezone.utc), source_uuid=source.id,
            status=JobStatus.ACTIVE, is_active=True, is_featured=False,
        )
        db_session.add(job)
    await db_session.commit()

    response = await client.get("/api/v1/jobs/locations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Deve retornar cidades únicas
    assert len(data) == 2
    assert "Recife" in data
    assert "São Paulo" in data


async def test_list_locations_with_q_filter(client, db_session):
    """Deve filtrar cidades pelo parâmetro q."""
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

    source = Source(name="TestSrc2", type="json", base_url="https://test2.io", status=SourceStatus.ACTIVE)
    db_session.add(source)
    await db_session.commit()

    for i, city in enumerate(["São Paulo", "São Bernardo", "Campinas"]):
        job = Job(
            id=_uuid.uuid4(), title=f"Vaga {i}", company="Y", location=city,
            modality=JobModality.REMOTE, area=JobArea.TI_SOFTWARE, description="d",
            source_url=f"http://t2/{i}", source_id=f"t2-{i}",
            posted_at=datetime.now(timezone.utc), source_uuid=source.id,
            status=JobStatus.ACTIVE, is_active=True, is_featured=False,
        )
        db_session.add(job)
    await db_session.commit()

    response = await client.get("/api/v1/jobs/locations?q=São")
    assert response.status_code == 200
    data = response.json()
    assert all("São" in city for city in data)
    assert "Campinas" not in data


async def test_list_locations_inactive_jobs_excluded(client, db_session):
    """Vagas inativas não devem aparecer nas sugestões."""
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

    source = Source(name="TestSrc3", type="json", base_url="https://test3.io", status=SourceStatus.ACTIVE)
    db_session.add(source)
    await db_session.commit()

    job = Job(
        id=_uuid.uuid4(), title="Inativa", company="Z", location="Porto Alegre",
        modality=JobModality.REMOTE, area=JobArea.TI_SOFTWARE, description="d",
        source_url="http://t3/1", source_id="t3-1",
        posted_at=datetime.now(timezone.utc), source_uuid=source.id,
        status=JobStatus.CLOSED, is_active=False, is_featured=False,
    )
    db_session.add(job)
    await db_session.commit()

    response = await client.get("/api/v1/jobs/locations")
    assert response.status_code == 200
    assert "Porto Alegre" not in response.json()
