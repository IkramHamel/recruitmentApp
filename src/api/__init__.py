# api_server.py

from fastapi import FastAPI
from .settings import SettingsEndpoints
from .auth import AuthEndpoints
from .iam import IAMEndpoints
from .anticheatRules import AntiCheatRulesEndpoint
from .exam import ExamEndpoints
from src.db.session import get_db  # Assuming you have a SQLAlchemy session
from fastapi.middleware.cors import CORSMiddleware
from src.internal.exam.assessment.models import Assessment
from src.internal.exam.questions.models import Question
from src.internal.exam.responses.models import Response
from src.internal.exam.test.models import Test
from src.internal.job_positions.models import *
from src.internal.settings.reasoners.models import Reasoners
from .websocket import WebSocketEndpoints
from src.internal.exam.results.models import Result
from .notification import NotificationEndpoints
from .jobpositions import JobEndpoints
from src.db.session import (
    SessionLocal
) 
from fastapi.staticfiles import StaticFiles


class APIServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8096, logger = None):
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.logger = logger  
        self._initialize_routes()

    def _initialize_routes(self):
        # Allow all origins for simplicity, you can specify specific origins as needed
        origins = [
            "*",  # Allows all origins
        ]

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,  # List of allowed origins
            allow_credentials=True,
            allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
            allow_headers=["*"],  # Allows all headers
        )
        self.app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
        
        auth_endpoints = AuthEndpoints(db_session=get_db).get_routers()
        self._appendRouters(auth_endpoints,"/api/auth",["Auth"])

        settings_endpoints = SettingsEndpoints(db_session=get_db).get_routers()
        self._appendRouters(settings_endpoints,"/api/settings",["Settings"])

        iam_endpoints = IAMEndpoints(db_session=get_db).get_routers()
        self._appendRouters(iam_endpoints,"/api/iam",["Iam"])

        rules_endpoints = AntiCheatRulesEndpoint(db_session=get_db).get_routers()
        self._appendRouters(rules_endpoints,"/api/rules",["Rules"])

        exams_endpoints = ExamEndpoints(db_session=get_db).get_routers()
        self._appendRouters(exams_endpoints,"/api/exams",["Exams"])

        #candidate_endpoints = CandidateEndpoints(db_session=get_db).get_routers()
        #self._appendRouters(candidate_endpoints,"/api/candidates",["Candidates"])

        notifs_endpoints = NotificationEndpoints(db_session=get_db).get_routers()
        self._appendRouters(notifs_endpoints,"/api/notification",["Notification Templates"])

        jobpositions_endpoints = JobEndpoints(db_session=get_db).get_routers() 
        self._appendRouters(jobpositions_endpoints,"/api/jobs",["Jobs Positions"])

        socket_endpoints = WebSocketEndpoints(db_session=get_db).get_routers()
        self._appendRouters(socket_endpoints,"/api/socket",["Websockets"])
        
        

    def _appendRouters(self,endpoints,prefix,tags):
        for endpoint in endpoints:
            self.app.include_router(endpoint, prefix=prefix, tags=tags)       

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)
        self.logger.info(f"Starting API server on {self.host}:{self.port}...")
