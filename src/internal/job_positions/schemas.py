from __future__ import annotations
from typing import Optional, List
from datetime import date, datetime
import uuid
from pydantic import BaseModel
from .models import JobType, CandidatePhase
from src.internal.exam.results.schemas import ResultResponse

# --- Candidate Verification ---
class CandidateVerificationData(BaseModel):
    email: str
    evaluation_code: str

# --- JobPhase schemas ---
class JobPhaseOut(BaseModel):
    id: int
    phase: CandidatePhase
    title: Optional[str] = None
    assessment_id: Optional[int] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobPhaseCreate(BaseModel):
    id: Optional[int] = None
    phase: CandidatePhase
    title: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    assessment_id: Optional[int] = None

# --- JobKeyword schemas ---
class JobKeywordBase(BaseModel):
    job_id: int
    keyword: str

class JobKeywordCreate(JobKeywordBase):
    pass

class JobKeywordOut(JobKeywordBase):
    id: int

    class Config:
        from_attributes = True

# --- CV and CVCandidate schemas ---
class CVVersionBase(BaseModel):
    cv_hash: str
    url_cv: str
    analysis_done: bool = False


class CVVersionCreate(CVVersionBase):
    pass

class CVVersionOut(CVVersionBase):
    id: int
    uploaded_at: datetime
    matches: List["CVCandidateOut"] = []  
    strengths: Optional[List["CandidateStrengthOut"]] = []
    areas_for_improvement: List["CandidateAreaForImprovementOut"] = []
    personal_information: Optional["PersonalInformationOut"] = None
    education: List["EducationOut"] = []
    work_experience: List["WorkExperienceOut"] = []
    certifications: List["CertificationOut"] = []
    languages: List["LanguageOut"] = []
    projects: List["ProjectOut"] = []
    awards_and_honors: List["AwardAndHonorOut"] = []
    volunteer_work: List["VolunteerWorkOut"] = []


    class Config:
        from_attributes = True

class CVCandidateBase(BaseModel):
    cv_version_id: int
    match_score: Optional[int] = None
    skills_match: Optional[int] = None
    experience_match: Optional[int] = None
    cultural_fit_feedback: Optional[str] = None
    overall_feedback: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recommendation: Optional[str] = None
    decision_reasoning: Optional[str] = None

class CVCandidateCreate(CVCandidateBase):
    pass

class CVCandidateOut(CVCandidateBase):
    id: int
    cv_version_id: int
    class Config:
        from_attributes = True

# --- JobCandidate schemas ---
class JobCandidateBase(BaseModel):
    job_id: Optional[int] = None
    SponsorName: Optional[str] = None
    job_phase_id: Optional[int] = None
    cv_version_id: Optional[int] = None
    cv_candidate_id: Optional[int] = None
    quiz_submitted: bool = False
    quiz_started_at: Optional[datetime] = None
    quiz_expires_at: Optional[datetime] = None

class JobPositionBase(BaseModel):
    name: str
    description: Optional[str] = None
    criteres: Optional[str] = None
    resumeJob: Optional[str] = None
    posted: Optional[bool] = False
    limitePostes: Optional[bool] = False
    job_type: JobType
    nbpostes: Optional[int] = None

class JobPositionCreate(JobPositionBase):
    responsabilities: str
    desired_profile: str
    keywords: List[str]
    jobsources: Optional[str] = None
    phases: List[JobPhaseCreate]


class JobCandidateCreate(JobCandidateBase):
    candidate_id: int   # obligatoire quand on crée un JobCandidate
class JobCandidateResponse(BaseModel):
    job_id: int  
    id: int
    evaluation_code: Optional[str] = None
    quiz_submitted: bool
    quiz_started_at: Optional[datetime] = None
    quiz_expires_at: Optional[datetime] = None
    candidate: Optional[CandidateResponse] = None 
    job_phase: Optional[JobPhaseOut] = None
    cv_version: Optional[CVVersionOut] = None
    
    results: List[ResultResponse] = []
    
    class Config:
        from_attributes = True
