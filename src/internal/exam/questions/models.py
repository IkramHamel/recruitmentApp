
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,JSON,literal
from src.db.session import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from ..test.models import test_questions_association

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    image = Column(String, nullable=True)  
    nbPoints = Column(Integer, nullable=False)
    question_type = Column(String, nullable=False)
    responses = relationship("Response", back_populates="question")
    tests = relationship("Test", secondary=test_questions_association, back_populates="questions")
    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt =  Column(DateTime, onupdate=datetime.now(timezone.utc),default=datetime.now(timezone.utc))
    

 