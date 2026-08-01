import asyncio
import logging
from urllib.parse import urlparse
import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}


async def _check_single_url(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        resp = await client.head(url, headers=HEADERS, timeout=10.0, follow_redirects=False)
        if resp.status_code == 405:
            resp = await client.get(url, headers=HEADERS, timeout=10.0, follow_redirects=False)

        if resp.status_code in (404, 410, 403):
            return url

        if resp.status_code in (301, 302, 303, 307, 308):
            redirect_target = resp.headers.get("location", "")
            if redirect_target:
                orig_domain = urlparse(url).netloc
                target_domain = urlparse(redirect_target).netloc
                if target_domain and target_domain != orig_domain:
                    return url
    except (httpx.ConnectError, httpx.TimeoutException):
        pass
    except Exception as exc:
        logger.debug("Erro ao checar URL %s: %s", url, exc)

    return None


async def check_expired_urls(urls: list[str], concurrency: int = 10) -> list[str]:
    """Verifica lista de URLs e retorna aquelas que expiraram na origem."""
    if not urls:
        return []

    semaphore = asyncio.Semaphore(concurrency)
    expired = []

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
        async def worker(u):
            async with semaphore:
                res = await _check_single_url(client, u)
                if res:
                    expired.append(res)

        await asyncio.gather(*(worker(u) for u in urls))

    return expired
