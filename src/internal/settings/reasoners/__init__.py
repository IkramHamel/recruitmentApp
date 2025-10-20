from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import Reasoners
from .schemas import ReasonerCreate, ReasonerUpdate, ReasonerResponse
from .providers import SUPPORTED_PROVIDERS, Providers
from typing import List
from .providers.base import LLMProvider

from .providers.groq_cloud import GroqCloudProvider
from .providers.gemini import GeminiProvider

# Function to get the list of supported providers
def get_supported_providers() -> List[str]:
    return SUPPORTED_PROVIDERS


# Create new Reasoner
def create_reasoner(db: Session, reasoner_create: ReasonerCreate) -> ReasonerResponse:
    db_reasoner = Reasoners(
        name=reasoner_create.name,
        provider=reasoner_create.provider,
        api_key=reasoner_create.api_key,
        model_id=reasoner_create.model_id
    )
    try:
        db.add(db_reasoner)
        db.commit()
        db.refresh(db_reasoner)
        return ReasonerResponse.model_validate(db_reasoner)
    except IntegrityError:
        db.rollback()
        raise ValueError("Reasoner entry with this configuration already exists.")

# Get all Reasoners
def get_reasoners(db: Session) -> List[ReasonerResponse]:
    db_reasoners = db.query(Reasoners).all()
    if db_reasoners:
        return [ReasonerResponse.model_validate(reasoner) for reasoner in db_reasoners]
    return []

# Get Reasoner by ID
def get_reasoner_by_id(db: Session, reasoner_id: int) -> ReasonerResponse:
    db_reasoner = db.query(Reasoners).filter(Reasoners.id == reasoner_id).first()
    if db_reasoner:
        return ReasonerResponse.model_validate(db_reasoner)
    return None

# Update Reasoner
def update_reasoner(db: Session, reasoner_id: int, reasoner_update: ReasonerUpdate) -> ReasonerResponse:
    db_reasoner = db.query(Reasoners).filter(Reasoners.id == reasoner_id).first()

    if db_reasoner:
        if reasoner_update.name:
            db_reasoner.name = reasoner_update.name
        if reasoner_update.provider:
            db_reasoner.provider = reasoner_update.provider
        if reasoner_update.api_key:
            db_reasoner.api_key = reasoner_update.api_key

        db.commit()
        db.refresh(db_reasoner)
        return ReasonerResponse.model_validate(db_reasoner)
    else:
        raise ValueError(f"Reasoner with ID {reasoner_id} not found.")

# Delete Reasoner
def delete_reasoner(db: Session, reasoner_id: int) -> bool:
    db_reasoner = db.query(Reasoners).filter(Reasoners.id == reasoner_id).first()

    if db_reasoner:
        db.delete(db_reasoner)
        db.commit()
        return True
    else:
        raise ValueError(f"Reasoner with ID {reasoner_id} not found.")

def getLLMProvider(db: Session, reasoner_id: int) -> LLMProvider:
    db_reasoner = db.query(Reasoners).filter(Reasoners.id == reasoner_id).first()

    if db_reasoner:
        if db_reasoner.provider == Providers.GroqCloud:
            return GroqCloudProvider()
        elif db_reasoner.provider == Providers.Gemini:
            return GeminiProvider()
    return None
