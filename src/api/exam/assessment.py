from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.exam.questions.schemas import QuestionResponse,QuestionResponseExam
from src.internal.exam.assessment.schemas import AssessmentCreate,AssessmentResponse,AssessmentUpdate ,AssessmentResponseExam
from src.internal.exam.assessment import create_assessment,delete_assessment,get_assessment_by_id,get_assessments,update_assessment,get_questions_by_assessment,get_assessment_by_idExam
from src.core.logging import logger  
from typing import List
from src.api.endpoint import BaseEndpoint
from src.internal.iam.users.models import User
from src.internal.exam.assessment.permissions import PERMISSIONS_ASSESSMENT
from src.api.middlewares.authz import has_permission
"""
dependencies=[Depends(requiresAuth)]
current_user: User = Depends(require_roles("ADMINISTRATOR"))
current_user: User = Depends(require_roles("ADMINISTRATOR"))
"""
class AssessmentsEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger  # You can use standard logging or a custom logger

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/assessments")

        @router.post("/", response_model=AssessmentResponse)
        def create_assessment_endpoint(assessment_data: AssessmentCreate, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_ASSESSMENT["Assessment Management"]["permissions"][0]["name"]))
):
            created_assessment = create_assessment(db, assessment_data)
            return created_assessment
        
        
        @router.get("/", response_model=List[AssessmentResponse])
        def get_assessments_endpoint(db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_ASSESSMENT["Assessment Management"]["permissions"][1]["name"]))
):
            assessments = get_assessments(db)
            return assessments

        @router.get("/{assessment_id}", response_model=AssessmentResponse)
        def get_assessment_endpoint(assessment_id: int, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_ASSESSMENT["Assessment Management"]["permissions"][4]["name"]))
):
            assessment = get_assessment_by_id(db, assessment_id)
            return assessment
        
        @router.get("/exam/{assessment_id}", response_model=AssessmentResponseExam)
        def get_assessment_endpoint_exam(assessment_id: int, db: Session = Depends(self.db_session)):
            assessment = get_assessment_by_idExam(db, assessment_id)
            return assessment
        @router.get("/uuid/{asszssment_uuid}", response_model=AssessmentResponse)
        def get_assessment_uuid(assessment_uuid: str, db: Session = Depends(self.db_session)):
            assessment = get_assessment_uuid(db, assessment_uuid)
            if not assessment:
                raise HTTPException(status_code=404, detail="candidate not found")
            return assessment
        @router.get("/getQuestions/{assessment_id}", response_model=List[QuestionResponseExam])
        def get_questions_endpoint(assessment_id: int, db: Session = Depends(self.db_session)):
            questions = get_questions_by_assessment(db, assessment_id)
            return questions
        
        @router.put("/{assessment_id}", response_model=AssessmentResponse)
        def update_assessment_endpoint(assessment_id: int, assessment_update: AssessmentUpdate, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_ASSESSMENT["Assessment Management"]["permissions"][2]["name"]))
):
            updated_assessment = update_assessment(db, assessment_id, assessment_update)
            return updated_assessment
        
        @router.delete("/{assessment_id}")
        def delete_assessment_endpoint(assessment_id: int, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_ASSESSMENT["Assessment Management"]["permissions"][0]["name"]))
):
            success = delete_assessment(db, assessment_id)
            if not success:
              raise HTTPException(status_code=404, detail="Assessment not found")
            return {"message": "Assessment deleted successfully"}

        
    
        return router
