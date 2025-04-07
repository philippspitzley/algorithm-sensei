import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Course,
    CourseCreate,
    CoursePublic,
    CoursesPublic,
    CourseUpdate,
    Message,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=CoursesPublic)
def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve items.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Course)
        count = session.exec(count_statement).one()
        statement = select(Course).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Course)
            .where(Course.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Course)
            .where(Course.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()

    return CoursesPublic(data=items, count=count)


@router.get("/{item_id}", response_model=CoursePublic)
def read_item(
    session: SessionDep, current_user: CurrentUser, item_id: uuid.UUID
) -> Any:
    """
    Get item by ID.
    """
    item = session.get(Course, item_id)
    if not item:
        raise HTTPException(
            status_code=404, detail=f"Item with id '{item_id}' not found"
        )
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=CoursePublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: CourseCreate
) -> Any:
    """
    Create new item.
    """
    item = Course.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{item_id}", response_model=CoursePublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_id: uuid.UUID,
    item_in: CourseUpdate,
) -> Any:
    """
    Update an item.
    """
    item = session.get(Course, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, item_id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = session.get(Course, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")
