from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.db.session import Base

'''

class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    url_cv = Column(String(255))
    cv_file_path = Column(String(255))

    # Relationship
    resume = relationship('Resume', uselist=False, back_populates='candidate')


class Resume(Base):
    __tablename__ = 'resume'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    email = Column(String(255), nullable=False)
    address = Column(Text)
    linkedin = Column(String(255))
    professional_summary = Column(Text)

    # Foreign key reference to Candidate
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    candidate = relationship('Candidate', back_populates='resume')

    # Relationships
    education = relationship('Education', back_populates='resume')
    work_experience = relationship('WorkExperience', back_populates='resume')
    skills = relationship('Skill', back_populates='resume')


class Education(Base):
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resume.id'), nullable=False)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    location = Column(String(255))

    resume = relationship('Resume', back_populates='education')


class WorkExperience(Base):
    __tablename__ = 'work_experience'
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resume.id'), nullable=False)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    location = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    responsibilities = Column(Text)
    achievements = Column(Text)

    resume = relationship('Resume', back_populates='work_experience')


class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resume.id'), nullable=False)
    skill_name = Column(String(255), nullable=False)

    resume = relationship('Resume', back_populates='skills')
'''