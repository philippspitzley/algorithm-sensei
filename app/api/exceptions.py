import uuid

from fastapi import FastAPI, HTTPException, Request, status
from slowapi.errors import RateLimitExceeded


# register custom exception handling for other libraries
def add_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers to the FastAPI app
    """

    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        retry_after = getattr(exc, "retry_after", None)
        raise RateLimitError(
            detail=f"Rate limit exceeded. {f'Please try again after {retry_after * 60} minutes.'}"
            if retry_after
            else "Rate limit exceeded. Please try again later.",
            retry_after=retry_after,
        )

    # registering it after function definition because decorator throws Pylance error
    app.exception_handler(RateLimitExceeded)(rate_limit_exceeded_handler)


class CustomError(HTTPException):
    def __init__(self, status_code: int, message: str, error_type: str):
        structured_details = {
            "message": message,
            "status_code": status_code,
            "error_type": error_type,
        }

        super().__init__(status_code=status_code, detail=structured_details)


class DatabaseOperationError(CustomError):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=detail,
            error_type="DatabaseOperationError",
        )


class NotFoundError(CustomError):
    def __init__(self, object_name: str | None = None, detail: str = "Not found"):
        if object_name:
            detail = f"{object_name} not found."
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=detail,
            error_type="NotFoundError",
        )


class ItemNotFoundError(CustomError):
    def __init__(self, item_id: uuid.UUID, item_name: str, detail: str = "Not found"):
        if item_name and item_id:
            detail = f"{item_name.capitalize()} with id {item_id} not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=detail,
            error_type="ItemNotFoundError",
        )


class PermissionDeniedError(CustomError):
    def __init__(
        self,
        detail: str = "Not enough permissions for this resource",
        error_type: str = "PermissionDeniedError",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=f"Access denied: {detail}",
            error_type=error_type,
        )


class InvalidCredentialsError(CustomError):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=detail,
            error_type="InvalidCredentialsError",
        )


class ItemAlreadyExistsError(CustomError):
    def __init__(self, item_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"'{item_name.capitalize()}' already exists in the system",
            error_type="ItemAlreadyExistsError",
        )


class ValidationError(CustomError):
    def __init__(
        self, detail: str = "Validation error", error_type: str = "ValidationError"
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=detail,
            error_type=error_type,
        )


class PasswordValidationError(ValidationError):
    def __init__(self, detail: str = "Password validation failed"):
        super().__init__(detail=detail, error_type="PasswordValidationError")


class EmailValidationError(ValidationError):
    def __init__(self, detail: str = "Email validation failed"):
        super().__init__(detail=detail, error_type="EmailValidationError")


class TokenValidationError(PermissionDeniedError):
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(detail=detail, error_type="TokenValidationError")


class InactiveUserError(ValidationError):
    def __init__(self, detail: str = "User account is inactive"):
        super().__init__(detail=detail, error_type="InactiveUserError")


class ResourceConflictError(CustomError):
    def __init__(self, resource_type: str, detail: str | None = None):
        message = f"Conflict with existing {resource_type}"
        if detail:
            message = f"{message}: {detail}"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            error_type="ResourceConflictError",
        )


class RateLimitError(CustomError):
    def __init__(
        self, detail: str = "Too many requests", retry_after: int | None = None
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=detail,
            error_type="RateLimitError",
        )

        # Add headers after initialization
        if retry_after is not None:
            self.headers = {"Retry-After": str(retry_after)}
