from sqlalchemy.orm import Session
from .models import Question
from ..responses.models import Response
from fastapi import APIRouter, UploadFile, File, Form, Depends
from .schemas import QuestionCreate, QuestionUpdate, QuestionResponse
from datetime import datetime, timezone
from typing import List
from typing import Optional

from src.db.session import get_db
from fastapi import File, UploadFile, HTTPException
import json
from ....core.cloudinary_config import *  
from cloudinary.uploader import upload
import os

async def create_question(
    label: str = Form(...),
    question_type: str = Form(...),
    nbPoints: int = Form(...),
    responses: str = Form(...),  
    image: Optional[UploadFile] = File(None),  # Image optionnelle
    db: Session = Depends(get_db)
):
    image_url = None  

    if image:
        try:
            result = upload(
                image.file,
                resource_type="image",
                public_id=image.filename,
                folder="Questions_Images"
            )
            image_url = result.get("secure_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur Cloudinary: {str(e)}")

    # Création de la question
    question = Question(
        label=label,
        question_type=question_type,
        nbPoints=nbPoints,
        image=image_url,  
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    # Traitement des réponses JSON
    try:
        parsed_responses = json.loads(responses)
        if not isinstance(parsed_responses, list):
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=400, detail="Format JSON invalide pour 'responses'.")

    for response_data in parsed_responses:
        if isinstance(response_data, str):
            try:
                response_data = json.loads(response_data)
            except Exception:
                raise HTTPException(status_code=400, detail="Élément invalide dans 'responses'.")

        response = Response(
            content=response_data["content"],
            is_correct=response_data["is_correct"],
            question_id=question.id,
            createdAt=datetime.now(timezone.utc),
            updatedAt=datetime.now(timezone.utc),
        )
        db.add(response)

    db.commit()

    return question

def get_questions(db: Session) -> List[QuestionResponse]:
    questions = db.query(Question).all()
    return [QuestionResponse.model_validate(q) for q in questions]

def get_question_by_id(db: Session, question_id: int) -> QuestionResponse:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    return QuestionResponse.model_validate(question)

async def update_question(
    question_id: int,
    label: str = Form(...),
    question_type: str = Form(...),
    nbPoints: int = Form(...),
    responses: str = Form(...),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question non trouvée")

    question.label = label
    question.question_type = question_type
    question.nbPoints = nbPoints
    question.updatedAt = datetime.now(timezone.utc)

    db.query(Response).filter(Response.question_id == question_id).delete()

    # Traiter et ajouter les nouvelles réponses
    try:
        parsed_responses = json.loads(responses)
        if not isinstance(parsed_responses, list):
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=400, detail="Format JSON invalide pour 'responses'.")

    for response_data in parsed_responses:
        if isinstance(response_data, str):
            try:
                response_data = json.loads(response_data)
            except Exception:
                raise HTTPException(status_code=400, detail="Élément invalide dans 'responses'.")

        new_response = Response(
            content=response_data["content"],
            is_correct=response_data["is_correct"],
            question_id=question_id,
            createdAt=datetime.now(timezone.utc),
            updatedAt=datetime.now(timezone.utc)
        )
        db.add(new_response)

    db.commit()
    db.refresh(question)

    return QuestionResponse.model_validate(question)

def delete_question(db: Session, question_id: int) -> bool:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question non trouvée")

    db.delete(question)
    db.commit()
    return True
