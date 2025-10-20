
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Table
from src.db.session import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

assessment_test_association = Table(
    "assessment_test",
    Base.metadata,
    Column("assessment_id", Integer, ForeignKey("assessments.id"), primary_key=True),
    Column("test_id", Integer, ForeignKey("tests.id"), primary_key=True)
)

class Assessment(Base):
    __tablename__ = 'assessments'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    duration  = Column(Integer, nullable=False)
    rules_id = Column(Integer, ForeignKey('rules.id', ondelete="SET NULL"), nullable=True)
    rules = relationship("AntiCheatRule", back_populates="assessments")
    tests = relationship("Test", secondary=assessment_test_association, back_populates="assessments")
    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt =  Column(DateTime, onupdate=datetime.now(timezone.utc),default=datetime.now(timezone.utc))
    results = relationship("Result", backref="assessments")
    phases = relationship("JobPhase", back_populates="assessment")


 