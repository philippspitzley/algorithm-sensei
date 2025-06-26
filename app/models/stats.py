from sqlmodel import SQLModel


class Stats(SQLModel):
    total_users: int
    total_courses: int
