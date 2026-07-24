from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_admin_key(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")):
    if not settings.ADMIN_API_KEY or x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autorizado")
    return True
