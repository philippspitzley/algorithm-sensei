from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


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
