from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Response 
from .schemas import ResponseCreate, ResponseUpdate, Response as ResponseSchema 
from typing import List
from datetime import datetime, timezone

def create_response(db: Session, response_data: ResponseCreate) -> ResponseSchema:
    response = Response(
        content=response_data.content,
        is_correct=response_data.is_correct,
        question_id=response_data.question_id
    )

    db.add(response)
    db.commit()
    db.refresh(response)
    return ResponseSchema.model_validate(response)

def get_responses(db: Session) -> List[ResponseSchema]:
    responses = db.query(Response).all()
    return [ResponseSchema.model_validate(r) for r in responses]

def get_response_by_id(db: Session, response_id: int) -> ResponseSchema:
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")
    return ResponseSchema.model_validate(response)

def update_response(db: Session, response_id: int, update_data: ResponseUpdate) -> ResponseSchema:
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")

    response.content = update_data.content
    response.is_correct = update_data.is_correct
    response.question_id = update_data.question_id
    response.updatedAt = datetime.now(timezone.utc)

    db.commit()
    db.refresh(response)
    return ResponseSchema.model_validate(response)

def delete_response(db: Session, response_id: int) -> bool:
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")

    db.delete(response)
    db.commit()
    return True
