from sqlalchemy.orm import Session 
from .models import (
    AwardAndHonor,Certification,Language,Education,PersonalInformation,Project,VolunteerWork,WorkExperience,
    CandidateAreaForImprovement,CandidateStrength,
    JobPosition,
    JobKeyword,Candidate,
    JobCandidate
    ,CVCandidate,CVVersion,CandidatePhase,JobPhase,CandidateAreaForImprovement,CandidateStrength
)
from sqlalchemy.orm import joinedload

from ..exam.assessment.models import Assessment
from pydantic import BaseModel
from .schemas import (
    JobPositionCreate,
    JobKeywordCreate,
    JobPhaseCreate,
    
    CandidatePhaseUpdate,CandidateVerificationData,CandidateStrengthCreate,
    CandidateAreaForImprovementCreate,
    CandidatePhaseUpdate,CandidateVerificationData
)
from typing import List
from fastapi import FastAPI, File, UploadFile
import random
import string
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from src.db.session import get_db
from uuid import uuid4
import os
import shutil
import hashlib
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from ..IA.analyse_cv import analyze_cv  
from ..IA.scoring_matching import evaluate_candidate,convert_candidate_data_to_text

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"





def get_candidates(db: Session) -> Candidate:
    return (
        db.query(Candidate).all()    )
def get_candidate_by_id(db: Session, candidate_id: int) -> Candidate:
    return db.query(Candidate).filter(Candidate.id == candidate_id).first()
