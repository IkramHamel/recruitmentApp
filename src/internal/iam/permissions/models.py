from sqlalchemy import Column, Integer, String, DateTime, Enum,Table,ForeignKey
from src.db.session import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from ..roles.models import role_permission_association
class GroupPermission(Base):
    __tablename__ = "group_permissions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    permissions = relationship("Permission", back_populates="group")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)  

    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")
    group_id = Column(Integer, ForeignKey("group_permissions.id"))
    group = relationship("GroupPermission", back_populates="permissions")
  