from collections.abc import Generator
from typing import Annotated, TypeVar

import jwt
from fastapi import Cookie, Depends, Header, Query
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, SQLModel

from app.api.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    NotFoundError,
    PermissionDeniedError,
    TokenValidationError,
)
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


def get_token_from_cookie_or_header(
    access_token: Annotated[str | None, Cookie()] = None,
    authorization: str | None = Header(None),
) -> str:
    """
    Get token from cookie or authorization header.
    """

    if access_token:
        return access_token
    elif authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")

    raise InvalidCredentialsError(detail="Authentication required")


def get_current_user(
    session: SessionDep, token: Annotated[str, Depends(get_token_from_cookie_or_header)]
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise TokenValidationError(detail="Could not validate credentials")
    user = session.get(User, token_data.sub)
    if not user:
        raise NotFoundError(object_name="User")
    if not user.is_active:
        raise InactiveUserError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
UserRequired = Depends(get_current_user)


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise PermissionDeniedError()
    return current_user


CurrentSuperUser = Annotated[User, Depends(get_current_active_superuser)]
SuperUserRequired = Depends(get_current_active_superuser)


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
