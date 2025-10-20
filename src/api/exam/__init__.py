
from fastapi import APIRouter
from sqlalchemy.orm import Session
from src.core.logging import logger
from typing import List
from src.api.endpoint import BaseEndpoint
from src.api.exam.assessment import AssessmentsEndpoint
from src.api.exam.test import TestsEndpoint
from src.api.exam.question import QuestionsEndpoint
from src.api.exam.response import ResponsesEndpoint
from src.api.exam.result import ResultsEndpoint


class ExamEndpoints:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_routers(self) -> List[APIRouter]:
        routes = list()

        # List of endpoint classes
        endpoints: list[BaseEndpoint] = [
        AssessmentsEndpoint(db_session=self.db_session),
        TestsEndpoint(db_session=self.db_session),
        QuestionsEndpoint(db_session=self.db_session),
        ResponsesEndpoint(db_session=self.db_session),
        ResultsEndpoint(db_session=self.db_session),

        

        ]
        

        # Iterate through the list and append the router for each endpoint
        for endpoint in endpoints:
            routes.append(endpoint.get_router())

        return routes
