import re

import httpx
from fastapi import APIRouter

from app.api.exceptions import InternalServerError, PistonAPIError
from app.core.config import settings
from app.models.piston_api import CodeError, CodeRequest, CodeResponse

router = APIRouter(prefix="/piston", tags=["piston_api"])
client = httpx.AsyncClient(timeout=settings.PISTON_TIMEOUT)


@router.post("/execute", response_model=CodeResponse)
async def execute_code(request: CodeRequest) -> CodeResponse:
    payload = request.model_dump(exclude_none=True)
    try:
        res = await client.post(
            settings.PISTON_API_URL,
            json=payload,
        )
        res.raise_for_status()
        result = res.json()

    except httpx.HTTPStatusError as error:
        raise PistonAPIError(response=error.response)

    except httpx.RequestError as error:
        msg = f"Could not connect to Piston API: {str(error)}"
        raise InternalServerError(detail=msg)

    data = CodeResponse.model_validate(result)

    compile_res = getattr(data, "compile", None)
    run_res = getattr(data, "run", None)
    error = None

    if run_res and run_res.stderr:
        error = parse_error(run_res.stderr)

        return CodeResponse(compile=compile_res, run=run_res, error=error)

    return CodeResponse(compile=data.compile, run=data.run, error=error)


def parse_error(stderr: str) -> CodeError:
    """Parse the stderr output to extract error details."""

    # Extract line and column
    location_match = re.search(r"\(/box/submission/(main.py:(\d?):(\d?))\)", stderr)

    location, line, column = (
        location_match.groups() if location_match else (None, None, None)
    )

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
        location=location,
        line=line,
        column=column,
    )
