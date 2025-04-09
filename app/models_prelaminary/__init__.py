# Import and re-export all models to avoid circular imports
__all__ = [
    # Base
    "TimeStampMixin",
    # Chapter models
    "Chapter",
    "ChapterBase",
    "ChapterCreate",
    "ChapterPoint",
    "ChapterPointBase",
    "ChapterPointCreate",
    "ChapterPointPublic",
    "ChapterPointUpdate",
    "ChapterPublic",
    "ChapterUpdate",
    # Course models
    "Course",
    "CourseBase",
    "CourseCreate",
    "CoursePublic",
    "CoursesPublic",
    "CourseUpdate",
    # UserCourse models
    "CourseStatus",
    "UserCourse",
    "UserCourseBase",
    "UserCourseCreate",
    "UserCoursePublic",
    "UserCourseUpdate",
    # User models
    "UpdatePassword",
    "User",
    "UserBase",
    "UserCreate",
    "UserPublic",
    "UserRegister",
    "UsersPublic",
    "UserUpdate",
    "UserUpdateMe",
    # Utility models
    "Message",
    "NewPassword",
    "Token",
    "TokenPayload",
]
# Base
from .base import TimeStampMixin

# Chapter models
from .chapters import (
    Chapter,
    ChapterBase,
    ChapterCreate,
    ChapterPoint,
    ChapterPointBase,
    ChapterPointCreate,
    ChapterPointPublic,
    ChapterPointUpdate,
    ChapterPublic,
    ChapterUpdate,
)

# Course models
from .courses import (
    Course,
    CourseBase,
    CourseCreate,
    CoursePublic,
    CoursesPublic,
    CourseUpdate,
)

# UserCourse models
from .user_courses import (
    CourseStatus,
    UserCourse,
    UserCourseBase,
    UserCourseCreate,
    UserCoursePublic,
    UserCourseUpdate,
)

# User models
from .users import (
    UpdatePassword,
    User,
    UserBase,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

# Utility models
from .utils import Message, NewPassword, Token, TokenPayload

# Update forward references
User.model_rebuild()
Course.model_rebuild()
Chapter.model_rebuild()
ChapterPoint.model_rebuild()
UserCourse.model_rebuild()
