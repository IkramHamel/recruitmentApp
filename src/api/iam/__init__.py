
from fastapi import APIRouter
from sqlalchemy.orm import Session
from src.core.logging import logger
from typing import List
from src.api.endpoint import BaseEndpoint
from src.api.iam.users import UsersEndpoint
from src.api.iam.roles import RolesEndpoint
from src.api.iam.permissions import PermissionsEndpoint


class IAMEndpoints:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_routers(self) -> List[APIRouter]:
        routes = list()

        # List of endpoint classes
        endpoints: list[BaseEndpoint] = [
        UsersEndpoint(db_session=self.db_session),
        RolesEndpoint(db_session=self.db_session),
        PermissionsEndpoint(db_session=self.db_session),

        ]
        

        # Iterate through the list and append the router for each endpoint
        for endpoint in endpoints:
            routes.append(endpoint.get_router())

        return routes
