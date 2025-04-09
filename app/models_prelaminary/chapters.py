import uuid
from typing import TYPE_CHECKING

from pydantic import HttpUrl
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel, String

from .base import TimeStampMixin

if TYPE_CHECKING:
    from .courses import Course


# Shared properties
class ChapterBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model
class Chapter(TimeStampMixin, ChapterBase, table="chapters"):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    course_id: uuid.UUID = Field(foreign_key="course.id", nullable=False)

    # Relationships
    course: "Course" = Relationship(back_populates="chapters")
    points: list["ChapterPoint"] = Relationship(back_populates="chapter")


# INPUT: Properties to receive via API
# on creation
class ChapterCreate(ChapterBase):
    course_id: uuid.UUID


# on update
class ChapterUpdate(SQLModel):
    title: str | None = None
    description: str | None = None


# OUTPUT: Properties to return via API
class ChapterPublic(ChapterBase):
    id: uuid.UUID
    course_id: uuid.UUID
    points: list["ChapterPointPublic"] | None = Field(default=[])


################################################
### ChapterPoint ###
################################################


# Shared properties
class ChapterPointBase(SQLModel):
    chapter_num: int | None = Field(default=1, ge=1)
    text: str | None = Field(default=None)
    code_block: str | None = Field(default=None)
    image: HttpUrl | None = Field(default=None, sa_column=Column(String(255)))
    video: HttpUrl | None = Field(default=None, sa_column=Column(String(255)))


# Database model
class ChapterPoint(TimeStampMixin, ChapterPointBase, table="chapter_points"):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chapter_id: uuid.UUID = Field(foreign_key="chapter.id", nullable=False)

    # Relationships
    chapter: Chapter = Relationship(back_populates="points")


# INPUT: Properties to receive via API
# on creation
class ChapterPointCreate(ChapterPointBase):
    pass


# on update
class ChapterPointUpdate(ChapterPointBase):
    pass


# OUTPUT: Properties to return via API
class ChapterPointPublic(ChapterPointBase):
    id: uuid.UUID
    chapter_id: uuid.UUID
