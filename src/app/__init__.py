
# app/core/application.py
from src.api import APIServer
from src.core.logging import logger
from src.db.session import Base, engine, SessionLocal
from src.internal.settings.app_settings import check_or_create_app_settings, create_app_languages

from src.internal.settings.app_settings.schemas import AppSettingsCreate

class Application:
    def __init__(self,host="0.0.0.0", port=8098):
        self.logger = logger
        # Migrate data
        # Create all tables defined by Base (including the User table)
        Base.metadata.create_all(bind=engine)
        self.api_server = APIServer(host=host, port=port,logger=self.logger)


    def run(self): 
        self._init_app()
        # Method to run the application when called programmatically
        self.api_server.run()


    def _init_app(self):
        # 1. Init roles
        # migrate permissions of each module
        
        # 1. Init app languages
        create_app_languages(SessionLocal())
        # 2. settings app 
        check_or_create_app_settings(SessionLocal(),app_settings_create=AppSettingsCreate(organization_name="",setup_status=1, default_language="English"))


        