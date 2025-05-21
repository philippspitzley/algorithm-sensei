# pyright: reportIncompatibleVariableOverride=false
import uuid
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import computed_field
from sqlalchemy import ForeignKeyConstraint
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
    current_chapter: int = Field(default=1)
    progress: int = Field(default=0)

    # created_at: datetime | None = Field(default_factory=datetime.utcnow)
    # updated_at: datetime = Field(
    #     default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}
    # )


# Database model
class UserCourse(TimeStampMixin, UserCourseBase, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, primary_key=True)
    course_id: uuid.UUID = Field(
        foreign_key="course.id", nullable=False, primary_key=True
    )

    # Relationships
    user: "User" = Relationship(back_populates="courses")
    course: "Course" = Relationship(back_populates="user_courses")
    finished_chapters: list["UserCourseFinishedChapter"] = Relationship(
        back_populates="user_course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class UserCourseFinishedChapter(TimeStampMixin, SQLModel, table=True):
    # __tablename__ = "usercoursefinishedchapter"

    user_course_user_id: uuid.UUID = Field(primary_key=True)
    user_course_course_id: uuid.UUID = Field(primary_key=True)
    chapter_id: uuid.UUID = Field(primary_key=True)

    # Relationships
    user_course: UserCourse = Relationship(
        back_populates="finished_chapters",
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_course_user_id", "user_course_course_id"],
            ["usercourse.user_id", "usercourse.course_id"],
            name="fk_usercoursefinishedchapter_usercourse",  # Optional: Naming the constraint
        ),
        ForeignKeyConstraint(
            ["chapter_id"],
            ["chapter.id"],
            name="fk_usercoursefinishedchapter_chapter_id_chapter",
            ondelete="CASCADE",
        ),
    )


# INPUT: Properties to receive via API
# on update
class UserCourseUpdate(UserCourseBase):
    status: CourseStatus | None = None
    current_chapter: int | None = None
    progress: int | None = None
    finished_chapters: list[uuid.UUID] | None = None


# on creation
class UserCourseCreate(UserCourseBase):
    user_id: uuid.UUID
    course_id: uuid.UUID


# OUTPUT: Properties to return via API
class UserCoursePublic(UserCourseBase):
    user_id: uuid.UUID
    course_id: uuid.UUID
    finished_chapters: list[UserCourseFinishedChapter] = Field(default=[], exclude=True)

    @computed_field(alias="finished_chapters")
    @property
    def finished_chapter_ids_list(self) -> list[uuid.UUID]:
        if self.finished_chapters:
            return [fc.chapter_id for fc in self.finished_chapters]
        return []
