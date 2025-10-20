from pydantic import BaseModel, EmailStr
from typing import Optional,List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

# Pydantic schema for creating a user
class UserCreate(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: EmailStr
    password: str
    role_id: int
class UserUpdateProfile(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None

    @validator("new_password")
    def validate_new_password(cls, value, values):
        if value and not values.get("old_password"):
            raise ValueError("L'ancien mot de passe est requis pour changer le mot de passe")
        return value

# Pydantic schema for updating a user
class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
class PermissionResponse(BaseModel):
    id: int
    name: str
    description: str

    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
class RoleResponse(BaseModel):
    id: int
    name: str
    permissions: Optional[List[PermissionResponse]] = None

    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
# Pydantic schema for the user response (excluding the password)
class UserResponse(BaseModel):
    id: int
    firstName: str
    lastName: str
    username: str
    email: EmailStr
    role: Optional[RoleResponse]
    lastLogin: Optional[datetime] = None
    lastLoginIP: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str ="bearer"