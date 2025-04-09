# pyright: reportIncompatibleVariableOverride=false
import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models import TimeStampMixin

if TYPE_CHECKING:
    from .chapters import Chapter, ChapterPublic
    from .user_courses import UserCourse


# Shared properties
class CourseBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model
class Course(TimeStampMixin, CourseBase, table="courses"):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationships
    chapters: list["Chapter"] = Relationship(back_populates="course")
    user_courses: list["UserCourse"] = Relationship(back_populates="course")


# INPUT: Properties to receive via API
# on creation
class CourseCreate(CourseBase):
    pass


# on update
class CourseUpdate(CourseBase):
    title: str | None = None


# OUTPUT: Properties to return via API
class CoursePublic(CourseBase):
    id: uuid.UUID
    chapters: list["ChapterPublic"] | None


class CoursesPublic(SQLModel):
    data: list[CoursePublic]
    count: int
