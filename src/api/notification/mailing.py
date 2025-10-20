from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.notification.mailing import send_mail, bulk_send
from src.core.logging import logger
from src.internal.notification.mailing import MailRequest, BulkMailRequest
from typing import List
from src.api.endpoint import BaseEndpoint

class MailingEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger  # Use your own logger setup or standard logging

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/mailing")

        @router.post("/send", response_model=dict)
        def send_mail_endpoint(mail_request: MailRequest, db: Session = Depends(self.db_session)):
            """Send a single email"""
            self.logger.info(f"Attempting to send an email to {mail_request.recipient_emails}")
            try:
                result = send_mail(mail_request)  # Calls the sendMail function from mailing.py
                self.logger.info(f"Email sent successfully to {mail_request.recipient_emails}")
                return {"message": "Email sent successfully", "result": result}
            except Exception as e:
                self.logger.error(f"Error sending email: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error sending email: {str(e)}")

        @router.post("/send/bulk", response_model=dict)
        def bulk_send_mail_endpoint(bulk_mail_request: BulkMailRequest, db: Session = Depends(self.db_session)):
            """Send emails in bulk to multiple recipients"""
            self.logger.info(f"Attempting to send bulk emails to {bulk_mail_request.recipients}")
            try:
                result = bulk_send(bulk_mail_request)  # Calls the bulkSend function from mailing.py
                self.logger.info(f"Bulk email sent successfully to {len(bulk_mail_request.recipients)} recipients")
                return {"message": f"Bulk email sent to {len(bulk_mail_request.recipients)} recipients", "result": result}
            except Exception as e:
                self.logger.error(f"Error sending bulk email: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error sending bulk email: {str(e)}")

        return router
