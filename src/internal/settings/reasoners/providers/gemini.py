from phi.model.google import Gemini
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    def model(self) -> Gemini:
        # Implement the logic to return a compatible Groq model for ProviderA
        return Gemini

