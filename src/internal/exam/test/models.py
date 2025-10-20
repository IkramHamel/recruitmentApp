
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Table
from src.db.session import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

test_questions_association = Table(
    "test_questions",
    Base.metadata,
    Column("test_id", Integer, ForeignKey("tests.id"), primary_key=True),
    Column("question_id", Integer, ForeignKey("questions.id"), primary_key=True)
    
)
def get_association_table():
    from ..assessment.models import assessment_test_association
    return assessment_test_association

class Test(Base):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
      
    assessments = relationship("Assessment", secondary=get_association_table, back_populates="tests")

    questions = relationship("Question", secondary=test_questions_association, back_populates="tests")
    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt =  Column(DateTime, onupdate=datetime.now(timezone.utc),default=datetime.now(timezone.utc))
    

 