# app/modules/settings/users/models.py
from sqlalchemy import Column, Integer, String, DateTime, Enum,Table,ForeignKey
from src.db.session import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship


role_permission_association = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True)
)
class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False,unique=True)
    users=relationship("User",back_populates="role")
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")

    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt = Column(DateTime, onupdate=datetime.now(timezone.utc),default=datetime.now(timezone.utc))

 