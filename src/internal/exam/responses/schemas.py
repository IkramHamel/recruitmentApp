
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ResponseBase(BaseModel):
    content: str
    is_correct: bool

class ResponseCreate(ResponseBase):
       pass
class ResponseUpdate(ResponseBase):
    question_id: Optional[int]


class Response(ResponseBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
class ResponseExam(BaseModel):
    id: int
    content: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
