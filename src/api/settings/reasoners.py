from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.logging import logger
from src.internal.settings.reasoners.schemas import ReasonerCreate, ReasonerUpdate, ReasonerResponse
from src.internal.settings.reasoners import create_reasoner, get_reasoners, get_reasoner_by_id, update_reasoner, delete_reasoner, get_supported_providers
from src.api.endpoint import BaseEndpoint


class ReasonersEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger  # Use your own logger setup or standard logging

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/reasoners")
        
        @router.get("/providers", response_model=List[str])
        def get_providers_endpoint():
            """Fetch all supported providers"""
            self.logger.info("Fetching supported providers")
            providers = get_supported_providers()
            print(providers)
            self.logger.info(f"Found {len(providers)} supported providers")
            return providers
        

        @router.get("/", response_model=List[ReasonerResponse])
        def get_all_reasoners(db: Session = Depends(self.db_session)):
            """Fetch all reasoners"""
            self.logger.info("Attempting to fetch all reasoners")
            db_reasoners = get_reasoners(db)
            self.logger.info(f"Found {len(db_reasoners)} reasoners")
            return db_reasoners

        @router.get("/{reasoner_id}", response_model=ReasonerResponse)
        def get_reasoner_by_id_endpoint(reasoner_id: int, db: Session = Depends(self.db_session)):
            """Fetch a specific reasoner by ID"""
            self.logger.info(f"Attempting to fetch reasoner with ID: {reasoner_id}")
            db_reasoner = get_reasoner_by_id(db, reasoner_id)
            if not db_reasoner:
                self.logger.error(f"Reasoner with ID {reasoner_id} not found.")
                raise HTTPException(status_code=404, detail="Reasoner not found")
            self.logger.info(f"Found reasoner with ID: {db_reasoner.id}")
            return db_reasoner

        @router.post("/", response_model=ReasonerResponse)
        def create_reasoner_endpoint(reasoner_create: ReasonerCreate, db: Session = Depends(self.db_session)):
            """Create a new reasoner"""
            self.logger.info(f"Attempting to create a reasoner with name: {reasoner_create.name}")
            created_reasoner = create_reasoner(db, reasoner_create)
            self.logger.info(f"Created reasoner with ID: {created_reasoner.id}")
            return created_reasoner

        @router.put("/{reasoner_id}", response_model=ReasonerResponse)
        def update_reasoner_endpoint(reasoner_id: int, reasoner_update: ReasonerUpdate, db: Session = Depends(self.db_session)):
            """Update an existing reasoner"""
            self.logger.info(f"Attempting to update reasoner with ID: {reasoner_id}")
            updated_reasoner = update_reasoner(db, reasoner_id, reasoner_update)
            if not updated_reasoner:
                self.logger.error(f"Reasoner with ID {reasoner_id} not found.")
                raise HTTPException(status_code=404, detail="Reasoner not found")
            self.logger.info(f"Updated reasoner with ID: {updated_reasoner.id}")
            return updated_reasoner

        @router.delete("/{reasoner_id}")
        def delete_reasoner_endpoint(reasoner_id: int, db: Session = Depends(self.db_session)):
            """Delete a reasoner by ID"""
            self.logger.info(f"Attempting to delete reasoner with ID: {reasoner_id}")
            success = delete_reasoner(db, reasoner_id)
            if not success:
                self.logger.error(f"Reasoner with ID {reasoner_id} not found.")
                raise HTTPException(status_code=404, detail="Reasoner not found")
            self.logger.info(f"Deleted reasoner with ID: {reasoner_id}")
            return {"message": "Reasoner deleted successfully"}

        return router
