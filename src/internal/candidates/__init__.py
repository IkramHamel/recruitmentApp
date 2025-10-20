'''
from sqlalchemy.orm import Session
from src.internal.candidates.models import Candidate, Resume
from src.internal.candidates.schemas import CandidateCreate, ResumeCreate

# Candidate CRUD operations
def create_candidate(db: Session, candidate: CandidateCreate):
    db_candidate = Candidate(
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        email=candidate.email,
        url_cv=candidate.url_cv,
        cv_file_path=candidate.cv_file_path,
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate



def get_candidates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Candidate).offset(skip).limit(limit).all()


def get_candidate(db: Session, candidate_id: int):
    return db.query(Candidate).filter(Candidate.id == candidate_id).first()


# Resume CRUD operations
def create_resume(db: Session, resume: ResumeCreate, candidate_id: int):
    db_resume = Resume(**resume.dict(), candidate_id=candidate_id)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


def get_resumes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Resume).offset(skip).limit(limit).all()


def get_resume(db: Session, resume_id: int):
    return db.query(Resume).filter(Resume.id == resume_id).first()

'''