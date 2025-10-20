'''
from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class CandidateBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    url_cv: Optional[str] = None
    cv_file_path: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: int
    resume: Optional['ResumeResponse'] = None  # Include resume in the output

    class Config:
        orm_mode = True


class EducationBase(BaseModel):
    degree: str
    institution: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = None


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: int

    class Config:
        orm_mode = True


class WorkExperienceBase(BaseModel):
    job_title: str
    company_name: str
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    responsibilities: Optional[str] = None
    achievements: Optional[str] = None


class WorkExperienceCreate(WorkExperienceBase):
    pass


class WorkExperienceResponse(WorkExperienceBase):
    id: int

    class Config:
        orm_mode = True


class SkillBase(BaseModel):
    skill_name: str


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: int

    class Config:
        orm_mode = True


class ResumeBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: str
    address: Optional[str] = None
    linkedin: Optional[str] = None
    professional_summary: Optional[str] = None
    education: Optional[List[EducationCreate]] = []
    work_experience: Optional[List[WorkExperienceCreate]] = []
    skills: Optional[List[SkillCreate]] = []


class ResumeCreate(ResumeBase):
    pass


class ResumeResponse(ResumeBase):
    id: int
    candidate_id: int

    class Config:
        orm_mode = True
'''