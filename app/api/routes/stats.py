from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.models import (
    Course,
    User,
)
from app.models.stats import Stats

router = APIRouter(prefix="/stats", tags=["stats"])


async def get_user_count(session: SessionDep) -> int:
    count_statement = select(func.count()).select_from(User)
    return session.exec(count_statement).one()


async def get_course_count(session: SessionDep) -> int:
    count_statement = select(func.count()).select_from(Course)
    return session.exec(count_statement).one()


@router.get("/", response_model=Stats)
async def get_public_stats(session: SessionDep) -> dict[str, int]:
    return {
        "total_users": await get_user_count(session),
        "total_courses": await get_course_count(session),
    }
