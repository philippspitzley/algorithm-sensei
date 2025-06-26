from fastapi import APIRouter

from app.api.routes import (
    ai_tutor,
    chapter_points,
    chapters,
    courses,
    login,
    piston_api,
    private,
    stats,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(courses.router)
api_router.include_router(chapters.router)
api_router.include_router(chapter_points.router)
api_router.include_router(utils.router)
api_router.include_router(piston_api.router)
api_router.include_router(ai_tutor.router)
api_router.include_router(stats.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