class JobPositionResponse(JobPositionBase):
    id: int
    uuid: uuid.UUID
    keywords: List[JobKeywordOut]
    responsabilities: str
    desired_profile: str

    job_candidates: List[JobCandidateResponse] = []
    phases: List[JobPhaseOut] = []

    class Config:
        from_attributes = True

# --- Candidate schemas ---
class CandidateBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(BaseModel):
    uuid: uuid.UUID
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    # relations
    #applications: List[JobCandidateResponse] = []
    cv_versions: List[CVVersionOut] = []


    class Config:
        form_attributes = True


# --- Candidate Strength & Improvement schemas ---
class CandidateStrengthBase(BaseModel):
    cv_versions_id: Optional[int] = None
    strength: Optional[str] = None

class CandidateStrengthCreate(CandidateStrengthBase):
    pass

class CandidateStrengthOut(CandidateStrengthBase):
    id: int
    class Config:
        form_attributes = True


class CandidateAreaForImprovementBase(BaseModel):
    cv_versions_id: Optional[int] = None
    area_for_improvement: Optional[str] = None

class CandidateAreaForImprovementCreate(CandidateAreaForImprovementBase):
    pass

class CandidateAreaForImprovementOut(CandidateAreaForImprovementBase):
    id: int
    class Config:
        form_attributes = True

# --- Personal Information schemas ---
class PersonalInformationBase(BaseModel):
    summary: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    linkedin: Optional[str]
    cv_versions_id: int

class PersonalInformationCreate(PersonalInformationBase):
    pass

class PersonalInformationOut(PersonalInformationBase):
    id: int
    class Config:
        form_attributes = True

# --- Education, WorkExperience, Certification, Language, Project, Award, Volunteer schemas ---
class EducationBase(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    location: Optional[str]
    cv_versions_id: int
class JobDescriptionRequest(BaseModel):
    name: Optional[str] = None
    desired_profile: Optional[str] = None
    responsabilities: Optional[str] = None
    criteres: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class EducationOut(EducationBase):
    id: int
    class Config:
        form_attributes = True

class WorkExperienceBase(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    responsibilities: Optional[str]
    achievements: Optional[str]
    cv_versions_id: int

class WorkExperienceCreate(WorkExperienceBase):
    pass

class WorkExperienceOut(WorkExperienceBase):
    id: int
    class Config:
        form_attributes = True

class CertificationBase(BaseModel):
    certification_name: Optional[str] = None
    institution: Optional[str] = None
    date_earned: Optional[date]
    cv_versions_id: int

class CertificationCreate(CertificationBase):
    pass

class CertificationOut(CertificationBase):
    id: int
    class Config:
        form_attributes = True

class LanguageBase(BaseModel):
    language: Optional[str] = None
    proficiency: Optional[str]
    cv_versions_id: int

class LanguageCreate(LanguageBase):
    pass

class LanguageOut(LanguageBase):
    id: int
    class Config:
        form_attributes = True

class ProjectBase(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str]
    dates: Optional[str]
    role: Optional[str]
    cv_versions_id: int

class ProjectCreate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    class Config:
        form_attributes = True

class AwardAndHonorBase(BaseModel):
    award_name: Optional[str] = None
    institution: Optional[str]
    date_awarded: Optional[date]
    cv_versions_id: int

class AwardAndHonorCreate(AwardAndHonorBase):
    pass

class AwardAndHonorOut(AwardAndHonorBase):
    id: int
    class Config:
        form_attributes = True

class VolunteerWorkBase(BaseModel):
    role: Optional[str] = None
    organization: Optional[str]
    dates: Optional[str]
    description: Optional[str]
    cv_versions_id: int

class VolunteerWorkCreate(VolunteerWorkBase):
    pass

class VolunteerWorkOut(VolunteerWorkBase):
    id: int
    class Config:
        form_attributes = True

# --- JobPosition schemas ---

class CandidatePhaseUpdate(BaseModel):
    id: int
    job_phase_id: int
    evaluation_code: Optional[str] = None

    class Config:
        form_attributes = True

