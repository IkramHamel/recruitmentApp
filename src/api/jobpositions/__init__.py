from fastapi import APIRouter, Depends, HTTPException,Body,Query
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime
from ...internal.job_positions.schemas import (
    JobPositionCreate, JobPositionResponse,JobDescriptionRequest,
    JobKeywordCreate, JobKeywordOut,CandidateResponse,
    JobPhaseCreate, JobCandidateResponse,CVVersionOut,
    JobPhaseOut,CandidateVerificationData,CandidatePhaseUpdate,CandidateAreaForImprovementOut,CandidateStrengthCreate,CandidateAreaForImprovementCreate
)
from fastapi import APIRouter, Depends, Form, File, UploadFile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ...internal.job_positions import (
    analyze_cv_background,get_cv_by_job_candidate,delete_jobcandidate,matching_score,
    create_job_position,get_all_jobcandidates, get_all_job_positions, get_job_position, update_job_position, delete_job_position,
    create_job_keyword, get_job_keywords, delete_job_keyword,update_phase,get_all_keywords,get_jobcandidate_by_id,
    create_job_candidate, get_job_candidates, delete_candidate,update_job_position_posted,start_quiz,
     verify_candidate,get_job_position_uuid,validate_quiz_token,update_candidate_phase,get_candidate_by_id,get_candidates,
    delete_candidate_area_for_improvement,get_candidate_strengths,create_candidate_strength,delete_candidate_strength,create_candidate_area_for_improvement,get_candidate_areas_for_improvement
)
from ...internal.IA.generate_description import generate_job_description
from ...internal.job_positions.models import CandidatePhase,JobCandidate
from src.db.session import get_db
from src.api.middlewares.authz import get_current_user
from src.internal.iam.users.models import User
from src.core.logging import logger
from pydantic import BaseModel
from src.internal.iam.users.models import User
from src.internal.job_positions.permissions import PERMISSIONS_JOBS,PERMISSIONS_CANDIDATES
from src.api.middlewares.authz import has_permission
from src.internal.IA.search import get_talent_recommendations,CandidateResult

