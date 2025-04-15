# pyright: reportIncompatibleVariableOverride=false
import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel

from .base import TimeStampMixin

if TYPE_CHECKING:
    from .courses import Course
    from .users import User


class CourseStatus(str, Enum):
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# Shared properties
class UserCourseBase(SQLModel):
    status: CourseStatus = Field(default=CourseStatus.ENROLLED)
    current_chapter: int = Field(default=1, ge=1)
    finished_chapters: list[int] = Field(default_factory=list)
    progress: int = Field(default=0, ge=0, le=100)


# Database model
class UserCourse(TimeStampMixin, UserCourseBase, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, primary_key=True)
    course_id: uuid.UUID = Field(
        foreign_key="course.id", nullable=False, primary_key=True
    )
    finished_chapters: list[int] = Field(default_factory=list, sa_column=Column(JSON))

    # Relationships
    user: "User" = Relationship(back_populates="courses")
    course: "Course" = Relationship(back_populates="user_courses")

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="unique_user_course"),
    )


# INPUT: Properties to receive via API
# on update
class UserCourseUpdate(UserCourseBase):
    status: CourseStatus | None = None
    current_chapter: int | None = None
    finished_chapters: list[int] | None = None
    progress: int | None = None


# on creation
class UserCourseCreate(UserCourseBase):
    user_id: uuid.UUID
    course_id: uuid.UUID


# OUTPUT: Properties to return via API
class UserCoursePublic(UserCourseBase):
    user_id: uuid.UUID
    course_id: uuid.UUID
