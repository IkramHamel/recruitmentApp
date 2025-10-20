from sqlalchemy import Column, Integer, String, Enum, DateTime
from src.db.session import Base
from .providers import Providers
from datetime import datetime, timezone

class Reasoners(Base):
    __tablename__ = 'reasoners'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    provider = Column(Enum(Providers), nullable=False)
    api_key = Column(String, nullable=False)
    model_id = Column(String, nullable=False)

    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt = Column(DateTime, onupdate=datetime.now(timezone.utc),default=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Reasoners(id={self.id}, name={self.name}, provider={self.provider}, model={self.model_id})>"