class JobEndpoints:
 

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_routers(self) -> List[APIRouter]:
        router = APIRouter()



        @router.get("/search", response_model=List[CandidateResult])
        def search_talents(query: str = Query(..., description="Requête de recherche de talent")):
            results = get_talent_recommendations(query, top_k=10)
            return results

        @router.post("/ia/generate_description")
        def generate_description_endpoint(request: JobDescriptionRequest):  
            try:
                result = generate_job_description(request.model_dump())
                return {"description": result.content}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        

        @router.get("/candidates", response_model=List[CandidateResponse])
        def read_candidates(db: Session = Depends(self.db_session)):
            return get_candidates(db)

        @router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
        def get_candidate(candidate_id: int, db: Session = Depends(self.db_session)):
            candidate = get_candidate_by_id(db, candidate_id)
            if not candidate:
                raise HTTPException(status_code=404, detail="candidate not found")
            return candidate
        
        @router.delete("/candidates/{candidate_id}", response_model=dict)
        def remove_candidate(candidate_id: int, db: Session = Depends(self.db_session)):
            if not delete_candidate(db, candidate_id):
                raise HTTPException(status_code=404, detail="Candidate not found")
            return {"message": "Candidate deleted successfully"}
        @router.put("/phases/{phase_id}",response_model=JobPhaseOut)
        def update_phases(phase_id: int, phase_data: JobPhaseCreate, db: Session = Depends(get_db)):
            return update_phase(db, phase_id, phase_data)
        # --- JobPosition Routes ---
        @router.post("/", response_model=JobPositionResponse)
        def create_job(job: JobPositionCreate, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_JOBS["Job Management"]["permissions"][0]["name"]))):
            return create_job_position(db, job)


        @router.get("/", response_model=List[JobPositionResponse])
        def list_jobs(db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_JOBS["Job Management"]["permissions"][1]["name"]))):
            return get_all_job_positions(db)
        @router.get("/jobsclient", response_model=List[JobPositionResponse])
        def list_jobs(db: Session = Depends(self.db_session)):
            return get_all_job_positions(db)

        @router.get("/{job_id}", response_model=JobPositionResponse)
        def get_job(job_id: int, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_JOBS["Job Management"]["permissions"][4]["name"]))):
            job = get_job_position(db, job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            return job
        @router.get("/uuid/{job_uuid}", response_model=JobPositionResponse)
        def get_job_uuid(job_uuid: str, db: Session = Depends(self.db_session)):
            job = get_job_position_uuid(db, job_uuid)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            return job
 
        @router.put("/{job_id}", response_model=JobPositionResponse)
        def update_job(job_id: int, job_data: JobPositionCreate, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_JOBS["Job Management"]["permissions"][2]["name"]))):
            updated = update_job_position(db, job_id, job_data)
            if not updated:
                raise HTTPException(status_code=404, detail="Job not found")
            return updated

        @router.patch("/posted/{job_id}", response_model=JobPositionResponse)
        def update_job_posted(job_id: int, db: Session = Depends(self.db_session)):
            updated = update_job_position_posted(db, job_id)
            if not updated:
                raise HTTPException(status_code=404, detail="Job not found")
            return updated
        @router.delete("/{job_id}", response_model=dict)
        def delete_job(job_id: int, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_JOBS["Job Management"]["permissions"][3]["name"]))):
            success = delete_job_position(db, job_id)
            if not success:
                raise HTTPException(status_code=404, detail="Job not found")
            return {"message": "Job deleted successfully"}

        # --- JobKeyword Routes ---
        @router.post("/keywords", response_model=JobKeywordOut)
        def add_keyword(keyword: JobKeywordCreate, db: Session = Depends(self.db_session)):
            return create_job_keyword(db, keyword)

        @router.get("/{job_id}/keywords", response_model=List[JobKeywordOut])
        def list_keywords(job_id: int, db: Session = Depends(self.db_session)):
            return get_job_keywords(db, job_id)
        
        @router.get("/uuid/{candidate_uuid}", response_model=JobCandidateResponse)
        def get_candidate_uuid(candidate_uuid: str, db: Session = Depends(self.db_session)):
            candidate = get_candidate_uuid(db, candidate_uuid)
            if not candidate:
                raise HTTPException(status_code=404, detail="candidate not found")
            return candidate
        @router.get("/jobcandidate/{candidate_id}", response_model=JobCandidateResponse)
        def get_jobcandidate_id(candidate_id: int, db: Session = Depends(self.db_session)):
            candidate = get_jobcandidate_by_id(db, candidate_id)
            if not candidate:
                raise HTTPException(status_code=404, detail="candidate not found")
            return candidate
        
        @router.get("/keywords", response_model=List[JobKeywordOut])
        def list_keywords_all(db: Session = Depends(self.db_session)):
            return get_all_keywords(db)

        @router.delete("/keywords/{keyword_id}", response_model=dict)
        def remove_keyword(keyword_id: int, db: Session = Depends(self.db_session)):
            if not delete_job_keyword(db, keyword_id):
                raise HTTPException(status_code=404, detail="Keyword not found")
            return {"message": "Keyword deleted successfully"}

        # --- JobCandidate Routes ---
        @router.get("/jobcandidate/list", response_model=List[JobCandidateResponse])
        def list_jobcandidates(db: Session = Depends(self.db_session)):
            return get_all_jobcandidates(db)
        @router.delete("/jobcandidates/{jobcandidate_id}", response_model=dict)
        def remove_jobcandidate(jobcandidate_id: int, db: Session = Depends(self.db_session)):
            if not delete_jobcandidate(db, jobcandidate_id):
                raise HTTPException(status_code=404, detail="job Candidate not found")
            return {"message": "job Candidate deleted successfully"}
        
        from fastapi import BackgroundTasks

        @router.get("/getCvByJobCandidate/{job_candidate_id}/{candidate_id}", response_model=CVVersionOut)
        def get_cv_by_job_candidate_endpoint(
        job_candidate_id: int,
        candidate_id: int,
        db: Session = Depends(get_db)):
            cv = get_cv_by_job_candidate(db, job_candidate_id, candidate_id)
            if not cv:
                raise HTTPException(status_code=404, detail="CV not found")
            return cv
        
        @router.post("/jobcandidate", response_model=JobCandidateResponse)
        def add_jobcandidate(
            background_tasks: BackgroundTasks,
            db: Session = Depends(get_db),
            job_id: int = Form(...),
            first_name: str = Form(...),
            last_name: str = Form(...),
            SponsorName: str = Form(...),
            email: str = Form(...),
            phone_number: str = Form(...),
            file: UploadFile = File(...),
            
):
    # 1️⃣ Créer le candidat et JobCandidate
            new_job_candidate, cv_version, temp_file_path =create_job_candidate(
            job_id=job_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        file=file,
        SponsorName=SponsorName,
        db=db
    )
            print("koj job id:", job_id)
    # 2️⃣ Lancer l'analyse CV en tâche de fond
            if not cv_version.analysis_done:
                background_tasks.add_task(
        analyze_cv_background,
        file_path=temp_file_path,
        cv_versions_id=cv_version.id,
        candidate_id=new_job_candidate.candidate_id,
        db=db
    )
            else:
                print(f"✅ CV version {cv_version.id} déjà analysée")

            background_tasks.add_task(matching_score, job_id=job_id, cv_versions_id=cv_version.id, db=db)

            return new_job_candidate

        @router.patch("/candidates/phase/{candidateId}/{phaseId}", response_model=JobCandidateResponse)
        def update_candidate_phase_route(candidateId: int,phase: CandidatePhase,phaseId:int ,db: Session = Depends(get_db)):
            updated_candidate = update_candidate_phase(db, candidateId, phase,phaseId)

            if not updated_candidate:
                raise HTTPException(status_code=404, detail="Candidat non trouvé")

            return updated_candidate
        """@router.get("/jobcandidates/{candidate_id}", response_model=JobCandidateResponse)
        def read_jobcandidate(candidate_id: int, db: Session = Depends(get_db)):
            return get_jobcandidate_by_id(db, candidate_id)"""
        
        @router.post("/candidates/verify_candidate/{job_uuid}")
        def verify_candidate_endpoint(job_uuid: str, data: CandidateVerificationData, db: Session = Depends(get_db)):
            return verify_candidate(db, job_uuid, data)
        
        @router.get("/candidates/start_quiz/{candidate_uuid}/{job_uuid}")
        def startQuizz(candidate_uuid:str,job_uuid: str, db: Session = Depends(get_db)):
            return start_quiz (candidate_uuid, job_uuid, db)


        
        @router.get("/{job_id}/candidates", response_model=List[JobCandidateResponse])
        def list_candidates(job_id: int, db: Session = Depends(self.db_session)):
            return get_job_candidates(db, job_id)


      # --- CandidateStrength Routes ---
        @router.post("/candidates/strengths", response_model=CandidateAreaForImprovementOut)
        def add_strength(strength: CandidateStrengthCreate, db: Session = Depends(self.db_session)):
            return create_candidate_strength(db, strength)

        @router.get("/candidates/{candidate_id}/strengths", response_model=List[CandidateAreaForImprovementOut])
        def list_strengths(candidate_id: int, db: Session = Depends(self.db_session)):
            return get_candidate_strengths(db, candidate_id)

        @router.delete("/candidates/strengths/{strength_id}", response_model=dict)
        def remove_strength(strength_id: int, db: Session = Depends(self.db_session)):
            if not delete_candidate_strength(db, strength_id):
                raise HTTPException(status_code=404, detail="Strength not found")
            return {"message": "Strength deleted successfully"}

        # --- CandidateAreaForImprovement Routes ---
        @router.post("/candidates/improvements", response_model=CandidateAreaForImprovementOut)
        def add_improvement(area: CandidateAreaForImprovementCreate, db: Session = Depends(self.db_session)):
            return create_candidate_area_for_improvement(db, area)

        

        @router.get("/candidates/{candidate_id}/improvements", response_model=List[CandidateAreaForImprovementOut])
        def list_improvements(candidate_id: int, db: Session = Depends(self.db_session)):
            return get_candidate_areas_for_improvement(db, candidate_id)

        @router.delete("/candidates/improvements/{area_id}", response_model=dict)
        def remove_improvement(area_id: int, db: Session = Depends(self.db_session)):
            if not delete_candidate_area_for_improvement(db, area_id):
                raise HTTPException(status_code=404, detail="Improvement not found")
            return {"message": "Improvement deleted successfully"}
        

        @router.post("/send-email")
        def send_email(
        candidate_email: str = Body(...),
        exam_url: str = Body(...),
        candidate_name: str = Body(...),
        evaluation_code: str = Body(...),
        startDate :str = Body(...),
        endDate : str = Body(...)

        ):
            
            try:
                subject = "Invitation à l'évaluation"

                message = f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.5; margin: 0; padding: 0;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
      <tr>
        <td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <tr>
              <td style="background-color: #003366; color: #ffffff; text-align: center; padding: 20px;">
                <h1 style="margin: 0; font-size: 24px;">3S RH</h1>
              </td>
            </tr>
            <tr>
             <td style="padding: 30px;">
  <h2 style="color: #003366;">Bonjour {candidate_name},</h2>

  <p>Nous avons le plaisir de vous inviter à passer une évaluation pour le poste auquel vous avez postulé.</p>

  <p style="text-align: center; margin: 30px 0;">
    L’évaluation se déroulera du <strong>{startDate}</strong> au <strong> {endDate }</strong>.<br><br>
    <a href="{exam_url}" style="background-color: #003366; color: #ffffff; text-decoration: none; padding: 12px 25px; border-radius: 5px; font-weight: bold;">
      Passer l’évaluation
    </a>
  </p>

  <p>
    Accédez à votre espace avec votre adresse e-mail et le code suivant : 
    <b>{evaluation_code}</b>.<br>
    Nous vous souhaitons bonne chance et restons à votre disposition pour toute question.
  </p>

  <p>Cordialement,<br><b>L’équipe 3S RH</b></p>
</td>

            </tr>
            <tr>
              <td style="background-color: #f4f4f4; text-align: center; padding: 15px; font-size: 12px; color: #777777;">
                &copy; 2025 3S RH. Tous droits réservés.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

                msg = MIMEMultipart()
                msg["From"] = os.getenv("SENDER_EMAIL")
                msg["To"] = candidate_email
                msg["Subject"] = subject
                msg.attach(MIMEText(message, "html"))

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))
                server.sendmail(os.getenv("SENDER_EMAIL"), candidate_email, msg.as_string())
                server.quit()

                return {"status": "success", "message": "Email envoyé avec succès ✅"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
            


        


        return [router]
