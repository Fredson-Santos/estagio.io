from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Job


async def find_existing_urls(session: AsyncSession, urls: list[str]) -> set[str]:
    """Retorna o conjunto de source_url que ja existem no banco (query unica IN)."""
    if not urls:
        return set()
    result = await session.execute(
        select(Job.source_url).where(Job.source_url.in_(urls))
    )
    return {row[0] for row in result.all()}
