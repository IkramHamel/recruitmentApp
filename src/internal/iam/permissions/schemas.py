from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Schema for creating a permission
class PermissionCreate(BaseModel):
    name: str


# Schema for permission response
class PermissionResponse(BaseModel):
    id: int
    name: str
    description: str

    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        


class GroupPermissionResponse(BaseModel):
    id: int
    name: str
    description: str
    permissions: List[PermissionResponse]  
    createdAt: datetime
    updatedAt: datetime
    
