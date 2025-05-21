import uuid

from fastapi import APIRouter
from sqlmodel import func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    PaginationParams,
    SessionDep,
    SuperUserRequired,
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
from app.models.courses import Course
from app.models.user_courses import (
    UserCourse,
    UserCourseCreate,
    UserCourseFinishedChapter,
    UserCoursePublic,
    UserCourseUpdate,
)

# uncomment next two lines for email support
# from app.utils import generate_new_account_email, send_email
# from app.core.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserPublic)
async def register_user(session: SessionDep, user_in: UserRegister) -> UserPublic:
    """
    Create new user without the need to be logged in.
    """

    user = crud.get_user_by_email(session=session, email=user_in.email)

    if user:
        raise EmailValidationError(detail=f"Email '{user_in.email}' already exists")

    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)

    return UserPublic.model_validate(user)


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser) -> UserPublic:
    """
    Get current user.
    """

    return UserPublic.model_validate(current_user)


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> UserPublic:
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

    return UserPublic.model_validate(current_user)


@router.patch("/me/password", response_model=Message)
async def update_password_me(
    *, session: SessionDep, password_in: UpdatePassword, current_user: CurrentUser
) -> Message:
    """
    Update own password.
    """

    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise PasswordValidationError(
            "Incorrect password. Make sure your current password is correct."
        )
    if password_in.current_password == password_in.new_password:
        raise PasswordValidationError(
            "New password cannot be the same as the current one"
        )

    hashed_password = get_password_hash(password_in.new_password)
    current_user.hashed_password = hashed_password

    session.add(current_user)
    session.commit()
    return Message(message="🔐 Password successfully updated ")


@router.delete("/me", response_model=Message)
async def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Message:
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


@router.get("/me/courses", response_model=UserCoursePublic | list[UserCoursePublic])
async def get_my_courses(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    course_id: uuid.UUID | None = None,
) -> list[UserCoursePublic] | UserCoursePublic:
    """
    Get enrolled courses.
    """

    course_statement = select(UserCourse).where(
        UserCourse.user_id == current_user.id,
        UserCourse.course_id == course_id,
    )

    courses_statement = select(UserCourse).where(
        UserCourse.user_id == current_user.id,
    )

    statement = course_statement if course_id else courses_statement

    user_courses = session.exec(statement).all()

    public_user_courses = [
        UserCoursePublic.model_validate(user_course) for user_course in user_courses
    ]

    if len(public_user_courses) == 1:
        return public_user_courses[0]

    return public_user_courses


@router.post("/me/courses/{course_id}", response_model=UserCourse)
async def enroll_course(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    course_id: uuid.UUID,
) -> UserCourse:
    """
    Enroll new course.
    """

    # check if course exists
    course = session.get(Course, course_id)
    if not course:
        raise ItemNotFoundError(item_id=course_id, item_name="Course")

    # check if course already in UserCourse
    statement = select(UserCourse).where(UserCourse.course_id == course_id)
    user_course_exists = session.exec(statement).first()
    if user_course_exists:
        raise ItemAlreadyExistsError(item_name="User course")

    user_course_in = UserCourseCreate(user_id=current_user.id, course_id=course_id)
    user_course = UserCourse.model_validate(user_course_in)

    session.add(user_course)
    session.commit()
    session.refresh(user_course)

    return user_course


@router.patch("/me/courses/{course_id}", response_model=UserCourse)
async def update_my_course(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    course_id: uuid.UUID,
    user_course_in: UserCourseUpdate,
) -> UserCourse:
    """
    Update own course.
    """

    user_course = session.get(
        UserCourse, {"user_id": current_user.id, "course_id": course_id}
    )
    if not user_course:
        raise ItemNotFoundError(item_id=course_id, item_name="User course")

    if user_course_in.finished_chapters is not None:
        # Fetch all existing finished chapter records for this user_course
        statement = select(UserCourseFinishedChapter).where(
            UserCourseFinishedChapter.user_course_user_id == current_user.id,
            UserCourseFinishedChapter.user_course_course_id == course_id,
        )
        existing_finished_chapter_records = session.exec(statement).all()

        # Create a set of existing finished chapter IDs in the database
        existing_finished_chapter_ids = {
            record.chapter_id for record in existing_finished_chapter_records
        }

        incoming_finished_chapter_ids = set(user_course_in.finished_chapters)

        # Chapters to add
        chapter_ids_to_add = (
            incoming_finished_chapter_ids - existing_finished_chapter_ids
        )
        for chapter_id_to_add in chapter_ids_to_add:
            new_finished_chapter = UserCourseFinishedChapter(
                user_course_user_id=current_user.id,
                user_course_course_id=course_id,
                chapter_id=chapter_id_to_add,
            )
            session.add(new_finished_chapter)
            print("Staged for adding new finished chapter:", new_finished_chapter)

        # Chapters to remove
        chapter_ids_to_remove = (
            existing_finished_chapter_ids - incoming_finished_chapter_ids
        )
        for record_to_remove in existing_finished_chapter_records:
            if record_to_remove.chapter_id in chapter_ids_to_remove:
                session.delete(record_to_remove)
                print("Staged for removing finished chapter:", record_to_remove)

    update_data = user_course_in.model_dump(
        exclude_unset=True,
        exclude={"finished_chapters"},
    )
    if update_data:
        user_course.sqlmodel_update(update_data)
        session.add(user_course)

    session.commit()
    session.refresh(user_course)

    return user_course


@router.get(
    "/",
    dependencies=[SuperUserRequired],
    response_model=UsersPublic,
)
async def get_users(
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
    dependencies=[SuperUserRequired],
    response_model=UserPublic,
)
async def create_user(*, session: SessionDep, user_in: UserCreate) -> UserPublic:
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

    return UserPublic.model_validate(user)


@router.get("/{user_id}", response_model=UserPublic, dependencies=[SuperUserRequired])
async def get_user_by_id(user_id: uuid.UUID, session: SessionDep) -> UserPublic:
    """
    Get a specific user by id.
    """

    user = session.get(User, user_id)

    if not user:
        raise ItemNotFoundError(item_id=user_id, item_name="User")

    # if user == current_user:
    #     return user

    # if not current_user.is_superuser:
    #     raise PermissionDeniedError(
    #         detail="The user doesn't have enough privileges",
    #     )

    return UserPublic.model_validate(user)


@router.patch(
    "/{user_id}",
    dependencies=[SuperUserRequired],
    response_model=UserPublic,
)
async def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> UserPublic:
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

    return UserPublic.model_validate(db_user)


@router.delete("/{user_id}", dependencies=[SuperUserRequired])
async def delete_user(
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
