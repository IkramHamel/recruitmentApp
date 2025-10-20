
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ResponseBase(BaseModel):
    question_id: int
    selected_response_ids: List[int] 

class ResultBase(BaseModel):
    score: int
    responses: List[ResponseBase] 
    jobcandidate_id: int
    assessment_id: int

class ResultCreate(ResultBase):
    is_cheating: Optional[bool] = False

class ResultResponse(ResultBase):
    id: int
    is_cheating: Optional[bool] = False

    date: datetime
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True
