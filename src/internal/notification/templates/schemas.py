from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import ContentType



# Schema for creating a new NotificationTemplate
class NotificationTemplateCreate(BaseModel):
    title: str
    content: str
    contentType: ContentType  # New field for content type (text or HTML)

# Schema for updating an existing NotificationTemplate
class NotificationTemplateUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[ContentType] = None
    contentType: Optional[str] = None  # Optional field for content type

    

# Schema for returning NotificationTemplate data
class NotificationTemplateResponse(BaseModel):
    id: int
    title: str
    content: str
    contentType: ContentType  # New field for content type
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True  # Tells Pydantic to treat SQLAlchemy models as dicts
