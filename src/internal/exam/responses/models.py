
from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Boolean
from src.db.session import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class Response(Base):
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False,default=False)
    question_id = Column(Integer, ForeignKey("questions.id"))
    question = relationship("Question", back_populates="responses")
    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt =  Column(DateTime, onupdate=datetime.now(timezone.utc),default=datetime.now(timezone.utc))
    

 