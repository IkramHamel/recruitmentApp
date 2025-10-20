from abc import ABC, abstractmethod
from phi.model.base import Model

class LLMProvider(ABC):
    @abstractmethod
    def model(self) -> Model:
        """
        Return a PHI model that is compatible with the Groq backend.
        """
        pass
