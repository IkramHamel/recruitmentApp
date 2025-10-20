from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from src.db.session import Base
from enum import Enum as pyEnum

class ContentType(pyEnum):
    PLAIN_TEXT = "PLAIN_TEXT"
    HTML = "HTML"


class NotificationTemplate(Base):
    __tablename__ = 'notification_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    contentType = Column(Enum(ContentType), nullable=False)  # New field to indicate text or HTML content type
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
