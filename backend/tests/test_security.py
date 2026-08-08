import pytest
from app.core.config import settings

TEST_KEY = "test_secret_key_12345"


@pytest.mark.asyncio
async def test_verify_admin_key_success(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_API_KEY", TEST_KEY)
    response = await client.get("/api/v1/admin/stats", headers={"X-Admin-Key": TEST_KEY})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_verify_admin_key_missing(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_API_KEY", TEST_KEY)
    response = await client.get("/api/v1/admin/stats")
    assert response.status_code == 401
    assert response.json()["detail"] == "Não autorizado"


@pytest.mark.asyncio
async def test_verify_admin_key_wrong(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_API_KEY", TEST_KEY)
    response = await client.get("/api/v1/admin/stats", headers={"X-Admin-Key": "wrong_key_999"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Não autorizado"


@pytest.mark.asyncio
async def test_verify_admin_key_not_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_API_KEY", None)
    response = await client.get("/api/v1/admin/stats", headers={"X-Admin-Key": "any_key"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Não autorizado"
