from sqlmodel import Field, SQLModel


class Message(SQLModel):
    """Generic message response model."""

    message: str


class Token(SQLModel):
    """JWT token response model."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """JWT token payload model."""

    sub: str | None = None


class NewPassword(SQLModel):
    """Model for password reset requests."""

    token: str
    new_password: str = Field(min_length=8, max_length=40)
