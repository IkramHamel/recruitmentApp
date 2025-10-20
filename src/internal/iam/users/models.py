# app/modules/settings/users/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from src.db.session import Base
from datetime import datetime, timezone
from src.internal.iam.roles.models import Role
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))  
    role= relationship("Role",back_populates="users")       
    lastLogin = Column(DateTime, nullable=True)
    lastLoginIP = Column(String, nullable=True)

    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt =  Column(DateTime, onupdate=datetime.now(timezone.utc),default=datetime.now(timezone.utc))
    

 