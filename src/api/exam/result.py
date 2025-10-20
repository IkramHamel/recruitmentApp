from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime
from src.internal.job_positions.models import JobCandidate
from src.internal.exam.results.schemas import ResultCreate, ResultResponse
from src.internal.exam.results import create_result, get_result_by_id, get_results_by_user
from src.api.endpoint import BaseEndpoint
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from src.db.session import get_db
from src.internal.exam.assessment.models import Assessment
from src.internal.exam.test.models import Test
from src.internal.exam.questions.models import Question
from src.internal.exam.results.models import Result
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
class ResultsEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_router(self) -> APIRouter:

        router = APIRouter(prefix="/results")
        @router.get("/results/{candidate_id}/{job_id}")
        def get_results_by_candidate_and_job(candidate_id: int, job_id: int, db: Session = Depends(get_db)):
    # 1️⃣ Récupérer le JobCandidate avec ses résultats
            jobcandidate = (
        db.query(JobCandidate)
        .options(joinedload(JobCandidate.results))
        .filter(JobCandidate.id == candidate_id, JobCandidate.job_id == job_id)
        .first()
    )

            if not jobcandidate:
                raise HTTPException(status_code=404, detail="Candidate not found for this job")

            enriched_results = []

    # 2️⃣ Parcourir les résultats liés à ce job_candidate
            for result in jobcandidate.results:
        # Récupérer l'assessment associé
                assessment = (
            db.query(Assessment)
            .options(
                joinedload(Assessment.tests)
                .joinedload(Test.questions)
                .joinedload(Question.responses)
            )
            .filter(Assessment.id == result.assessment_id)
            .first()
        )

                if not assessment:
                    continue

        # 3️⃣ Construire la map question_id → question
                question_map = {q.id: q for test in assessment.tests for q in test.questions}

        # 4️⃣ Enrichir les réponses avec les textes choisis
                enriched_responses = []
                for resp in result.responses:
                    question = question_map.get(resp["question_id"])
                    if not question:
                        continue

                    selected_texts = [
                r.content for r in question.responses if r.id in resp["selected_response_ids"]
            ]

                    enriched_responses.append({
                "question_text": question.label,
                "selected_responses": selected_texts
            })

        # 5️⃣ Ajouter le résultat enrichi à la liste
                enriched_results.append({
            "assessment_id": assessment.id,
            "assessment_title": assessment.title,
            "score": result.score,
            "date": result.date,
            "responses": enriched_responses
        })

    # 6️⃣ Retourner la réponse finale (hors de la boucle)
            return {
        "candidate_id": jobcandidate.candidate.id,
        "first_name": jobcandidate.candidate.first_name,
        "last_name": jobcandidate.candidate.last_name,
        "results_by_assessment": enriched_results
    }

        @router.post("/", response_model=ResultResponse)
        def create_result_endpoint(
        result_data: ResultCreate,
        db: Session = Depends(self.db_session),
        token: str = Depends(oauth2_scheme)
        ):
            try:
                decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=403, detail="Token invalide")

    # 2️⃣ Vérifier manuellement l'expiration
            exp_timestamp = decoded.get("exp")
            if exp_timestamp is None:
                raise HTTPException(status_code=403, detail="Token invalide : pas de date d'expiration")
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise HTTPException(status_code=403, detail="Session expirée")

    # 3️⃣ Récupérer les IDs depuis le token
            jobcandidate_id_from_token = decoded.get("jobcandidateId")
            candidate_id_from_token = decoded.get("candidateId")
            assessment_id_from_token = decoded.get("assessmentId")
            job_id_from_token = decoded.get("jobId")

    # 4️⃣ Vérifier que le jobcandidate existe et correspond
            jobcandidate = db.query(JobCandidate).filter(JobCandidate.id == jobcandidate_id_from_token).first()
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id_from_token).first()
            if not jobcandidate:
                raise HTTPException(status_code=403, detail="Token invalide")
            if jobcandidate.candidate_id != candidate_id_from_token:
                raise HTTPException(status_code=403, detail="Token ne correspond pas au candidat")
            if assessment.id != assessment_id_from_token:
                raise HTTPException(status_code=403, detail="Token ne correspond pas à l'évaluation")
            if jobcandidate.job_id != job_id_from_token:
                raise HTTPException(status_code=403, detail="Token ne correspond pas au job")

    # 5️⃣ Vérifier que le quiz n'a pas déjà été soumis
            if jobcandidate.quiz_submitted:
                raise HTTPException(status_code=403, detail="Quiz déjà soumis")

    # 6️⃣ Créer le résultat
            created_result = create_result(db, result_data)

    # 7️⃣ Marquer le quiz comme soumis pour ce jobcandidate spécifique
            jobcandidate.quiz_submitted = True
            db.commit()

            return created_result


        @router.get("/{result_id}", response_model=ResultResponse)
        def get_result_endpoint(result_id: int, db: Session = Depends(self.db_session)):
            result = get_result_by_id(db, result_id)
            if not result:
                raise HTTPException(status_code=404, detail="Result not found")
            return result

        @router.get("/user/{candidate_id}", response_model=List[ResultResponse])
        def get_results_by_user_endpoint(user_id: int, db: Session = Depends(self.db_session)):
            results = get_results_by_user(db, user_id)
            return results

        return router
    
    
