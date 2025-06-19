import uuid
from typing import TYPE_CHECKING, Any

from pydantic import HttpUrl, model_validator
from sqlalchemy import Connection, event, update
from sqlalchemy.orm import Mapper
from sqlalchemy.types import String, TypeDecorator
from sqlmodel import Field, Relationship, SQLModel, Text

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
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None)
    exercise: str | None = Field(default=None, sa_type=Text)
    test_code: str | None = Field(default=None, sa_type=Text)


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
    chapter_num: int = Field(ge=1)

    # Relationships
    course: "Course" = Relationship(back_populates="chapters")
    points: list["ChapterPoint"] = Relationship(back_populates="chapter")


# Event listener for automatic renumbering after deletion
@event.listens_for(Chapter, "after_delete")
def renumber_chapters_after_delete(
    mapper: Mapper[Chapter], connection: Connection, target: Chapter
):
    """Automatically renumber chapters after one is deleted"""
    connection.execute(
        update(Chapter.__table__)  # type: ignore[attr-defined]
        .where(
            Chapter.__table__.c.course_id == target.course_id,  # type: ignore[attr-defined]
            Chapter.__table__.c.chapter_num > target.chapter_num,  # type: ignore[attr-defined]
        )
        .values(chapter_num=Chapter.__table__.c.chapter_num - 1)  # type: ignore[attr-defined]
    )


class ChapterPoint(TimeStampMixin, ChapterPointBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chapter_id: uuid.UUID = Field(foreign_key="chapter.id", nullable=False)

    # Relationships
    chapter: "Chapter" = Relationship(back_populates="points")


# API Input models
class ChapterCreate(ChapterBase):
    pass


class ChapterPointCreate(ChapterPointBase):
    @model_validator(mode="after")
    def check_exclusive_content_fields(self) -> "ChapterPointCreate":
        content_fields = [
            self.text,
            self.code_block,
            self.image,
            self.video,
        ]
        provided_fields_count = sum(1 for field in content_fields if field is not None)

        if provided_fields_count == 0:
            raise ValueError(
                "One of 'text', 'code_block', 'image', or 'video' must be provided."
            )
        if provided_fields_count > 1:
            raise ValueError(
                "Only one of 'text', 'code_block', 'image', or 'video' can be provided."
            )
        return self


class ChapterUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None)
    exercise: str | None = Field(default=None)
    test_code: str | None = Field(default=None)


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
    chapter_num: int
    points: list[ChapterPointPublic] | None = None  # Field(default_factory=list)


class ChaptersPublic(SQLModel):
    data: list[ChapterPublic] = Field(default_factory=list)
    count: int | None = None
