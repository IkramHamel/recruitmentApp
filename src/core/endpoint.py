# app/modules/endpoint_interface.py
from abc import ABC, abstractmethod
from fastapi import APIRouter

class EndpointInterface(ABC):
    @abstractmethod
    def get_router(self) -> APIRouter:
        """Returns the API router for the feature."""
        pass
