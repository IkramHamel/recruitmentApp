# models.py
from sqlalchemy import (
    Column, Integer, String, Text, Enum, ForeignKey, Date, Boolean,DateTime,UniqueConstraint,JSON
)
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from src.db.session import Base
from enum import Enum as PyEnum
from src.internal.exam.assessment.models import Assessment
from sqlalchemy.dialects.postgresql import UUID
import uuid

class CandidatePhase(str, PyEnum):
    REGISTERED = "REGISTERED"
    EVALUATION = "EVALUATION"
    INTERVIEW = "INTERVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ON_HOLD = "ON_HOLD"


class JobType(str, PyEnum):
    INTERNSHIP = "INTERNSHIP"
    FULL_TIME = "FULL_TIME"


class JobPhase(Base):
    __tablename__ = 'job_phases'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('job_positions.id', ondelete="CASCADE"), nullable=False)
    phase = Column(Enum(CandidatePhase, native_enum=False), nullable=False)
    title = Column(String,nullable=True)
    job_position = relationship("JobPosition", back_populates="phases")
    job_candidates = relationship("JobCandidate", back_populates="job_phase", cascade="all, delete-orphan")
    assessment = relationship("Assessment", back_populates="phases")
    assessment_id = Column(Integer, ForeignKey('assessments.id', ondelete="SET NULL"), nullable=True)
    startDate = Column(DateTime,nullable=True)
    endDate = Column(DateTime,nullable=True)

class JobPosition(Base):
    __tablename__ = 'job_positions'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    criteres = Column(Text, nullable=False)      
    resumeJob = Column(Text, nullable=False)    
    posted = Column(Boolean, default=False)

    job_type = Column(Enum(JobType, native_enum=False), nullable=False)  
    nbpostes = Column(Integer, nullable=True, default=0)
    limitePostes = Column(Boolean, default=False)

    responsabilities = Column(Text, nullable=False)  
    desired_profile = Column(Text, nullable=False)   
    jobsource = Column(String, nullable=True)  

    keywords = relationship(
        'JobKeyword',
        back_populates='job_position',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    job_candidates = relationship(
        'JobCandidate',
        back_populates='job_position',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    phases = relationship(
        "JobPhase",
        back_populates="job_position",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

  


class JobKeyword(Base):
    __tablename__ = 'job_keywords'

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('job_positions.id'), nullable=False)
    keyword = Column(String(255), nullable=False)

    job_position = relationship('JobPosition', back_populates='keywords')

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)  
    phone_number = Column(String, nullable=True)
    # relations
    applications = relationship("JobCandidate", back_populates="candidate", cascade="all, delete-orphan")
    cv_versions = relationship("CVVersion", back_populates="candidate", cascade="all, delete-orphan")
    


class JobCandidate(Base):
    __tablename__ = 'job_candidates'

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey('job_positions.id', ondelete="CASCADE"), nullable=True)

    SponsorName = Column(String, nullable=True)
    evaluation_code = Column(String, nullable=True, unique=True)
    quiz_submitted = Column(Boolean, default=False, nullable=False)
    quiz_started_at = Column(DateTime, nullable=True)
    quiz_expires_at = Column(DateTime, nullable=True)
    results = relationship("Result", back_populates="job_candidate", cascade="all, delete-orphan")
    job_phase_id = Column(Integer, ForeignKey('job_phases.id', ondelete="CASCADE"), nullable=True)
    cv_version_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"), nullable=True)
    cv_version = relationship(
    "CVVersion",
   
    )
    cv_candidate_id = Column(Integer, ForeignKey('cv_candidates.id', ondelete="CASCADE"), nullable=True)
    cv_candidate = relationship(
    "CVCandidate",
   
    )   
    candidate = relationship("Candidate", back_populates="applications")
    job_phase = relationship("JobPhase", back_populates="job_candidates")    
    job_position = relationship('JobPosition', back_populates='job_candidates')
    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", name="uix_job_candidate"),
    )

class CVCandidate(Base):
    __tablename__ = 'cv_candidates'

    id = Column(Integer, primary_key=True, index=True)
    cv_version_id = Column(Integer, ForeignKey("cv_versions.id", ondelete="CASCADE"), nullable=False )
    match_score = Column(Integer, nullable=True)
    skills_match = Column(Integer, nullable=True)
    experience_match = Column(Integer, nullable=True)
    
    cultural_fit_feedback = Column(String, nullable=True)
    overall_feedback = Column(String, nullable=True)
    
    strengths = Column(JSON, nullable=True)  
    weaknesses = Column(JSON, nullable=True)  
    
    recommendation = Column(String, nullable=True)
    decision_reasoning = Column(String, nullable=True)
    # relations
    cv_version = relationship("CVVersion", back_populates="matches")

    

   
