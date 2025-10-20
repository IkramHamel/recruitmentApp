from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from ..responses.schemas import Response,ResponseCreate ,ResponseExam
class QuestionBase(BaseModel):
    label: str
    nbPoints: int
    question_type: str
    responses: Optional[List[ResponseCreate]] = None


class QuestionCreate(QuestionBase):
    pass
class QuestionUpdate(QuestionBase):
    pass
class QuestionResponse(QuestionBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    responses: Optional[List[Response]]= None
    image: Optional[str] = None
    class Config:
        from_attributes = True
class QuestionResponseExam(BaseModel):
    id: int
    responses: Optional[List[ResponseExam]] = None
    label: str
    nbPoints: int
    question_type: str
    image: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    class Config:
        from_attributes = True
