from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

from app.core.config import settings

# Initialize Gemini model
gemini_model = GeminiModel(
    "gemini-2.0-flash", provider=GoogleGLAProvider(api_key=settings.GEMINI_API_KEY)
)


class AIConfig:
    """Configuration class for AI services"""

    @staticmethod
    def get_gemini_model():
        return gemini_model
