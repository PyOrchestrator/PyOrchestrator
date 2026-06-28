from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/info")
async def system_info():
    return {
        "name": "PyOrchestrator",
        "version": settings.app_version,
        "environment": settings.app_env,
    }
