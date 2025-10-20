# src/internal/settings/settings_endpoints.py

from fastapi import APIRouter
from .app import GeneralSettingsEndpoint
from .reasoners import ReasonersEndpoint
from sqlalchemy.orm import Session
from src.core.logging import logger
from typing import List
from src.api.endpoint import BaseEndpoint


class SettingsEndpoints:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_routers(self) -> List[APIRouter]:
        routes = list()

        # List of endpoint classes
        endpoints: list[BaseEndpoint] = [
            GeneralSettingsEndpoint(db_session=self.db_session),
            ReasonersEndpoint(db_session=self.db_session),
            
        ]

        # Iterate through the list and append the router for each endpoint
        for endpoint in endpoints:
            routes.append(endpoint.get_router())

        return routes
