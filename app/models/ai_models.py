from enum import Enum

from pydantic import BaseModel


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class HintRequest(BaseModel):
    user_code: str
    exercise_description: str
    test_cases: str
    error: str | None = None
    difficulty_level: Difficulty = Difficulty.BEGINNER
    previous_hints: list["HintResponse"] = []


class HintResponse(BaseModel):
    hint: str
    explanation: str
    code_snippet: str | None = None
    next_steps: list[str]
    confidence_score: float
    detected_issue_type: str | None = None
