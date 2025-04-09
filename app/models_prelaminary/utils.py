import inspect
from enum import Enum

from sqlmodel import Field, SQLModel

import app.models as models_module


def create_model_class_name_enum() -> type[Enum]:
    """
    Dynamically create an Enum of all SQLModel table classes in the models module.
    """

    model_classes = {}
    for name, cls in inspect.getmembers(models_module, inspect.isclass):
        if (
            issubclass(cls, SQLModel)
            and cls != SQLModel
            and hasattr(cls, "__tablename__")
        ):
            model_classes[name] = name

    return Enum("ModelClassName", model_classes)


ModelClassName = create_model_class_name_enum()


class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
