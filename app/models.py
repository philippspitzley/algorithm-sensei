import uuid
from datetime import UTC, datetime
from enum import Enum

from pydantic import EmailStr, HttpUrl
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel


class TimeStampMixin(SQLModel):
    """Mixin class for timestamp fields."""

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Database timestamp when the record was created.",
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(UTC),
        },
    )


################################
### User ###
################################


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    user_name: str | None = Field(unique=True, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    user_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    user_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(TimeStampMixin, UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

    # Relationships
    # courses: list["UserCourse"] = Relationship(back_populates="user")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


################################
### Course ###
################################


# Shared properties
class CourseBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class CourseCreate(CourseBase):
    pass


# Properties to receive on item update
class CourseUpdate(CourseBase):
    title: str | None = None


# Database model, database table inferred from class name
class Course(TimeStampMixin, CourseBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    chapters: list["Chapter"] = Relationship(back_populates="course")
    user_courses: list["UserCourse"] = Relationship(back_populates="course")


# Properties to return via API, id is always required
class CoursePublic(CourseBase):
    id: uuid.UUID
    chapters: list["ChapterPublic"] | None


class CoursesPublic(SQLModel):
    data: list[CoursePublic]
    count: int


################################
#### UserCourse ####
################################


class CourseStatus(str, Enum):
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserCourseBase(SQLModel):
    status: CourseStatus = Field(default=CourseStatus.ENROLLED)
    current_chapter: int = Field(default=1, ge=1)
    finished_chapters: list[int] = Field(default=None, unique_items=True)
    progress: int = Field(default=0, ge=0, le=100)


class UserCourse(TimeStampMixin, UserCourseBase, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, primary_key=True)
    course_id: uuid.UUID = Field(
        foreign_key="course.id", nullable=False, primary_key=True
    )
    finished_chapters: list[int] = Field(default_factory=list, sa_column=Column(JSON))

    # Relationships
    user: User = Relationship(back_populates="courses")
    course: Course = Relationship(back_populates="user_courses")

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="unique_user_course"),
    )


class UserCoursePublic(UserCourseBase):
    user_id: uuid.UUID
    course_id: uuid.UUID


class UserCourseUpdate(UserCourseBase):
    status: CourseStatus | None = None
    current_chapter: int | None = None
    finished_chapters: list[int] | None = None
    progress: int | None = None


class UserCourseCreate(UserCourseUpdate):
    user_id: uuid.UUID
    course_id: uuid.UUID


####################################
### Chapter ###
####################################


class ChapterBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class Chapter(TimeStampMixin, ChapterBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    course_id: uuid.UUID = Field(foreign_key="course.id", nullable=False)

    # Relationships
    course: Course = Relationship(back_populates="chapters")
    points: list["ChapterPoint"] = Relationship(back_populates="chapter")


class ChapterCreate(ChapterBase):
    course_id: uuid.UUID


class ChapterUpdate(ChapterBase):
    title: str | None = None


class ChapterPublic(ChapterBase):
    id: uuid.UUID
    course_id: uuid.UUID
    points: list["ChapterPointPublic"] | None = Field(default=[])


####################################
### ChapterPoint ###
####################################


class ChapterPointBase(SQLModel):
    chapter_num: int = Field(default=1, ge=1)
    text: str | None = Field(default=None)
    code_block: str | None = Field(default=None)
    image: HttpUrl | None = Field(default=None)
    video: HttpUrl | None = Field(default=None)


class ChapterPoint(TimeStampMixin, ChapterPointBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chapter_id: uuid.UUID = Field(foreign_key="chapter.id", nullable=False)

    # HttpUrl from pydantic is not compatible with SQLAlchemy so we use str in the database and validate it in the model
    image: str | None = Field(default=None, max_length=255)
    video: str | None = Field(default=None, max_length=255)

    # Relationships
    chapter: Chapter = Relationship(back_populates="points")


class ChapterPointCreate(ChapterPointBase):
    pass


class ChapterPointUpdate(ChapterPointBase):
    chapter_num: int | None = None


class ChapterPointPublic(ChapterPointBase):
    id: uuid.UUID
    chapter_id: uuid.UUID


####################################
### Utility ###
######################################


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
