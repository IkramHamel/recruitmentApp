from pydantic import BaseModel, EmailStr
from typing import List, Literal

# Schema for a single email request
class MailRequest(BaseModel):
    subject: str
    recipient_emails: List[EmailStr]
    body: str
    content_type: str = 'text'  # Default content type is 'text'. Can be 'html' as well.


# Schema for a bulk email request
class BulkMailRequest(BaseModel):
    subject: str
    body: str
    recipients: List[EmailStr]
    content_type: Literal["text", "html"] = "text"  # Default to "text"
