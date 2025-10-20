from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Test
from .schemas import TestCreate, TestUpdate, TestResponse
from datetime import datetime, timezone
from typing import List

def create_test(db: Session, test_data: TestCreate) -> TestResponse:   

    test = Test(
        title=test_data.title,
        description=test_data.description,
    )

    db.add(test)
    db.commit()
    db.refresh(test)

    return TestResponse.model_validate(test)

def get_tests(db: Session) -> List[TestResponse]:
    tests = db.query(Test).all()
    return [TestResponse.model_validate(t) for t in tests]

def get_test_by_id(db: Session, test_id: int) -> TestResponse:
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test non trouvé")
    return TestResponse.model_validate(test)

def update_test(db: Session, test_id: int, update_data: TestUpdate) -> TestResponse:
    from ..questions.models import Question

    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test non trouvé")

    test.title = update_data.title
    test.description = update_data.description
    test.updatedAt = datetime.now(timezone.utc)

    if update_data.question_ids is not None:
        questions = db.query(Question).filter(Question.id.in_(update_data.question_ids)).all()
        if len(questions) != len(update_data.question_ids):
            raise HTTPException(status_code=400, detail="Une ou plusieurs questions sont invalides")
        test.questions = questions

    db.commit()
    db.refresh(test)
    return TestResponse.model_validate(test)

def delete_test(db: Session, test_id: int) -> bool:
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test non trouvé")

    db.delete(test)
    db.commit()
    return True
