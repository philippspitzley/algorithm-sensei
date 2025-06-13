import re

import httpx
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.models.piston_api import CodeError, CodeRequest, CodeResponse

router = APIRouter(prefix="/piston", tags=["piston_api"])


@router.post("/execute", response_model=CodeResponse)
async def execute_code(request: CodeRequest) -> CodeResponse:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.PISTON_API_URL,
                json={
                    "language": request.language,
                    "version": request.version,
                    "files": [
                        {"name": request.files.name, "content": request.files.content}
                    ],
                },
            )
            response.raise_for_status()
            data: CodeResponse = response.json()

            if data.run and data.run.stderr:
                error = parse_error(data["run"]["stderr"])
                print("Compile Error Found:", error)

                return CodeResponse(run=data["run"], error=error)

            print("No errors in run output.")

        except httpx.HTTPStatusError as error:
            print("Error Response:", error.response.json())
            raise HTTPException(
                status_code=error.response.status_code,
                detail=error.response.json(),
            )
            return CodeResponse(
                compile=None, run=None, error=CodeError(message=str(error))
            )

        return CodeResponse(compile=data.get("compile"), run=data["run"], error=None)


def parse_error(stderr: str) -> CodeError:
    """Parse the stderr output to extract error details."""

    # Extract line and column
    location_match = re.search(r"main\.js:(\d+):(\d+)", stderr)
    line, column = location_match.groups() if location_match else (None, None)

    # Extract pointer (line with the caret)
    pointer_match = re.search(r"(?m)^(\s*\^)\s*$", stderr)
    pointer_line = pointer_match.group(1) if pointer_match else None

    # Extract the error type and message
    error_match = re.search(
        r"^(?P<type>\w+Error): (?P<message>.+)$", stderr, re.MULTILINE
    )
    error_type = error_match.group("type") if error_match else None
    error_message = error_match.group("message") if error_match else None

    return CodeError(
        type=error_type,
        message=error_message,
        pointer=pointer_line,
        line=line,
        column=column,
    )
