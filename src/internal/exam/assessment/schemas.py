from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from ..test.schemas import TestResponse,TestResponseExam
from ...anti_cheat.schemas import AntiCheatRuleResponse
import uuid

class AssessmentBase(BaseModel):
    title: str
    description: str
    duration: int
    rules_id: Optional[int]=None

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentUpdate(AssessmentBase):
    test_ids: Optional[List[int]]= None



class AssessmentResponse(AssessmentBase):
    id: int
    uuid: uuid.UUID
    createdAt: datetime
    updatedAt: datetime
    tests: Optional[ List[TestResponse]] = None
    rules: Optional[ AntiCheatRuleResponse] = None
    rules_id: Optional[int] = None   # <-- rendre optionnel

    class Config:
        from_attributes = True
class AssessmentResponseExam(AssessmentBase):
    id: int
    uuid: uuid.UUID
    createdAt: datetime
    updatedAt: datetime
    tests: Optional[ List[TestResponseExam]] = None
    rules: Optional[ AntiCheatRuleResponse] = None
    class Config:
        from_attributes = True


