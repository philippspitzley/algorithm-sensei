from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response

# from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import (  # get_current_active_superuser
    CurrentUser,
    SessionDep,
)
from app.api.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    NotFoundError,
    TokenValidationError,
)
from app.api.limiter import limiter
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Message, NewPassword, Token, UserPublic
from app.utils import (
    # uncomment for email support
    # generate_password_reset_token,
    # generate_reset_password_email,
    # send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
@limiter.limit("5/minute")  # type: ignore
def login_access_token(
    response: Response,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise InvalidCredentialsError(detail="Incorrect email or password")
    elif not user.is_active:
        raise InactiveUserError()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    # HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript from accessing the cookie, crucial for security
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",  # TODO: IMPORTANT: use "strict in production"
        secure=False,  # TODO: IMPORTANT: use True in production for HTTPS
    )

    return Token(access_token=access_token)


@router.post("/logout")
@limiter.limit("10/minute")  # type: ignore
def logout(response: Response) -> Message:
    """
    Logout by clearing the access token cookie
    """

    response.delete_cookie(key="access_token")
    return Message(message="Successfully logged out")


@router.post("/login/test-token", response_model=UserPublic)
@limiter.limit("5/minute")  # type: ignore
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
@limiter.limit("3/5minutes")  # type: ignore
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise NotFoundError(
            object_name="User",
            detail=f"{email} does not exist in the system",
        )
    # password_reset_token = generate_password_reset_token(email=email)
    # email_data = generate_reset_password_email(
    #     email_to=user.email, email=email, token=password_reset_token
    # )
    # send_email(
    #     email_to=user.email,
    #     subject=email_data.subject,
    #     html_content=email_data.html_content,
    # )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
@limiter.limit("3/5minutes")  # type: ignore
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise TokenValidationError(detail="Invalid password reset token")
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise NotFoundError(
            object_name="User",
            detail=f"{email} does not exist in the system",
        )
    elif not user.is_active:
        raise InactiveUserError()
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")


# @router.post(
#     "/password-recovery-html-content/{email}",
#     dependencies=[Depends(get_current_active_superuser)],
#     response_class=HTMLResponse,
# )
# def recover_password_html_content(email: str, session: SessionDep) -> Any:
#     """
#     HTML Content for Password Recovery
#     """
#     user = crud.get_user_by_email(session=session, email=email)

#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     password_reset_token = generate_password_reset_token(email=email)
#     email_data = generate_reset_password_email(
#         email_to=user.email, email=email, token=password_reset_token
#     )

#     return HTMLResponse(
#         content=email_data.html_content,
#         headers={"subject:": email_data.subject},
#     )