# ---- JobPosition CRUD ----
def create_job_position(db: Session, job: JobPositionCreate) -> JobPosition:
    new_job = JobPosition(
        name=job.name,
        description=job.description,
        criteres=job.criteres,
        resumeJob=job.resumeJob,
        posted=job.posted,
        job_type=job.job_type,
        nbpostes=job.nbpostes,
        limitePostes=job.limitePostes,
        responsabilities=job.responsabilities,
        desired_profile=job.desired_profile,        
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    for k in job.keywords:
        db.add(JobKeyword(job_id=new_job.id, keyword=k))

    for phase in job.phases:
        db.add(JobPhase(job_id=new_job.id, phase=phase.phase, title=phase.title, 
        assessment_id=phase.assessment_id, startDate= phase.startDate, endDate=phase.endDate))


    db.commit()
    db.refresh(new_job)
    return new_job

def get_job_position(db: Session, job_id: int) -> JobPosition:
    return (
        db.query(JobPosition)
        .options(
            joinedload(JobPosition.job_candidates),
            joinedload(JobPosition.phases)
        )
        .filter(JobPosition.id == job_id)
        .first()
    )
def get_job_position_uuid(db: Session, job_uuid: str) -> JobPosition:
    return (
        db.query(JobPosition)
        .options(
            joinedload(JobPosition.job_candidates),
            joinedload(JobPosition.phases)
        )
        .filter(JobPosition.uuid == job_uuid)
        .first()
    )
def get_all_job_positions(db: Session) -> List[JobPosition]:
    
    return (
        db.query(JobPosition)
        .options(
            joinedload(JobPosition.job_candidates),
            joinedload(JobPosition.phases)
        )
        .all()
    )



def parse_datetime(value):
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
    return value  # déjà un datetime

def update_job_position(db: Session, job_id: int, job_data):
    job = db.query(JobPosition).filter(JobPosition.id == job_id).first()
    if not job:
        return None

    # --- Infos principales ---
    for attr in ["name", "description", "criteres", "resumeJob", "posted", "job_type",
                 "nbpostes", "limitePostes", "responsabilities", "desired_profile"]:
        setattr(job, attr, getattr(job_data, attr, getattr(job, attr)))

    # --- Mots-clés ---
    db.query(JobKeyword).filter(JobKeyword.job_id == job.id).delete()
    for kw in job_data.keywords:
        db.add(JobKeyword(job_id=job.id, keyword=kw))

    # --- Phases ---
    existing_phases = {p.id: p for p in db.query(JobPhase).filter(JobPhase.job_id == job.id).all()}
    received_ids = set()

    for phase in job_data.phases:
        phase_id = getattr(phase, "id", None)

        start_date = getattr(phase, "startDate", None)
        end_date = getattr(phase, "endDate", None)

        if start_date:
            start = parse_datetime(start_date) 
        else:
            start = None

        if end_date:
            end = parse_datetime(end_date) 
        else:
            end = None

        if phase_id and phase_id in existing_phases:
            # Update
            p = existing_phases[phase_id]
            p.phase = phase.phase
            p.title = getattr(phase, "title", p.title)
            p.startDate = start
            p.endDate = end
            p.assessment_id = getattr(phase, "assessment_id", None)
            db.add(p)  # important pour trigger UPDATE
            received_ids.add(phase_id)
        else:
            # Nouvelle phase
            p_new = JobPhase(
                job_id=job.id,
                phase=phase.phase,
                title=getattr(phase, "title", None),
                startDate=start,
                endDate=end,
                assessment_id=getattr(phase, "assessment_id", None)
            )
            db.add(p_new)

    # Suppression des phases non reçues
    for pid, p in existing_phases.items():
        if pid not in received_ids:
            if db.query(JobCandidate).filter(JobCandidate.job_phase_id == pid).count() == 0:
                db.delete(p)

    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def update_job_position_posted(db: Session, job_id: int, ) -> JobPosition | None:
    job = db.query(JobPosition).filter(JobPosition.id == job_id).first()
    if not job:
        return None  
    job.posted = not job.posted 

    db.commit()
    db.refresh(job)
    return job


def delete_job_position(db: Session, job_id: int) -> bool:
    job = db.query(JobPosition).filter(JobPosition.id == job_id).first()
    if not job:
        return False
    db.delete(job)
    db.commit()
    return True

# ---- JobKeyword CRUD ----
def create_job_keyword(db: Session, keyword: JobKeywordCreate) -> JobKeyword:
    new_keyword = JobKeyword(**keyword.dict())
    db.add(new_keyword)
    db.commit()
    db.refresh(new_keyword)
    return new_keyword

def get_job_keywords(db: Session, job_id: int) -> List[JobKeyword]:
    return db.query(JobKeyword).filter(JobKeyword.job_id == job_id).all()
def get_all_keywords(db: Session ) -> List[JobKeyword]:
    try:
        # 🔹 Récupère tous les mots-clés de la table JobPosition
        job_positions = db.query(JobPosition.keywords).all()
        
        # 🔹 Extraire les mots-clés (supposé que c'est un tableau ou string)
        keywords = set()
        for jp in job_positions:
            if jp.keywords:
                if isinstance(jp.keywords, list):
                    keywords.update(jp.keywords)
                else:
                    # Si c'est une string séparée par virgule
                    keywords.update([k.strip() for k in jp.keywords.split(",")])

        return list(keywords)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des mots-clés: {e}")


def delete_job_keyword(db: Session, keyword_id: int) -> bool:
    keyword = db.query(JobKeyword).filter(JobKeyword.id == keyword_id).first()
    if not keyword:
        return False
    db.delete(keyword)
    db.commit()
    return True

def update_phase(db: Session, phase_id: int, job_data: JobPhaseCreate):
    phase = db.query(JobPhase).filter(JobPhase.id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase introuvable")

    update_data = job_data.dict(exclude_unset=True)

    for key, value in update_data.items():
        #if key == "startDate" and value:
            #  Ajouter +1 heure
            #setattr(phase, key, value + timedelta(hours=1))
        #elif key == "endDate" and value:
            #  Retirer 1 heure
            #setattr(phase, key, value - timedelta(hours=1))
        
        setattr(phase, key, value)
        #print(f"🔄 Mise à jour de {key} à {value}")

    db.commit()
    db.refresh(phase)
    return phase

# ---- JobCandidate CRUD ----
UPLOAD_DIR = "uploads/cvs"

from fastapi import HTTPException, Form, File, UploadFile, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
import os, shutil

def get_all_jobcandidates(db: Session) -> List[JobCandidate]:
    return db.query(JobCandidate).all()
def get_jobcandidate_by_id(db: Session, candidate_id: int) -> JobCandidate:
    return db.query(JobCandidate).filter(JobCandidate.id == candidate_id).first()
    
def get_job_candidate_uuid(db: Session, candidate_uuid: str) -> JobCandidate:
    return db.query(JobCandidate).filter(JobCandidate.uuid == candidate_uuid).first()
def delete_jobcandidate(db: Session, jobcandidate_id: int) -> bool:
    # 🔹 Récupérer le JobCandidate
    jobcandidate = db.query(JobCandidate).filter(JobCandidate.id == jobcandidate_id).first()
    if not jobcandidate:
        return False

    # 🔹 Sauvegarder l'ID du CVVersion avant suppression (important !)
    cv_version_id = jobcandidate.cv_version_id

    # 🔹 Supprimer le JobCandidate
    db.delete(jobcandidate)
    db.commit()

    # 🔹 Vérifier si d'autres JobCandidate utilisent encore ce CVVersion
    if cv_version_id:
        remaining_links = (
            db.query(JobCandidate)
            .filter(JobCandidate.cv_version_id == cv_version_id)
            .count()
        )

        if remaining_links == 0:
            cv_version = db.query(CVVersion).filter(CVVersion.id == cv_version_id).first()
            if cv_version:
                db.delete(cv_version)
                db.commit()

    return True

def generate_unique_code(length=8):
    """Génère un code alphanumérique aléatoire de la longueur donnée."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def calculate_file_hash(file_path: str) -> str:
    """Calcule le hash SHA256 d’un fichier."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()



from sqlalchemy.exc import IntegrityError
def get_cv_by_job_candidate(db: Session, job_candidate_id: int, candidate_id: int):
    job_candidate = (
        db.query(JobCandidate)
        .filter(
            JobCandidate.id == job_candidate_id,
            JobCandidate.candidate_id == candidate_id
        )
        .first()
    )

    if not job_candidate or not job_candidate.cv_candidate_id:
        return None

    cv_candidate = (
        db.query(CVCandidate)
        .filter(CVCandidate.id == job_candidate.cv_candidate_id)
        .first()
    )

    if not cv_candidate:
        return None

    cv_version = (
        db.query(CVVersion)
        .filter(CVVersion.id == cv_candidate.cv_version_id)
        .first()
    )

    if cv_version:
        cv_version.matches = [cv_candidate]

    return cv_version


def create_job_candidate(
    job_id: int,
    first_name: str,
    last_name: str,
    email: str,
    SponsorName: str,
    phone_number: str,
    file: UploadFile,
    db: Session
) -> tuple[JobCandidate, CVVersion, str]:
    
    # 1️⃣ Vérifier le job
    job = db.query(JobPosition).filter(JobPosition.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable.")

    # 2️⃣ Vérifier le nombre de candidats
    total_candidates = db.query(JobCandidate).filter(JobCandidate.job_id == job_id).count()
    if job.nbpostes and total_candidates >= job.nbpostes:
        raise HTTPException(status_code=400, detail="Nombre maximum de candidatures atteint.")

    # 3️⃣ Vérifier le fichier PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF.")

    # 4️⃣ Enregistrer le fichier temporairement
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    temp_filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, temp_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5️⃣ Calculer hash du CV
    file_hash = calculate_file_hash(file_path)
    url_cv = f"uploads/cvs/{temp_filename}".replace("\\", "/")

    # 6️⃣ Vérifier ou créer le candidat
    candidate = db.query(Candidate).filter(Candidate.email == email).first()
    if not candidate:
        candidate = Candidate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    # 7️⃣ Vérifier ou créer la version du CV
    cv_version = db.query(CVVersion).filter(CVVersion.cv_hash == file_hash).first()
    if not cv_version:
        cv_version = CVVersion(
            candidate_id=candidate.id,
            cv_hash=file_hash,
            url_cv=url_cv
        )
        db.add(cv_version)
        db.commit()
        db.refresh(cv_version)

    # 8️⃣ Phase initiale
    initial_phase = db.query(JobPhase).filter(
        JobPhase.job_id == job_id,
        JobPhase.phase == CandidatePhase.REGISTERED
    ).first()
    if not initial_phase:
        raise HTTPException(status_code=404, detail="Phase initiale 'REGISTERED' introuvable.")

    # 🔟 Créer un CVCandidate pour CE job précis
    cv_candidate = CVCandidate(
            cv_version_id=cv_version.id,
            match_score=None,
            skills_match=None,
            experience_match=None
        )
    db.add(cv_candidate)
    db.commit()
    db.refresh(cv_candidate)
    try:
        # 9️⃣ Créer la candidature au poste
        new_job_candidate = JobCandidate(
            job_id=job_id,
            SponsorName=SponsorName,
            job_phase_id=initial_phase.id,
            candidate_id=candidate.id,
            cv_version_id=cv_version.id,
            cv_candidate_id=cv_candidate.id
        )
        db.add(new_job_candidate)
        db.commit()
        db.refresh(new_job_candidate)

        

    except IntegrityError as e:
        db.rollback()
        if "job_id" in str(e.orig) and "candidate_id" in str(e.orig):
            raise HTTPException(status_code=409, detail="Ce candidat a déjà postulé à ce job.")
        raise HTTPException(status_code=400, detail=f"Erreur d'intégrité : {e.orig}")

    return new_job_candidate, cv_version, file_path

def analyze_cv_background(file_path: str, cv_versions_id: int, db: Session,candidate_id: int):
    cv_data = analyze_cv(file_path,candidate_id)
    print(f"Analyse CV terminée pour le candidat {cv_versions_id}")

    try:
        # 1️⃣ Strengths
        strength_objs = [
            CandidateStrength(cv_versions_id=cv_versions_id, strength=s.strength)
            for s in cv_data.strengths
        ]
        db.bulk_save_objects(strength_objs)

        # 2️⃣ Areas for Improvement
        areas_objs = [
            CandidateAreaForImprovement(cv_versions_id=cv_versions_id, area_for_improvement=a.area)
            for a in getattr(cv_data, "areas_for_improvement", [])
        ]
        db.bulk_save_objects(areas_objs)

        # 3️⃣ Languages
        language_objs = [
            Language(cv_versions_id=cv_versions_id, language=l.language, proficiency=getattr(l, "proficiency", None))
            for l in cv_data.languages
        ]
        db.bulk_save_objects(language_objs)

        # 4️⃣ Education
        education_objs = [
            Education(
                cv_versions_id=cv_versions_id,
                degree=e.degree,
                institution=e.institution,
                start_date=getattr(e, "start_date", None),
                end_date=getattr(e, "end_date", None),
                location=getattr(e, "location", None)
            )
            for e in cv_data.education
        ]
        db.bulk_save_objects(education_objs)

        # 5️⃣ Work Experience
        work_objs = [
            WorkExperience(
                cv_versions_id=cv_versions_id,
                job_title=w.job_title,
                company_name=w.company_name,
                location=getattr(w, "location", None),
                start_date=getattr(w, "start_date", None),
                end_date=getattr(w, "end_date", None),
                responsibilities=getattr(w, "responsibilities", None),
                achievements=getattr(w, "achievements", None)
            )
            for w in cv_data.work_experience
        ]
        db.bulk_save_objects(work_objs)

        # 6️⃣ Projects
        project_objs = [
            Project(
                cv_versions_id=cv_versions_id,
                project_name=p.project_name,
                description=getattr(p, "description", None),
                dates=getattr(p, "dates", None),
                role=getattr(p, "role", None)
            )
            for p in cv_data.projects
        ]
        db.bulk_save_objects(project_objs)

        # 7️⃣ Volunteer Work
        volunteer_objs = [
            VolunteerWork(
                cv_versions_id=cv_versions_id,
                role=v.role,
                organization=getattr(v, "organization", None),
                dates=getattr(v, "dates", None),
                description=getattr(v, "description", None)
            )
            for v in cv_data.volunteer_work
        ]
        db.bulk_save_objects(volunteer_objs)

        # 8️⃣ Certifications
        cert_objs = [
            Certification(
                cv_versions_id=cv_versions_id,
                certification_name=c.certification_name,
                institution=c.institution,
                date_earned=getattr(c, "date_earned", None)
            )
            for c in getattr(cv_data, "certifications", [])
        ]
        db.bulk_save_objects(cert_objs)

        # 9️⃣ Awards and Honors
        award_objs = [
            AwardAndHonor(
                cv_versions_id=cv_versions_id,
                award_name=a.award_name,
                institution=getattr(a, "institution", None),
                date_awarded=getattr(a, "date_awarded", None)
            )
            for a in getattr(cv_data, "awards_and_honors", [])
        ]
        db.bulk_save_objects(award_objs)

        pi = getattr(cv_data, "personal_information", None)
        if pi:
            pi_obj = PersonalInformation(
                cv_versions_id=cv_versions_id,
                summary=getattr(pi, "summary", None),
                phone=getattr(pi, "phone", None),
                address=getattr(pi, "address", None),
                linkedin=getattr(pi, "linkedin", None)
            )
            db.add(pi_obj)

        cv_version = db.query(CVVersion).filter(CVVersion.id == cv_versions_id).first()
        cv_version.analysis_done = True
        db.commit()
        # Commit une seule fois pour tout
        db.commit()
        print(f"Toutes les données CV ont été insérées pour le candidat {cv_versions_id}")

    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'analyse du CV pour {cv_versions_id}: {e}")

    finally:
        db.close()

def matching_score(job_id: int, cv_versions_id: int, db: Session):
    try:
        # 🔎 Récupérer le job et la version CV
        job = db.query(JobPosition).filter(JobPosition.id == job_id).first()
        cv_version = db.query(CVVersion).filter(CVVersion.id == cv_versions_id).first()

        if not job or not cv_version:
            print(f"Job {job_id} ou CV {cv_versions_id} introuvable.")
            return

        # ⚡ Récupérer toutes les données CV du candidat (éducation, expériences, etc.)
        personal_info = db.query(PersonalInformation).filter_by(cv_versions_id=cv_versions_id).first()
        education_list = db.query(Education).filter_by(cv_versions_id=cv_versions_id).all()
        work_experience_list = db.query(WorkExperience).filter_by(cv_versions_id=cv_versions_id).all()
        certifications_list = db.query(Certification).filter_by(cv_versions_id=cv_versions_id).all()
        languages_list = db.query(Language).filter_by(cv_versions_id=cv_versions_id).all()
        projects_list = db.query(Project).filter_by(cv_versions_id=cv_versions_id).all()
        awards_list = db.query(AwardAndHonor).filter_by(cv_versions_id=cv_versions_id).all()
        volunteer_list = db.query(VolunteerWork).filter_by(cv_versions_id=cv_versions_id).all()
        strengths_list = db.query(CandidateStrength).filter_by(cv_versions_id=cv_versions_id).all()
        improvements_list = db.query(CandidateAreaForImprovement).filter_by(cv_versions_id=cv_versions_id).all()

        # 🔄 Convertir en texte structuré
        candidate_text = convert_candidate_data_to_text(
            personal_info,
            education_list,
            work_experience_list,
            certifications_list,
            languages_list,
            projects_list,
            awards_list,
            volunteer_list,
            strengths_list,
            improvements_list
        )

        result = evaluate_candidate(job.description, candidate_text)

        if result:
            # 💾 Sauvegarder le résultat en DB
            cv_candidate = db.query(CVCandidate).filter_by(cv_version_id=cv_versions_id).first()
            if cv_candidate:
                cv_candidate.match_score = result.match_score
                cv_candidate.skills_match = result.skills_match
                cv_candidate.experience_match = result.experience_match
                cv_candidate.cultural_fit_feedback = result.cultural_fit_feedback
                cv_candidate.overall_feedback = result.overall_feedback
                cv_candidate.strengths = result.strengths
                cv_candidate.weaknesses = result.weaknesses
                cv_candidate.recommendation = result.recommendation
                cv_candidate.decision_reasoning = result.decision_reasoning

                db.commit()
                print(f"✅ Score CV sauvegardé pour cv_version {cv_versions_id}")
            else:
                print(f"Aucun CVCandidate trouvé pour cv_version {cv_versions_id}")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur analyse score CV {cv_versions_id}: {e}")



def update_candidate_phase(
    db: Session,
    candidate_id: int,
    new_phase: CandidatePhase,
    phase_id: int
) -> JobCandidate | None:
    candidate = db.query(JobCandidate).filter(JobCandidate.id == candidate_id).first()
    if not candidate:
        return None  # pas de candidat trouvé

    new_job_phase = db.query(JobPhase).filter(
        JobPhase.id == phase_id,
        JobPhase.job_id == candidate.job_id,
        JobPhase.phase == new_phase
    ).first()

    if not new_job_phase:
        raise ValueError(f"Phase {new_phase} (id={phase_id}) introuvable pour ce job.")

    candidate.job_phase_id = new_job_phase.id

    # Génération d'un code unique si la phase est EVALUATION
    if new_phase == CandidatePhase.EVALUATION:
        candidate.evaluation_code = generate_unique_code()

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    db.refresh(candidate)
    return candidate

def get_job_candidates(db: Session, job_id: int) -> List[JobCandidate]:
    
    return db.query(JobCandidate).filter(JobCandidate.job_id == job_id).all()

def verify_candidate(db: Session, job_uuid: str, data: CandidateVerificationData) -> dict:
     # 1️⃣ On récupère le job avec l'UUID
    job = db.query(JobPosition).filter(JobPosition.uuid == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable.")

    # 2️⃣ On vérifie le candidat avec l'ID du job trouvé
    jobcandidate = (
     db.query(JobCandidate)
    .join(JobCandidate.candidate)  # relation vers le modèle Candidate
    .filter(Candidate.email == data.email)
    .filter(JobCandidate.job_id == job.id)
    .first()
)
    candidate = db.query(Candidate).filter(Candidate.email == data.email).first()
    if not jobcandidate:
        raise HTTPException(status_code=404, detail="Aucun candidat trouvé avec ces informations.")

    if jobcandidate.quiz_submitted:
        raise HTTPException(status_code=403, detail="Vous avez déjà passé ce quiz.")

    phase = db.query(JobPhase).filter(
        JobPhase.id == jobcandidate.job_phase_id,
        JobPhase.job_id == job.id,
        JobPhase.assessment_id.isnot(None)
    ).first()

    if not phase or not phase.assessment:
        raise HTTPException(status_code=404, detail="Aucun assessment lié à ce candidat/job.")

    if jobcandidate.job_phase_id != phase.id or phase.phase != "EVALUATION":
        raise HTTPException(
            status_code=403,
            detail="Le candidat n'est pas dans la phase d'évaluation."
        )
    #  Vérification du temps
    now = datetime.utcnow()+ timedelta(hours=1) 
    if phase.startDate and now < phase.startDate:
        raise HTTPException(status_code=403, detail="Le quiz n'a pas encore commencé.")
    if phase.endDate and now > phase.endDate:
        raise HTTPException(status_code=403, detail="Le quiz est terminé.")

    return {
        "candidateId": jobcandidate.id,
        "candidateUuid": candidate.uuid,
        "phaseId": phase.id,
        "assessmentId": phase.assessment_id,
        "phase": phase.phase,
        "now": now  ,
        "startDate" : phase.startDate,
        "endDate": phase.endDate
    }

def start_quiz(candidate_uuid: str, job_uuid: str, db: Session) -> dict:
    job = db.query(JobPosition).filter(JobPosition.uuid == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable.")
    candidate = db.query(Candidate).filter(Candidate.uuid == candidate_uuid).first()
    jobcandidate = db.query(JobCandidate).filter(
        JobCandidate.candidate_id == candidate.id,
        JobCandidate.job_id == job.id
    ).first()
    if not jobcandidate:
        raise HTTPException(status_code=404, detail="Candidat non trouvé")

    if jobcandidate.quiz_submitted:
        raise HTTPException(status_code=403, detail="Quiz déjà soumis ")

    phase = db.query(JobPhase).filter(JobPhase.id == jobcandidate.job_phase_id).first()
    if not phase or not phase.assessment:
        raise HTTPException(status_code=404, detail="Phase ou assessment introuvable")

    assessment = phase.assessment 
    print(" l'assessment:",assessment.id)
    duration = getattr(assessment, "duration", 90)  # durée du quiz en minutes
    extra_time = 5  # minutes supplémentaires pour le token après expiration du quiz

    now = datetime.utcnow() + timedelta(hours=1)

    if not jobcandidate.quiz_started_at:
        # Première entrée -> on démarre la session
        jobcandidate.quiz_started_at = now
        db.commit()

    # Recalcul des expirations
    expires_at = jobcandidate.quiz_started_at + timedelta(minutes=duration)
    token_expiration = expires_at + timedelta(minutes=extra_time)

    # Vérifier si le temps est écoulé
    if now > expires_at:
        raise HTTPException(status_code=403, detail="Session expirée.")

    payload = {
        "jobcandidateId": jobcandidate.id,
        "assessmentId": assessment.id,
        "candidateId": candidate.id,
        "jobId": job.id,
        "iat": jobcandidate.quiz_started_at.timestamp(),
        "exp": token_expiration.timestamp(),
    }
    quiz_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "quiz_token": quiz_token,
        "expiresAt": int(expires_at.timestamp() * 1000),
        "candidateSession": {
            "jobcandidateId":jobcandidate.id,
            "candidateId": candidate.id,
            "candidateUuid": candidate_uuid,
            "first_name": candidate.first_name,
            "last_name": candidate.last_name,
            "assessmentId": phase.assessment_id,
            "assessmentUuid": assessment.uuid, 
            "phase": phase.phase,
            "quiz_submitted": jobcandidate.quiz_submitted  
        }
    }

def validate_quiz_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token invalide")

    candidate_id = payload["candidateId"]
    candidate = db.query(JobCandidate).filter(JobCandidate.id == candidate_id).first()

    if not candidate or candidate.quiz_submitted:
        raise HTTPException(status_code=403, detail="Quiz déjà soumis ou candidat introuvable")
    
    #  Marquer le token comme utilisé si besoin
    if payload.get("used", False):
        raise HTTPException(status_code=403, detail="Token déjà utilisé")
    
    return candidate, payload
def delete_candidate(db: Session, candidate_id: int) -> bool:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        return False
    db.delete(candidate)
    db.commit()
    return True

# ---- CandidateStrength CRUD ----
def create_candidate_strength(db: Session, strength: CandidateStrengthCreate) -> CandidateStrength:
    new_strength = CandidateStrength(**strength.dict())
    db.add(new_strength)
    db.commit()
    db.refresh(new_strength)
    return new_strength

def get_candidate_strengths(db: Session, candidate_match_id: int) -> List[CandidateStrength]:
    return db.query(CandidateStrength).filter(CandidateStrength.candidate_match_id == candidate_match_id).all()

def delete_candidate_strength(db: Session, strength_id: int) -> bool:
    strength = db.query(CandidateStrength).filter(CandidateStrength.id == strength_id).first()
    if not strength:
        return False
    db.delete(strength)
    db.commit()
    return True

# ---- CandidateAreaForImprovement CRUD ----
def create_candidate_area_for_improvement(db: Session, area: CandidateAreaForImprovementCreate) -> CandidateAreaForImprovement:
    new_area = CandidateAreaForImprovement(**area.dict())
    db.add(new_area)
    db.commit()
    db.refresh(new_area)
    return new_area

def get_candidate_areas_for_improvement(db: Session, candidate_match_id: int) -> List[CandidateAreaForImprovement]:
    return db.query(CandidateAreaForImprovement).filter(CandidateAreaForImprovement.candidate_match_id == candidate_match_id).all()

def delete_candidate_area_for_improvement(db: Session, area_id: int) -> bool:
    area = db.query(CandidateAreaForImprovement).filter(CandidateAreaForImprovement.id == area_id).first()
    if not area:
        return False
    db.delete(area)
    db.commit()
    return True

def delete_candidate_area_for_improvement(db: Session, area_id: int) -> bool:
    area = db.query(CandidateAreaForImprovement).filter(CandidateAreaForImprovement.id == area_id).first()
    if not area:
        return False
    db.delete(area)
    db.commit()
    return True
