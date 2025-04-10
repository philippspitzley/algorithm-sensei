import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    PaginationParams,
    SessionDep,
    get_current_active_superuser,
)
from app.api.exceptions import (
    EmailValidationError,
    ItemAlreadyExistsError,
    ItemNotFoundError,
    PasswordValidationError,
    PermissionDeniedError,
)
from app.core.security import get_password_hash, verify_password
from app.models import (
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

# uncomment next two lines for email support
# from app.utils import generate_new_account_email, send_email
# from app.core.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def get_users(
    session: SessionDep,
    pagination_params: PaginationParams,
    include_count: bool = False,
) -> UsersPublic:
    """
    Retrieve users.
    """
    skip = pagination_params["skip"]
    limit = pagination_params["limit"]

    # Get paginated users
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    public_users = [UserPublic.model_validate(user) for user in users]

    count = None
    if include_count:
        count_statement = select(func.count()).select_from(User)
        count = session.exec(count_statement).one()

    return UsersPublic(data=public_users, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise ItemAlreadyExistsError(item_name=user_in.email)

    user = crud.create_user(session=session, user_create=user_in)

    # if settings.emails_enabled and user_in.email:
    #     email_data = generate_new_account_email(
    #         email_to=user_in.email, username=user_in.email, password=user_in.password
    #     )
    #     send_email(
    #         email_to=user_in.email,
    #         subject=email_data.subject,
    #         html_content=email_data.html_content,
    #     )

    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise ItemAlreadyExistsError(item_name=user_in.email)

    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """

    if not verify_password(body.current_password, current_user.hashed_password):
        raise PasswordValidationError("Incorrect password")
    if body.current_password == body.new_password:
        raise PasswordValidationError(
            "New password cannot be the same as the current one"
        )

    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password

    session.add(current_user)
    session.commit()
    return Message(message="🔐 Password successfully updated ")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise PermissionDeniedError(
            detail="Super users are not allowed to delete themselves",
        )
    session.delete(current_user)
    session.commit()

    return Message(message="👋 User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)

    if user:
        raise EmailValidationError(detail=f"Email '{user_in.email}' already exists")

    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)

    return user


@router.get("/{user_id}", response_model=UserPublic)
def get_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user

    if not current_user.is_superuser:
        raise PermissionDeniedError(
            detail="The user doesn't have enough privileges",
        )

    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise ItemNotFoundError(item_id=user_id, item_name="User")

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise ItemAlreadyExistsError(item_name="User")

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)

    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise ItemNotFoundError(item_id=user_id, item_name="User")
    if user == current_user:
        raise PermissionDeniedError(
            detail="Super users are not allowed to delete themselves",
        )

    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
