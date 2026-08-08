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


async def test_read_jobs_q_title_match_comes_first(client, db_session):
    """Vagas com o termo no título devem aparecer antes das que têm o termo apenas na empresa."""
    import uuid as _uuid
    from datetime import datetime, timedelta, timezone
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

    source = Source(name="RelevanceTest", type="json", base_url="https://rel.io", status=SourceStatus.ACTIVE)
    db_session.add(source)
    await db_session.commit()

    now = datetime.now(timezone.utc)
    # Vaga mais recente, mas o termo "Marketing" está só na empresa
    job_company_match = Job(
        id=_uuid.uuid4(), title="Estágio Comercial", company="Marketing Corp",
        location="SP", modality=JobModality.REMOTE, area=JobArea.MARKETING,
        description="desc", source_url="http://rel/1", source_id="rel-1",
        posted_at=now, source_uuid=source.id,
        status=JobStatus.ACTIVE, is_active=True, is_featured=False,
    )
    # Vaga mais antiga, mas o termo "Marketing" está no título
    job_title_match = Job(
        id=_uuid.uuid4(), title="Estágio em Marketing Digital", company="Outra Empresa",
        location="SP", modality=JobModality.REMOTE, area=JobArea.MARKETING,
        description="desc", source_url="http://rel/2", source_id="rel-2",
        posted_at=now - timedelta(days=5), source_uuid=source.id,
        status=JobStatus.ACTIVE, is_active=True, is_featured=False,
    )
    db_session.add_all([job_company_match, job_title_match])
    await db_session.commit()

    response = await client.get("/api/v1/jobs?q=Marketing")
    assert response.status_code == 200
    items = response.json()["items"]
    # Deve retornar as 2 vagas
    titles = [i["title"] for i in items]
    assert "Estágio em Marketing Digital" in titles
    assert "Estágio Comercial" in titles
    # A vaga com Marketing no título deve vir PRIMEIRO
    assert titles.index("Estágio em Marketing Digital") < titles.index("Estágio Comercial"), (
        f"Esperado 'Estágio em Marketing Digital' antes de 'Estágio Comercial', mas a ordem foi: {titles}"
    )


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


# --- Testes do endpoint /platforms ---

async def test_list_platforms_empty(client):
    """Sem vagas ativas, deve retornar lista vazia."""
    response = await client.get("/api/v1/jobs/platforms")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_platforms_returns_aggregated(client, db_session):
    """Deve agregar contagens por plataforma normalizada."""
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

    # 3 sources distintas que devem agregar para 2 plataformas (Gupy x2 + Eureca x1)
    gupy1 = Source(name="bmw.gupy.io", type="json", base_url="https://bmw.gupy.io", status=SourceStatus.ACTIVE)
    gupy2 = Source(name="bauducco.gupy.io", type="json", base_url="https://bauducco.gupy.io", status=SourceStatus.ACTIVE)
    eureca = Source(name="eureca.me", type="json", base_url="https://eureca.me", status=SourceStatus.ACTIVE)
    db_session.add_all([gupy1, gupy2, eureca])
    await db_session.commit()
    await db_session.refresh(gupy1)
    await db_session.refresh(gupy2)
    await db_session.refresh(eureca)

    now = datetime.now(timezone.utc)
    jobs_specs = [
        (gupy1, "http://j/1"),
        (gupy1, "http://j/2"),
        (gupy2, "http://j/3"),
        (eureca, "http://j/4"),
    ]
    for i, (src, url) in enumerate(jobs_specs):
        job = Job(
            id=_uuid.uuid4(), title=f"Vaga {i}", company="X", location="SP",
            modality=JobModality.REMOTE, area=JobArea.TI_SOFTWARE, description="d",
            source_url=url, source_id=f"src-{i}", posted_at=now,
            source_uuid=src.id, status=JobStatus.ACTIVE, is_active=True, is_featured=False,
        )
        db_session.add(job)
    await db_session.commit()

    response = await client.get("/api/v1/jobs/platforms")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Deriva dicionário slug -> count
    by_slug = {item["slug"]: item for item in data}
    assert "gupy" in by_slug, f"slug 'gupy' ausente em {by_slug.keys()}"
    assert by_slug["gupy"]["name"] == "Gupy"
    assert by_slug["gupy"]["count"] == 3, f"esperado 3 vagas gupy, veio {by_slug['gupy']['count']}"

    assert "eureca" in by_slug
    assert by_slug["eureca"]["name"] == "Eureca"
    assert by_slug["eureca"]["count"] == 1

    # Ordenação: Gupy (3) deve vir antes de Eureca (1)
    assert data[0]["slug"] == "gupy"
    assert data[1]["slug"] == "eureca"


