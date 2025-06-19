import uuid

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import CurrentUser, PaginationParams, SessionDep
from app.api.exceptions import (
    ItemNotFoundError,
    PermissionDeniedError,
)
from app.models import (
    Chapter,
    ChapterCreate,
    ChapterPointPublic,
    ChapterPublic,
    ChaptersPublic,
    ChapterUpdate,
    Message,
)
from app.models.courses import Course

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("/", response_model=ChaptersPublic)
async def get_chapters(
    *,
    session: SessionDep,
    pagination_params: PaginationParams,
    include_count: bool = False,
) -> ChaptersPublic:
    """
    Get chapters.
    """

    skip = pagination_params["skip"]
    limit = pagination_params["limit"]

    if include_count:
        count_statement = select(func.count()).select_from(Chapter)
        count = session.exec(count_statement).one()
    else:
        count = None

    statement = select(Chapter).offset(skip).limit(limit)
    chapters = session.exec(statement).all()
    public_chapters = [ChapterPublic.model_validate(chapter) for chapter in chapters]

    return ChaptersPublic(data=public_chapters, count=count)


@router.get("/{chapter_id}", response_model=ChapterPublic)
async def get_chapter(
    *, session: SessionDep, chapter_id: uuid.UUID, include_chapter_points: bool = True
) -> ChapterPublic:
    """
    Get chapter by ID
    """

    chapter = session.get(Chapter, chapter_id)

    if not chapter:
        raise ItemNotFoundError(item_id=chapter_id, item_name="Chapter")

    if not include_chapter_points:
        chapter = chapter.model_dump(exclude={"chapter_points"})

    return ChapterPublic.model_validate(chapter)


@router.get("/{chapter_id}/chapter-points")
async def get_chapter_points_from_chapter(
    session: SessionDep,
    chapter_id: uuid.UUID,
) -> list[ChapterPointPublic]:
    chapter = session.get(Chapter, chapter_id)

    if not chapter:
        raise ItemNotFoundError(item_id=chapter_id, item_name="Chapter")

    chapter_points = [
        ChapterPointPublic.model_validate(chapter_point)
        for chapter_point in chapter.points
    ]

    return chapter_points


@router.post("/{course_id}", response_model=ChapterPublic)
async def create_chapter(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    chapter_in: ChapterCreate,
    course_id: uuid.UUID,
) -> Chapter:
    """
    Create new chapter.
    """

    if not current_user.is_superuser:
        raise PermissionDeniedError()

    # check if course exists
    course = session.get(Course, course_id)
    if not course:
        raise ItemNotFoundError(item_id=course_id, item_name="Course")

    count_statement = (
        select(func.count()).select_from(Chapter).where(Chapter.course_id == course_id)
    )
    chapter_count = session.scalar(count_statement) or 0

    chapter = Chapter(
        **chapter_in.model_dump(),
        chapter_num=chapter_count + 1,
        course_id=course_id,
    )

    session.add(chapter)
    session.commit()

    return chapter


@router.patch("/{chapter_id}", response_model=ChapterPublic)
async def update_chapter(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    chapter_in: ChapterUpdate,
    chapter_id: uuid.UUID,
) -> ChapterPublic:
    """
    Update chapter.
    """

    if not current_user.is_superuser:
        raise PermissionDeniedError()

    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise ItemNotFoundError(item_id=chapter_id, item_name="Chapter")

    update_dict = chapter_in.model_dump(exclude_unset=True)
    chapter.sqlmodel_update(update_dict)

    session.add(chapter)
    session.commit()
    session.refresh(chapter)

    return ChapterPublic.model_validate(chapter)


@router.delete("/{chapter_id}")
async def delete_chapter(
    *, session: SessionDep, current_user: CurrentUser, chapter_id: uuid.UUID
) -> Message:
    """
    Delete Chapter.
    """

    if not current_user.is_superuser:
        raise PermissionDeniedError()

    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise ItemNotFoundError(item_id=chapter_id, item_name="Chapter")

    session.delete(chapter)
    session.commit()

    return Message(message="👋 Chapter deleted successfully")
