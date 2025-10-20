from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.exam.responses.models import Response  # Modèle ORM
from src.internal.exam.responses.schemas import ResponseCreate, ResponseUpdate, Response as ResponseSchema
from src.internal.exam.responses import (
    create_response,
    get_responses,
    get_response_by_id,
    update_response,
    delete_response
)
from typing import List
from src.api.endpoint import BaseEndpoint
from src.core.logging import logger
# from src.api.middlewares.authz import has_permission

class ResponsesEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/responses")

        @router.post("/", response_model=ResponseSchema)
        def create_response_endpoint(response_data: ResponseCreate, db: Session = Depends(self.db_session)):
            created_response = create_response(db, response_data)
            return created_response

        @router.get("/", response_model=List[ResponseSchema])
        def get_all_responses_endpoint(db: Session = Depends(self.db_session)):
            responses = get_responses(db)
            return responses

        @router.get("/{response_id}", response_model=ResponseSchema)
        def get_response_endpoint(response_id: int, db: Session = Depends(self.db_session)):
            response = get_response_by_id(db, response_id)
            return response

        @router.put("/{response_id}", response_model=ResponseSchema)
        def update_response_endpoint(response_id: int, response_update: ResponseUpdate, db: Session = Depends(self.db_session)):
            updated_response = update_response(db, response_id, response_update)
            return updated_response

        @router.delete("/{response_id}")
        def delete_response_endpoint(response_id: int, db: Session = Depends(self.db_session)):
            success = delete_response(db, response_id)
            if not success:
                raise HTTPException(status_code=404, detail="Response not found")
            return {"message": "Response deleted successfully"}

        return router
