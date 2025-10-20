from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.notification.templates import create_notification_template, get_notification_templates, get_notification_template_by_id, update_notification_template, delete_notification_template
from src.core.logging import logger
from src.internal.notification.templates import NotificationTemplateResponse, NotificationTemplateCreate, NotificationTemplateUpdate
from typing import List
from src.api.endpoint import BaseEndpoint

class NotificationTemplateEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger # Use your own logger setup or standard logging

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/templates")

        @router.post("/", response_model=NotificationTemplateResponse)
        def create_notification_template_endpoint(template: NotificationTemplateCreate, db: Session = Depends(self.db_session)):
            """Create a new Notification Template"""
            self.logger.info(f"Attempting to create Notification Template with title: {template.title}")
            try:
                created_template = create_notification_template(db, template)
                self.logger.info(f"Notification Template created with ID: {created_template.id}")
                return created_template
            except ValueError as e:
                self.logger.error(f"Error creating Notification Template: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))

        @router.get("/", response_model=List[NotificationTemplateResponse])
        def get_all_notification_templates_endpoint(db: Session = Depends(self.db_session)):
            """Get all Notification Templates"""
            self.logger.info("Attempting to fetch all Notification Templates")
            db_templates = get_notification_templates(db)
            if not db_templates:
                self.logger.error("No Notification Templates found.")
                raise HTTPException(status_code=404, detail="No Notification Templates found")
            self.logger.info(f"Fetched {len(db_templates)} Notification Templates")
            return db_templates

        @router.get("/{template_id}", response_model=NotificationTemplateResponse)
        def get_notification_template_by_id_endpoint(template_id: int, db: Session = Depends(self.db_session)):
            """Get a Notification Template by ID"""
            self.logger.info(f"Attempting to fetch Notification Template with ID: {template_id}")
            db_template = get_notification_template_by_id(db, template_id)
            if not db_template:
                self.logger.error(f"Notification Template with ID {template_id} not found.")
                raise HTTPException(status_code=404, detail="Notification Template not found")
            self.logger.info(f"Notification Template found with ID: {db_template.id}")
            return db_template

        @router.put("/{template_id}", response_model=NotificationTemplateResponse)
        def update_notification_template_endpoint(template_id: int, template_update: NotificationTemplateUpdate, db: Session = Depends(self.db_session)):
            """Update a Notification Template"""
            self.logger.info(f"Attempting to update Notification Template with ID: {template_id}")
            try:
                updated_template = update_notification_template(db, template_id, template_update)
                self.logger.info(f"Notification Template updated with ID: {updated_template.id}")
                return updated_template
            except ValueError as e:
                self.logger.error(f"Error updating Notification Template: {str(e)}")
                raise HTTPException(status_code=404, detail=str(e))

        @router.delete("/{template_id}")
        def delete_notification_template_endpoint(template_id: int, db: Session = Depends(self.db_session)):
            """Delete a Notification Template"""
            self.logger.info(f"Attempting to delete Notification Template with ID: {template_id}")
            try:
                success = delete_notification_template(db, template_id)
                if not success:
                    raise HTTPException(status_code=404, detail="Notification Template not found")
                self.logger.info(f"Notification Template with ID {template_id} deleted.")
                return {"message": "Notification Template deleted successfully"}
            except ValueError as e:
                self.logger.error(f"Error deleting Notification Template: {str(e)}")
                raise HTTPException(status_code=404, detail=str(e))

        return router
