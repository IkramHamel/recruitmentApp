# app/modules/base.py
from src.db.session import get_db
from src.core.logging import setup_logging
from .endpoint import EndpointInterface
from fastapi import APIRouter

class BaseFeature(EndpointInterface):
    def __init__(self):
        # Initialize logger and DB session
        self.db_session = get_db
        self.logger = setup_logging()

    def get_router(self) -> APIRouter:
        """This is a placeholder. Each feature should override this."""
        raise NotImplementedError("Subclasses must implement the 'get_router' method.")
