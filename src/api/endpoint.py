from abc import ABC, abstractmethod
from fastapi import APIRouter

class BaseEndpoint(ABC):
    @abstractmethod
    def get_router(self) -> APIRouter:
        """
        Return a list of FastAPI router.
        """
        pass
