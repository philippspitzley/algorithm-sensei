import uuid

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import CurrentUser, PaginationParams, SessionDep
from app.api.exceptions import (
    ItemAlreadyExistsError,
    ItemNotFoundError,
    PermissionDeniedError,
)
from app.models import (
    Chapter,
    ChapterPoint,
    ChapterPointCreate,
    ChapterPointPublic,
    ChapterPointsPublic,
    ChapterPointUpdate,
    Message,
)

router = APIRouter(prefix="/chapterPoints", tags=["chapter_points"])


@router.get("/", response_model=ChapterPointsPublic)
async def get_chapter_points(
    *,
    session: SessionDep,
    pagination_params: PaginationParams,
    include_count: bool = False,
) -> ChapterPointsPublic:
    """
    Get chapter points.
    """

    skip = pagination_params["skip"]
    limit = pagination_params["limit"]

    if include_count:
        count_statement = select(func.count()).select_from(ChapterPoint)
        count = session.exec(count_statement).one()
    else:
        count = None

    statement = select(ChapterPoint).offset(skip).limit(limit)
    chapter_points = session.exec(statement).all()
    public_chapter_points = [
        ChapterPointPublic.model_validate(chapter_point)
        for chapter_point in chapter_points
    ]

    return ChapterPointsPublic(data=public_chapter_points, count=count)


@router.get("/{chapter_point_id}", response_model=ChapterPointPublic)
async def get_chapter(
    *, session: SessionDep, chapter_point_id: uuid.UUID
) -> ChapterPointPublic:
    """
    Get chapter point by ID
    """
    chapter_point = session.get(ChapterPoint, chapter_point_id)

    if not chapter_point:
        raise ItemNotFoundError(item_id=chapter_point_id, item_name="Chapter Point")

    return ChapterPointPublic.model_validate(chapter_point)


@router.post("/", response_model=ChapterPointPublic)
async def create_chapter_point(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    chapter_point_in: ChapterPointCreate,
    chapter_id: uuid.UUID,
) -> ChapterPointPublic:
    """
    Create new chapter point.
    """

    if not current_user.is_superuser:
        raise PermissionDeniedError()

    # check if chapter exists
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise ItemNotFoundError(item_id=chapter_id, item_name="Chapter")

    # check if chapter_point_num already exists
    chapter_point_num = chapter_point_in.chapter_point_num
    chapter_point_nums = [point.chapter_point_num for point in chapter.points]
    if chapter_point_num in chapter_point_nums:
        raise ItemAlreadyExistsError(item_name=f"Chapter Point {chapter_point_num}")

    # create new chapter_point
    chapter_point = ChapterPoint.model_validate(
        chapter_point_in, update={"chapter_id": chapter_id}
    )

    session.add(chapter_point)
    session.commit()
    session.refresh(chapter_point)

    return ChapterPointPublic.model_validate(chapter_point)


@router.patch("/{chapter_point_id}", response_model=ChapterPointPublic)
async def update_chapter_point(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    chapter_point_in: ChapterPointUpdate,
    chapter_point_id: uuid.UUID,
) -> ChapterPointPublic:
    """
    Update chapter point.
    """

    if not current_user.is_superuser:
        raise PermissionDeniedError()

    chapter_point = session.get(ChapterPoint, chapter_point_id)
    if not chapter_point:
        raise ItemNotFoundError(item_id=chapter_point_id, item_name="Chapter Point")

    chapter_point_dict = chapter_point_in.model_dump(exclude_unset=True)
    chapter_point.sqlmodel_update(chapter_point_dict)

    session.add(chapter_point)
    session.commit()
    session.refresh(chapter_point)

    return ChapterPointPublic.model_validate(chapter_point)


@router.delete("/{chapter_point_id}")
async def delete_chapter_point(
    *, session: SessionDep, current_user: CurrentUser, chapter_point_id: uuid.UUID
) -> Message:
    """
    Delete Chapter Point.
    """

    if not current_user.is_superuser:
        raise PermissionDeniedError()

    chapter_point = session.get(ChapterPoint, chapter_point_id)
    if not chapter_point:
        raise ItemNotFoundError(item_id=chapter_point_id, item_name="Chapter Point")

    session.delete(chapter_point)
    session.commit()

    return Message(message="👋 Chapter Point deleted successfully")
