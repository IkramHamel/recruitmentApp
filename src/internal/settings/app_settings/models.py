from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from src.db.session import Base
from enum import Enum as pyEnum


class SetupStatus(pyEnum):
    UNFINISHED = 0
    DONE = 1


class AppSettings(Base):
    __tablename__ = 'app_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_name = Column(String, nullable=False)
    setup_status = Column(Enum(SetupStatus), nullable=False)  # 0 => not setup, 1 => Done
    # Foreign key for the default_language
    default_language = Column(String, ForeignKey('app_supported_languages.language'))
    
    # Relationship to SupportedLanguages
    default_language_rel = relationship("SupportedLanguages", back_populates="app_settings", uselist=False)


class SupportedLanguages(Base):
    __tablename__ = 'app_supported_languages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String, unique=True, nullable=False)
    icon = Column(String, nullable=False)
    
    # Relationship to AppSettings
    app_settings = relationship("AppSettings", back_populates="default_language_rel", uselist=False)