class CVVersion(Base):
    __tablename__ = 'cv_versions'

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    analysis_done = Column(Boolean, default=False)  

    cv_hash = Column(String, nullable=False, unique=True)  # hash pour vérifier doublon
    url_cv = Column(String, nullable=False)   # URL du fichier CV
    uploaded_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))

    # relations
    candidate = relationship("Candidate", back_populates="cv_versions")
    matches = relationship("CVCandidate", back_populates="cv_version", cascade="all, delete-orphan")  

    strengths = relationship('CandidateStrength', back_populates='cv_versions', cascade='all, delete-orphan')
    areas_for_improvement = relationship('CandidateAreaForImprovement', back_populates='cv_versions', cascade='all, delete-orphan')
    personal_information = relationship(
    'PersonalInformation',
    uselist=False,
    back_populates='cv_versions',
    cascade='all, delete-orphan',  
    passive_deletes=True            
    )
    education = relationship('Education', back_populates='cv_versions', cascade='all, delete-orphan')
    work_experience = relationship('WorkExperience', back_populates='cv_versions', cascade='all, delete-orphan')
    certifications = relationship('Certification', back_populates='cv_versions', cascade='all, delete-orphan')
    languages = relationship('Language', back_populates='cv_versions', cascade='all, delete-orphan')
    projects = relationship('Project', back_populates='cv_versions', cascade='all, delete-orphan')
    awards_and_honors = relationship('AwardAndHonor', back_populates='cv_versions', cascade='all, delete-orphan')
    volunteer_work = relationship('VolunteerWork', back_populates='cv_versions', cascade='all, delete-orphan')


class CandidateStrength(Base):
    __tablename__ = 'candidate_strengths'

    id = Column(Integer, primary_key=True, index=True)
    cv_versions_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"),  nullable=False)
    strength = Column(Text, nullable=False)

    cv_versions = relationship('CVVersion', back_populates='strengths')


class CandidateAreaForImprovement(Base):
    __tablename__ = 'candidate_areas_for_improvement'

    id = Column(Integer, primary_key=True, index=True)
    cv_versions_id = Column(Integer,ForeignKey('cv_versions.id', ondelete="CASCADE"),  nullable=False)
    area_for_improvement = Column(Text, nullable=False)

    cv_versions = relationship('CVVersion', back_populates='areas_for_improvement')


class PersonalInformation(Base):
    __tablename__ = 'candidate_personal_information'

    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    linkedin = Column(String, nullable=True)
    cv_versions_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"), nullable=False)

    cv_versions = relationship('CVVersion', back_populates='personal_information')


class Education(Base):
    __tablename__ = 'candidate_education'

    id = Column(Integer, primary_key=True, index=True)
    degree = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    location = Column(String, nullable=True)
    cv_versions_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"), nullable=False)
    cv_versions = relationship('CVVersion', back_populates='education')


class WorkExperience(Base):
    __tablename__ = 'candidate_work_experience'

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    responsibilities = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)
    cv_versions_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"), nullable=False)

    cv_versions = relationship('CVVersion', back_populates='work_experience')


class Certification(Base):
    __tablename__ = 'candidate_certifications'

    id = Column(Integer, primary_key=True, index=True)
    certification_name = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    date_earned = Column(Date, nullable=True)
    cv_versions_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"), nullable=False)

    cv_versions = relationship('CVVersion', back_populates='certifications')

class Language(Base):
    __tablename__ = 'candidate_languages'

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String, nullable=False)
    proficiency = Column(String, nullable=True)
    cv_versions_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"), nullable=False)

    cv_versions = relationship('CVVersion', back_populates='languages')


class Project(Base):
    __tablename__ = 'candidate_projects'

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    dates = Column(String, nullable=True)
    role = Column(String, nullable=True)
    cv_versions_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"), nullable=False)

    cv_versions = relationship('CVVersion', back_populates='projects')


class AwardAndHonor(Base):
    __tablename__ = 'candidate_awards_and_honors'

    id = Column(Integer, primary_key=True, index=True)
    award_name = Column(String, nullable=False)
    institution = Column(String, nullable=True)
    date_awarded = Column(Date, nullable=True)
    cv_versions_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"), nullable=False)
    cv_versions = relationship('CVVersion', back_populates='awards_and_honors')

class VolunteerWork(Base):
    __tablename__ = 'candidate_volunteer_work'
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    dates = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    cv_versions_id = Column(Integer, ForeignKey('cv_versions.id', ondelete="CASCADE"), nullable=False)
    cv_versions = relationship('CVVersion', back_populates='volunteer_work')
