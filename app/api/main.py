from fastapi import APIRouter

from app.core.config import settings

from .routes import chapter_points, chapters, courses, login, private, users, utils

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(courses.router)
api_router.include_router(chapters.router)
api_router.include_router(chapter_points.router)
api_router.include_router(utils.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
