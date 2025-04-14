import uuid
from typing import TYPE_CHECKING, Any

from pydantic import HttpUrl
from sqlalchemy.types import String, TypeDecorator
from sqlmodel import Field, Relationship, SQLModel

from .base import TimeStampMixin

if TYPE_CHECKING:
    from .courses import Course


# custom HttpUrl type
class HttpUrlType(TypeDecorator[HttpUrl]):
    impl = String(2083)
    cache_ok = True

    @property
    def python_type(self):
        return HttpUrl

    def process_bind_param(self, value: HttpUrl | None, dialect: Any) -> str | None:
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value: str | None, dialect: Any) -> HttpUrl | None:
        if value is None:
            return None
        return HttpUrl(url=value)

    def process_literal_param(self, value: HttpUrl | None, dialect: Any) -> str:
        return str(value)


# Shared required properties
class ChapterBase(SQLModel):
    chapter_num: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ChapterPointBase(SQLModel):
    chapter_point_num: int = Field(ge=1)
    text: str | None = Field(default=None)
    code_block: str | None = Field(default=None)
    image: HttpUrl | None = Field(default=None, sa_type=HttpUrlType)
    video: HttpUrl | None = Field(default=None, sa_type=HttpUrlType)


# Database model
class Chapter(TimeStampMixin, ChapterBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    course_id: uuid.UUID = Field(foreign_key="course.id", nullable=False)

    # Relationships
    course: "Course" = Relationship(back_populates="chapters")
    points: list["ChapterPoint"] = Relationship(back_populates="chapter")


class ChapterPoint(TimeStampMixin, ChapterPointBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chapter_id: uuid.UUID = Field(foreign_key="chapter.id", nullable=False)

    # Relationships
    chapter: "Chapter" = Relationship(back_populates="points")


# API Input models
class ChapterCreate(ChapterBase):
    pass


class ChapterPointCreate(ChapterPointBase):
    pass


class ChapterUpdate(SQLModel):
    chapter_num: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ChapterPointUpdate(SQLModel):
    chapter_point_num: int | None = Field(default=None, ge=1)
    text: str | None = Field(default=None)
    code_block: str | None = Field(default=None)
    image: HttpUrl | None = Field(default=None, sa_type=HttpUrlType)
    video: HttpUrl | None = Field(default=None, sa_type=HttpUrlType)


class ChapterPointPublic(ChapterPointBase):
    id: uuid.UUID
    chapter_id: uuid.UUID


class ChapterPointsPublic(SQLModel):
    data: list[ChapterPointPublic] = Field(default_factory=list)
    count: int | None = None


class ChapterPublic(ChapterBase):
    id: uuid.UUID
    course_id: uuid.UUID
    points: list[ChapterPointPublic] = Field(default_factory=list)


class ChaptersPublic(SQLModel):
    data: list[ChapterPublic] = Field(default_factory=list)
    count: int | None = None
