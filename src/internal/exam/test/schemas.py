from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from ..questions.schemas import QuestionResponse,QuestionResponseExam
class TestBase(BaseModel):
    title: str
    description: str

class TestCreate(TestBase):
    pass
class TestUpdate(TestBase):
    question_ids: Optional[List[int]]

class TestResponse(TestBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    questions: Optional[List[QuestionResponse]]= None


    class Config:
        from_attributes = True
class TestResponseExam(TestBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    questions: Optional[List[QuestionResponseExam]]= None


    class Config:
        from_attributes = True
