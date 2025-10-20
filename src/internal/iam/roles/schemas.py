from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from typing import Union


# Schema for creating a role
class RoleCreate(BaseModel):
    name: str
   

class RoleUpdate(BaseModel):
    name: Optional[str] | None
    permissions:  Optional [list[int]] | None

class PermissionResponse(BaseModel):
    id: int
    name: str
    description: str

    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
# Schema for role response
class RoleResponse(BaseModel):
    id: int
    name: str
    permissions: Optional[ List[PermissionResponse]] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
