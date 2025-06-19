import logfire
from fastapi import APIRouter, HTTPException, Request

from app.api.limiter import limiter
from app.models.ai_models import HintRequest, HintResponse
from app.services.ai_agent import generate_hint

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate", response_model=HintResponse)
@limiter.limit("50/day")  # type: ignore
async def get_hint(hint_request: HintRequest, request: Request) -> HintResponse:
    """Generate a contextual hint for a coding exercise."""
    with logfire.span("hint_endpoint"):
        try:
            logfire.info(
                "Hint request received",
                request=hint_request.model_dump(exclude_none=True),
            )

            hint_response = await generate_hint(hint_request)

            logfire.info(
                "Hint response generated", confidence=hint_response.confidence_score
            )

            return hint_response

        except Exception as e:
            logfire.error("Error in hint endpoint", error=str(e))
            raise HTTPException(
                status_code=500, detail="Failed to generate hint. Please try again."
            )


@router.get("/health")
async def health_check():
    """Simple health check for the hints service."""
    return {"status": "healthy", "service": "hints"}
