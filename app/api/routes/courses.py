import uuid

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import CurrentUser, PaginationParams, SessionDep
from app.api.exceptions import ItemNotFoundError, PermissionDeniedError
from app.models import (
    Course,
    CourseCreate,
    CoursePublic,
    CoursesPublic,
    CourseUpdate,
    Message,
)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=CoursesPublic)
async def get_courses(
    *,
    session: SessionDep,
    pagination_params: PaginationParams,
    include_count: bool = False,
) -> CoursesPublic:
    """
    Retrieve courses.
    """

    skip = pagination_params["skip"]
    limit = pagination_params["limit"]

    if include_count:
        count_statement = select(func.count()).select_from(Course)
        count = session.exec(count_statement).one()
    else:
        count = None

    statement = select(Course).offset(skip).limit(limit)
    courses = session.exec(statement).all()
    public_courses = [CoursePublic.model_validate(course) for course in courses]

    return CoursesPublic(data=public_courses, count=count)


@router.get("/{course_id}", response_model=CoursePublic)
async def get_course(
    session: SessionDep, course_id: uuid.UUID, include_chapters: bool = True
) -> CoursePublic:
    """
    Get course by ID.
    """

    course = session.get(Course, course_id)

    if not course:
        raise ItemNotFoundError(item_id=course_id, item_name="Course")

    if not include_chapters:
        course = course.model_dump(exclude={"chapters"})

    return CoursePublic.model_validate(course)


@router.post("/", response_model=CoursePublic)
async def create_course(
    *, session: SessionDep, current_user: CurrentUser, course_in: CourseCreate
) -> CoursePublic:
    """
    Create new course.
    """

    if not current_user.is_superuser:
        raise PermissionDeniedError()

    course = Course.model_validate(course_in)

    session.add(course)
    session.commit()
    session.refresh(course)

    return CoursePublic.model_validate(course)


@router.patch("/{course_id}", response_model=CoursePublic)
async def update_course(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    course_id: uuid.UUID,
    course_in: CourseUpdate,
) -> CoursePublic:
    """
    Update an course.
    """
    course = session.get(Course, course_id)

    if not course:
        raise ItemNotFoundError(item_id=course_id, item_name="Course")
    if not current_user.is_superuser:
        raise PermissionDeniedError()

    update_dict = course_in.model_dump(exclude_unset=True)
    course.sqlmodel_update(update_dict)

    session.add(course)
    session.commit()
    session.refresh(course)

    return CoursePublic.model_validate(course)


@router.delete("/{course_id}")
async def delete_course(
    session: SessionDep, current_user: CurrentUser, course_id: uuid.UUID
) -> Message:
    """
    Delete a course.
    """
    course = session.get(Course, course_id)

    if not course:
        raise ItemNotFoundError(item_id=course_id, item_name="Course")
    if not current_user.is_superuser:
        raise PermissionDeniedError()

    session.delete(course)
    session.commit()

    return Message(message="👋 Course deleted successfully")
