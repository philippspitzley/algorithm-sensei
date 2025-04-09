import uuid

from fastapi import HTTPException, status


class DatabaseOperationError(HTTPException):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🚨 {detail}",
        )


class NotFoundError(HTTPException):
    def __init__(self, object_name: str | None, detail: str = "❓ Not found"):
        if object_name:
            detail = f"❓ {object_name} not found."
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ItemNotFoundError(NotFoundError):
    def __init__(self, item_id: uuid.UUID, item_name: str):
        super().__init__(
            object_name=item_name,
            detail=f"'{item_name.capitalize()}' with id '{item_id}' not found",
        )


class PermissionDeniedError(HTTPException):
    def __init__(self, detail: str = "Not enough permissions for this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"⛔ Access denied: {detail}",
        )


class InvalidCredentialsError(HTTPException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"🚫 {detail}",
        )


class ItemAlreadyExistsError(HTTPException):
    def __init__(self, item_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"⚠️ '{item_name.capitalize()}' already exists in the system",
        )


class ValidationError(HTTPException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"❗ {detail}",
        )


class PasswordValidationError(ValidationError):
    def __init__(self, detail: str = "Password validation failed"):
        super().__init__(detail=f"🔑 {detail}")


class EmailValidationError(ValidationError):
    def __init__(self, detail: str = " Email validation failed"):
        super().__init__(detail=f"📧 {detail}")


class ResourceConflictError(HTTPException):
    def __init__(self, resource_type: str, detail: str | None = None):
        message = f"⚔️ Conflict with existing {resource_type}"
        if detail:
            message = f"{message}: {detail}"
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)
