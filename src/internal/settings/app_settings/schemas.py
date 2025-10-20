from pydantic import BaseModel
from typing import Optional,List
from .models import SetupStatus


# Pydantic schema for creating AppSettings
class AppSettingsCreate(BaseModel):
    organization_name: str
    setup_status: SetupStatus  # 0 => Organization config, 1 => Admin Account, etc.
    default_language: str

# Pydantic schema for updating AppSettings
class AppSettingsUpdate(BaseModel):
    organization_name: str
    default_language: Optional[str]


class AvailableTimezones(BaseModel):
    timezones: List[str]


# Pydantic schema for returning AppSettings with the default_reasoner
class AppSettingsResponse(BaseModel):
    id: int
    organization_name: str
    setup_status: SetupStatus
    default_language: str

    class Config:
        from_attributes = True  # Tells Pydantic to treat SQLAlchemy models as dicts


# Pydantic schema for returning App Supported Languages with the default_reasoner
class SupportedLanguageResponse(BaseModel):
    id: int
    language: str
    icon: str

    class Config:
        from_attributes = True  # Tells Pydantic to treat SQLAlchemy models as dicts