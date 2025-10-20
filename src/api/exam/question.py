from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.exam.questions.schemas import QuestionCreate, QuestionUpdate, QuestionResponse
from src.internal.exam.questions import (
    create_question,
    get_questions,
    get_question_by_id,
    update_question,
    delete_question
)
from typing import List
from src.api.endpoint import BaseEndpoint
from src.core.logging import logger
from fastapi import File, UploadFile, HTTPException
from cloudinary.uploader import upload
from io import BytesIO
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends
from src.internal.iam.users.models import User
from src.internal.exam.questions.permissions import PERMISSIONS_QUESTIONS
from src.api.middlewares.authz import has_permission
class QuestionsEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/questions")

        @router.post("/", response_model=QuestionResponse)
        async def create_question_endpoint(
        label: str = Form(...),
        question_type: str = Form(...),
        nbPoints: int = Form(...),
        responses: str = Form(...),
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(self.db_session),
        currentUser: User = Depends(has_permission(PERMISSIONS_QUESTIONS["Question Management"]["permissions"][0]["name"]))

    ):
    # tu appelles ta fonction métier (create_question) avec ces params
            question = await create_question(label,question_type, nbPoints,responses, image, db)
            return question

        @router.get("/", response_model=List[QuestionResponse])
        def get_all_questions_endpoint(db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_QUESTIONS["Question Management"]["permissions"][1]["name"]))
):
            return get_questions(db)

        @router.get("/{question_id}", response_model=QuestionResponse)
        def get_question_endpoint(question_id: int, db: Session = Depends(self.db_session)):
            question = get_question_by_id(db, question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")
            return question

        @router.put("/{question_id}", response_model=QuestionResponse)
        def update_question_endpoint(question_id: int, question_update: QuestionUpdate, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_QUESTIONS["Question Management"]["permissions"][2]["name"]))):
            return update_question(db, question_id, question_update)

        @router.delete("/{question_id}")
        def delete_question_endpoint(question_id: int, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_QUESTIONS["Question Management"]["permissions"][3]["name"]))):
            success = delete_question(db, question_id)
            if not success:
                raise HTTPException(status_code=404, detail="Question not found")
            return {"message": "Question deleted successfully"}

        return router
