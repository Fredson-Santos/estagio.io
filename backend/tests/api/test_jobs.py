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


async def test_read_jobs_with_area_filter(client, seed_job):
    response = await client.get("/api/v1/jobs?area=TI_SOFTWARE")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for item in data["items"]:
        assert item["area"] == "TI_SOFTWARE"


async def test_read_jobs_with_modality_filter(client):
    response = await client.get("/api/v1/jobs?modality=REMOTE")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for item in data["items"]:
        assert item["modality"] == "REMOTE"


async def test_read_jobs_with_invalid_area(client):
    response = await client.get("/api/v1/jobs?area=INVALIDO")
    assert response.status_code == 422


async def test_read_jobs_with_wildcard_in_q(client):
    response = await client.get("/api/v1/jobs?q=%25%25%25%25%25")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
