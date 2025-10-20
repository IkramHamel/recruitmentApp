from sqlalchemy.orm import Session,joinedload
from .models import Assessment
from ..test.models import Test
from ...anti_cheat.models import AntiCheatRule
from .schemas import AssessmentCreate, AssessmentResponse, AssessmentUpdate,AssessmentResponseExam
from ..questions.schemas import QuestionResponse,QuestionResponseExam
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import List

def create_assessment(db: Session, assessment_data: AssessmentCreate) -> AssessmentResponse:
    # On récupère les tests à inclure
    #tests = db.query(Test).filter(Test.id.in_(assessment_data.tests)).all()

    # Vérifier la validité des tests
    #if not tests or len(tests) != len(assessment_data.tests):
        #raise HTTPException(status_code=400, detail="Un ou plusieurs tests sont invalides")

    assessment = Assessment(
        title=assessment_data.title,
        description=assessment_data.description,
        duration=assessment_data.duration,
        rules_id=assessment_data.rules_id,
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return AssessmentResponse.model_validate(assessment)

def get_assessments(db: Session) -> List[AssessmentResponse]:
    assessments = db.query(Assessment).all()
    return [AssessmentResponse.model_validate(a) for a in assessments]

def get_assessment_by_id(db: Session, assessment_id: int) -> AssessmentResponse:
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return AssessmentResponse.model_validate(assessment)

def get_assessment_by_idExam(db: Session, assessment_id: int) -> AssessmentResponseExam:
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return AssessmentResponse.model_validate(assessment)

def get_assessment_uuid(db: Session, assessment_uuid: str) -> Assessment:
    return db.query(Assessment).filter(Assessment.uuid == assessment_uuid).first()
def get_questions_by_assessment(db: Session, assessment_id: int) -> List[QuestionResponseExam]:
    assessment = (
        db.query(Assessment)
        .options(
            joinedload(Assessment.tests).joinedload(Test.questions)
        )
        .filter(Assessment.id == assessment_id)
        .first()
    )

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Utilisation d'un set pour éviter les doublons (cas où une question est dans plusieurs tests)
    unique_questions = {question for test in assessment.tests for question in test.questions}

    return [QuestionResponse.model_validate(q) for q in unique_questions]

def update_assessment(db: Session, assessment_id: int, update_data: AssessmentUpdate) -> AssessmentResponse:
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment.title = update_data.title
    assessment.description = update_data.description
    assessment.duration = update_data.duration
    assessment.rules_id = update_data.rules_id
    assessment.updatedAt = datetime.now(timezone.utc)

    if update_data.test_ids is not None:
        tests = db.query(Test).filter(Test.id.in_(update_data.test_ids)).all()
        assessment.tests = tests
   



    db.commit()
    db.refresh(assessment)
    return AssessmentResponse.model_validate(assessment)

def delete_assessment(db: Session, assessment_id: int) -> bool:
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    db.delete(assessment)
    db.commit()
    return True