async def test_list_platforms_excludes_inactive_jobs(client, db_session):
    """Vagas inativas não devem contribuir para a contagem de plataformas."""
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

    # Source só com vagas inativas — não deve aparecer na resposta
    src_inactive = Source(name="vaga-ja.com", type="json", base_url="https://vaga-ja.com", status=SourceStatus.ACTIVE)
    db_session.add(src_inactive)
    await db_session.commit()
    await db_session.refresh(src_inactive)

    job = Job(
        id=_uuid.uuid4(), title="Inativa", company="Y", location="RJ",
        modality=JobModality.REMOTE, area=JobArea.TI_SOFTWARE, description="d",
        source_url="http://inv/1", source_id="inv-1",
        posted_at=datetime.now(timezone.utc), source_uuid=src_inactive.id,
        status=JobStatus.CLOSED, is_active=False, is_featured=False,
    )
    db_session.add(job)
    await db_session.commit()

    response = await client.get("/api/v1/jobs/platforms")
    assert response.status_code == 200
    data = response.json()

    # Plataforma 'vaga-ja' não deve aparecer pois a única vaga está inativa
    slugs = [item["slug"] for item in data]
    assert "vaga-ja" not in slugs


async def test_read_jobs_with_platform_filter(client, db_session):
    """Filtra vagas por plataforma via parâmetro ?platform=gupy."""
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

    gupy = Source(name="bmw.gupy.io", type="json", base_url="https://bmw.gupy.io", status=SourceStatus.ACTIVE)
    eureca = Source(name="eureca.me", type="json", base_url="https://eureca.me", status=SourceStatus.ACTIVE)
    db_session.add_all([gupy, eureca])
    await db_session.commit()
    await db_session.refresh(gupy)
    await db_session.refresh(eureca)

    now = datetime.now(timezone.utc)
    # 2 vagas Gupy + 1 vaga Eureca
    for i, (src, url) in enumerate([
        (gupy, "http://jpf/1"),
        (gupy, "http://jpf/2"),
        (eureca, "http://jpf/3"),
    ]):
        job = Job(
            id=_uuid.uuid4(), title=f"Vaga {i}", company="X", location="SP",
            modality=JobModality.REMOTE, area=JobArea.TI_SOFTWARE, description="d",
            source_url=url, source_id=f"jpf-{i}", posted_at=now,
            source_uuid=src.id, status=JobStatus.ACTIVE, is_active=True, is_featured=False,
        )
        db_session.add(job)
    await db_session.commit()

    response = await client.get("/api/v1/jobs?platform=gupy")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2, f"esperado 2 vagas gupy, veio {data['total']}"
    # Sem o filtro retornaria 3 vagas (2 gupy + 1 eureca); o filtro removeu eureca.
    assert len(data["items"]) == 2


async def test_read_jobs_with_platform_filter_no_match(client, db_session):
    """Plataforma inexistente deve retornar lista vazia."""
    import uuid as _uuid
    from datetime import datetime, timezone
    from app.db.models import Job, Source
    from estagio_shared.taxonomy import JobArea, JobModality, JobStatus, SourceStatus

    gupy = Source(name="gupy.io", type="json", base_url="https://gupy.io", status=SourceStatus.ACTIVE)
    db_session.add(gupy)
    await db_session.commit()
    await db_session.refresh(gupy)

    job = Job(
        id=_uuid.uuid4(), title="Vaga", company="X", location="SP",
        modality=JobModality.REMOTE, area=JobArea.TI_SOFTWARE, description="d",
        source_url="http://jnof/1", source_id="jnof-1",
        posted_at=datetime.now(timezone.utc), source_uuid=gupy.id,
        status=JobStatus.ACTIVE, is_active=True, is_featured=False,
    )
    db_session.add(job)
    await db_session.commit()

    response = await client.get("/api/v1/jobs?platform=plataforma-inexistente")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
