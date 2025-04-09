from collections.abc import Generator
from enum import Enum
from typing import Annotated, Any, TypeVar
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, SQLModel

from app.api.exceptions import ItemNotFoundError, NotFoundError, PermissionDeniedError
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User

ModelT = TypeVar("ModelT", bound=SQLModel)

# Constants
PAGINATION_LIMIT_DEFAULT: int = 50
PAGINATION_LIMIT_MAX: int = 100

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise NotFoundError(object_name="User")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise PermissionDeniedError()
    return current_user


def pagination_params(
    skip: int = Query(
        0,
        ge=0,
        le=PAGINATION_LIMIT_MAX - 1,
        description="Number of items to skip.",
    ),
    limit: int = Query(
        PAGINATION_LIMIT_DEFAULT,
        ge=1,
        le=PAGINATION_LIMIT_MAX,
        description="Maximum number of items to return.",
    ),
) -> dict[str, int]:
    return {"skip": skip, "limit": limit}


PaginationParams = Annotated[dict[str, int], Depends(pagination_params)]


class ModelClassName(str, Enum):
    User = "User"
    Course = "Course"
    Chapter = "Chapter"
    # Add other model class names here as needed


def get_item_with_permissions(model_class_name: ModelClassName):
    """
    Factory function that creates a dependency for retrieving an item by ID
    with permission checking.

    Args:
        model_class_name: The name of the model class to use for retrieval
    """

    def _get_item(
        session: SessionDep,
        current_user: CurrentUser,
        item_id: UUID,
    ) -> Any:
        # Import model class at runtime to avoid circular imports
        from app.models import (
            Chapter,
            Course,
        )  # Add other models as needed  # noqa: I001

        # Map string names to actual classes
        model_map: dict[str, type] = {
            "Course": Course,
            "Chapter": Chapter,
            "User": User,
            # Add other models here
        }

        model_class = model_map.get(model_class_name)
        if not model_class:
            raise ValueError(f"Unknown model class: {model_class_name}")

        item = session.get(model_class, item_id)
        if not item:
            raise ItemNotFoundError(item_id=item_id, item_name=model_class_name)

        # Check if item has owner_id attribute
        if (
            hasattr(item, "owner_id")
            and not current_user.is_superuser
            and item.owner_id != current_user.id
        ):
            raise PermissionDeniedError()

        return item

    return _get_item
