import pytest
from unittest.mock import patch, MagicMock
import httpx
from src.services.health_check import check_expired_urls


@pytest.mark.asyncio
async def test_check_expired_urls_marks_404():
    mock_resp = MagicMock()
    mock_resp.status_code = 404

    with patch("httpx.AsyncClient.head", return_value=mock_resp):
        expired = await check_expired_urls(["https://gupy.io/job/404"])

    assert expired == ["https://gupy.io/job/404"]


@pytest.mark.asyncio
async def test_check_expired_urls_marks_410():
    mock_resp = MagicMock()
    mock_resp.status_code = 410

    with patch("httpx.AsyncClient.head", return_value=mock_resp):
        expired = await check_expired_urls(["https://gupy.io/job/410"])

    assert expired == ["https://gupy.io/job/410"]


@pytest.mark.asyncio
async def test_check_expired_urls_ignores_timeout():
    with patch("httpx.AsyncClient.head", side_effect=httpx.TimeoutException("Timeout")):
        expired = await check_expired_urls(["https://gupy.io/job/timeout"])

    assert expired == []


@pytest.mark.asyncio
async def test_check_expired_urls_marks_redirect_to_different_domain():
    mock_resp = MagicMock()
    mock_resp.status_code = 302
    mock_resp.headers = {"location": "https://otherdomain.com/expired"}

    with patch("httpx.AsyncClient.head", return_value=mock_resp):
        expired = await check_expired_urls(["https://gupy.io/job/302"])

    assert expired == ["https://gupy.io/job/302"]
