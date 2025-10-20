from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.candidates import create_candidate, get_candidates, get_candidate, get_resume,create_resume
from src.internal.candidates.schemas import CandidateCreate, CandidateResponse, ResumeCreate, ResumeResponse
from src.core.logging import logger
from typing import List


class CandidateEndpoints:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_routers(self) -> List[APIRouter]:
        router = APIRouter(prefix="/candidates")

        # Endpoint for getting all candidates
        @router.get("/", response_model=List[CandidateResponse])
        def get_all_candidates_endpoint(db: Session = Depends(self.db_session)):
            """Fetch all candidates."""
            self.logger.info("Fetching all candidates.")
            candidates = get_candidates(db)
            if not candidates:
                self.logger.error("No candidates found.")
                raise HTTPException(status_code=404, detail="No candidates found.")
            return candidates

        # Endpoint for getting a candidate by ID
        @router.get("/{candidate_id}", response_model=CandidateResponse)
        def get_candidate_by_id_endpoint(candidate_id: int, db: Session = Depends(self.db_session)):
            """Fetch a candidate by ID."""
            self.logger.info(f"Fetching candidate with ID: {candidate_id}")
            candidate = get_candidate(db, candidate_id)
            if not candidate:
                self.logger.error(f"Candidate with ID {candidate_id} not found.")
                raise HTTPException(status_code=404, detail="Candidate not found.")
            return candidate

        # Endpoint for fetching a candidate's resume
        @router.get("/{candidate_id}/resume", response_model=ResumeResponse)
        def get_resume_for_candidate(candidate_id: int, db: Session = Depends(self.db_session)):
            """Fetch the resume for a specific candidate."""
            self.logger.info(f"Fetching resume for candidate ID: {candidate_id}")
            resume = get_resume(db, candidate_id)
            if not resume:
                self.logger.error(f"No resume found for candidate ID {candidate_id}.")
                raise HTTPException(status_code=404, detail="Resume not found.")
            return resume

        return [router]
