from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import datetime, timezone,timedelta
from typing import List, Dict

from .models import Result
from ..assessment.models import Assessment
from ..questions.models import Question
from .schemas import ResultCreate, ResultResponse
from src.internal.job_positions.models import JobCandidate
from sqlalchemy.orm import joinedload
from ..test.models import Test

def create_result(db: Session, result_data: ResultCreate) -> ResultResponse:
    # 1 Récupérer l'assessment
    assessment = (
        db.query(Assessment)
        .options(joinedload(Assessment.tests).joinedload(Test.questions).joinedload(Question.responses))
        .filter(Assessment.id == result_data.assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    question_map = {
        question.id: question
        for test in assessment.tests
        for question in test.questions
    }

    # 2 Calculer le score
    total_points = 0
    obtained_points = 0

    for resp in result_data.responses:
        q_id = resp.question_id
        selected_ids = resp.selected_response_ids

        question = question_map.get(q_id)
        if not question:
            raise HTTPException(status_code=400, detail=f"Question id {q_id} invalide pour cet assessment")

        total_points += question.nbPoints
        correct_ids = [r.id for r in question.responses if r.is_correct]
        if set(selected_ids) == set(correct_ids):
            obtained_points += question.nbPoints

    score = round((obtained_points / total_points) * 100, 2) if total_points > 0 else 0
    candidate = db.query(JobCandidate).filter(JobCandidate.id == result_data.jobcandidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    # 3 Enregistrer le résultat
    now = datetime.now(timezone.utc)+ timedelta(hours=1)
    result = Result(
        score=score,
        responses=[r.dict() for r in result_data.responses],
        jobcandidate_id=result_data.jobcandidate_id,
        assessment_id=result_data.assessment_id,
        date=now,
        createdAt=now,
        updatedAt=now,
    )
    db.add(result)

    # 4 Mettre à jour le candidat : marque quiz soumis
    if candidate:
        candidate.quiz_submitted = True
        candidate.quiz_expires_at = now

    db.commit()
    db.refresh(result)
    return ResultResponse.model_validate(result)

def get_result_by_id(db: Session, result_id: int) -> ResultResponse:
    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return ResultResponse.model_validate(result)

def get_results_by_user(db: Session, candidate_id: int) -> List[ResultResponse]:
    results = db.query(Result).filter(Result.candidate_id == candidate_id).all()
    return [ResultResponse.model_validate(r) for r in results]

def delete_result(db: Session, result_id: int) -> bool:
    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    db.delete(result)
    db.commit()
    return True
