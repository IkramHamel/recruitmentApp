from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.settings.app_settings import get_app_settings, update_app_settings, get_list_timezones, get_supported_languages
from src.core.logging import logger
from src.internal.settings.app_settings.schemas import AppSettingsResponse, AppSettingsUpdate, AvailableTimezones
from src.api.endpoint import BaseEndpoint
from ..middlewares.authz import has_permission
from ...internal.iam.users.models import User
'''
dependencies=[Depends(requiresAuth)]
'''
class GeneralSettingsEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger  # Use your own logger setup or standard logging

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/app")

        @router.get("/", response_model=AppSettingsResponse)
        def get_appSettings(db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission('view_app'))):
            """Fetch general app settings"""
            self.logger.info("Attempting to fetch general app settings")
            db_settings = get_app_settings(db)
            if not db_settings:
                self.logger.error("App settings not found.")
                raise HTTPException(status_code=404, detail="App settings not found")
            self.logger.info(f"App settings found with ID: {db_settings.id}")
            return db_settings
        
        @router.get("/languages",)
        def get_languages_supported(db: Session = Depends(self.db_session)):
            """Fetch general app settings"""
            self.logger.info("Attempting to fetch supported languages")
            db_supported_languages = get_supported_languages(db)
            return db_supported_languages

        @router.put("/", response_model=AppSettingsResponse)
        def update_appSettings(app_settings_update: AppSettingsUpdate, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission('update_app'))):
            """Update the general app settings"""
            self.logger.info("Attempting to update general app settings")
            updated_settings = update_app_settings(db, app_settings_update)
            if not updated_settings:
                self.logger.error("Failed to update app settings.")
                raise HTTPException(status_code=400, detail="Failed to update app settings")
            self.logger.info(f"App settings updated with ID: {updated_settings.id}")
            return updated_settings

        @router.get("/timezones", response_model=AvailableTimezones)
        def get_available_timezones(db: Session = Depends(self.db_session)):
            """Update the general app settings"""
            self.logger.info("Attempting to get available timezones")
            timezones = get_list_timezones()
            self.logger.info(f"{len(timezones)} available timezones")
            return {"timezones": timezones}

        return router
