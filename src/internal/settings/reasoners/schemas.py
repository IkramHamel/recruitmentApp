from pydantic import BaseModel
from typing import Optional
from .providers import Providers
from datetime import datetime


# Pydantic schema for creating Reasoners
class ReasonerCreate(BaseModel):
    name: str
    provider: Providers
    api_key: str
    model_id: str

# Pydantic schema for updating Reasoners
class ReasonerUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[Providers] = None
    api_key: Optional[str] = None
    model_id: Optional[str] = None





# Pydantic schema for the Reasoners response
class ReasonerResponse(BaseModel):
    id: int
    name: str
    provider: Providers
    api_key: str
    model_id: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True  # Tells Pydantic to treat SQLAlchemy models as dicts
