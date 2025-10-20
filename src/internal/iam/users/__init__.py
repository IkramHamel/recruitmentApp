
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .models import User
from .schemas import UserCreate, UserUpdate, UserResponse
from src.utils.bcrypt import hash_password
from typing import List
from datetime import datetime, timezone

# Create User
def create_user(db: Session, user_create: UserCreate) -> UserResponse:
    hashed_password = hash_password(user_create.password)
    db_user = User(
        firstName=user_create.firstName,
        lastName=user_create.lastName,
        username=user_create.username,
        email=user_create.email,
        password=hashed_password,
        role_id = user_create.role_id,
        createdAt = datetime.now(timezone.utc)   
    
              )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserResponse.model_validate(db_user)
    except IntegrityError:
        db.rollback()
        raise ValueError("Username or email already exists.")




# Get Users
def get_users(db: Session) -> List[UserResponse]:
    db_users = db.query(User).all()
    return [UserResponse.model_validate(user) for user in db_users]


# Get User by ID
def get_user_by_id(db: Session, user_id: int) -> UserResponse:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        return UserResponse.model_validate(db_user)
    return None


# Get User by Username
def get_user_by_username(db: Session, username: str) -> UserResponse:
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        return UserResponse.model_validate(db_user)
    return None

def get_user_by_username_for_auth(db: Session, username: str) -> User:
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        return db_user
    return None


# Update User
def update_user(db: Session, user_id: int, user_update: UserUpdate) -> UserResponse:
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if db_user:
        if user_update.firstName:
            db_user.firstName = user_update.firstName
        if user_update.lastName:
            db_user.lastName = user_update.lastName
        if user_update.username:
            db_user.username = user_update.username
        if user_update.email:
            db_user.email = user_update.email
        if user_update.role_id:
            db_user.role_id = user_update.role_id
        
        db_user.updatedAt = datetime.now(timezone.utc)   

        db.commit()
        db.refresh(db_user)
        return UserResponse.model_validate(db_user)
    else:
        raise ValueError(f"User with ID {user_id} not found.")


# Delete User
def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    else:
        raise ValueError(f"User with ID {user_id} not found.")
