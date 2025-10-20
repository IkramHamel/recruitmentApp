
from sqlalchemy import Column, Integer, DateTime,JSON,ForeignKey,Boolean
from src.db.session import Base
from datetime import datetime, timezone ,timedelta
from sqlalchemy.orm import relationship

class Result(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer, nullable=False)
    responses = Column(JSON, nullable=False)  
    date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
    is_cheating = Column(Boolean, default=False, nullable=False)
    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt =  Column(DateTime, onupdate=datetime.now(timezone.utc),default=datetime.now(timezone.utc))
    job_candidate = relationship("JobCandidate", back_populates="results")
    jobcandidate_id = Column(Integer, ForeignKey("job_candidates.id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    