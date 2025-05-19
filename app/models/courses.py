# pyright: reportIncompatibleVariableOverride=false
import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models import TimeStampMixin

from .chapters import (
    ChapterPublic,  # must be imported above TYPE_CHECKING because Chapter and ChapterPublic are circular references from ChapterBase
)

if TYPE_CHECKING:
    from .chapters import Chapter
    from .user_courses import UserCourse


# Shared properties
class CourseBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None)


# Database model
class Course(TimeStampMixin, CourseBase, table=True):
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
    chapters: list["ChapterPublic"] | None = None  # Field(default_factory=list)


class CoursesPublic(SQLModel):
    data: list["CoursePublic"] = Field(default_factory=list)
    count: int | None = Field(default=None, ge=0)
