# src/internal/settings/settings_endpoints.py

from fastapi import APIRouter
from .mailing import MailingEndpoint
from .templates import NotificationTemplateEndpoint
from sqlalchemy.orm import Session
from src.core.logging import logger
from typing import List
from src.api.endpoint import BaseEndpoint


class NotificationEndpoints:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_routers(self) -> List[APIRouter]:
        routes = list()

        # List of endpoint classes
        endpoints: list[BaseEndpoint] = [
            MailingEndpoint(db_session=self.db_session),
            NotificationTemplateEndpoint(db_session=self.db_session),
        ]

        # Iterate through the list and append the router for each endpoint
        for endpoint in endpoints:
            routes.append(endpoint.get_router())

        self.logger.info("Settings endpoints loaded successfully.")
        return routes
