from fastapi import APIRouter
from app.api.v1.endpoints import jobs, admin

api_router = APIRouter()
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
