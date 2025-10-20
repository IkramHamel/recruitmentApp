from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.exam.test.schemas import TestCreate, TestUpdate, TestResponse
from src.internal.exam.test import (
    create_test,
    get_tests,
    get_test_by_id,
    update_test,
    delete_test
)
from typing import List
from src.api.endpoint import BaseEndpoint
from src.core.logging import logger
from src.internal.iam.users.models import User
from src.internal.exam.test.permissions import PERMISSIONS_TESTS
from src.api.middlewares.authz import has_permission
class TestsEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/tests")

        @router.post("/", response_model=TestResponse)
        def create_test_endpoint(test_data: TestCreate, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_TESTS["Test Management"]["permissions"][0]["name"]))
):
            return create_test(db, test_data)

        @router.get("/", response_model=List[TestResponse])
        def get_all_tests_endpoint(db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_TESTS["Test Management"]["permissions"][1]["name"]))
):
            return get_tests(db)

        @router.get("/{test_id}", response_model=TestResponse)
        def get_test_endpoint(test_id: int, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_TESTS["Test Management"]["permissions"][4]["name"]))
):
            test = get_test_by_id(db, test_id)
            if not test:
                raise HTTPException(status_code=404, detail="Test not found")
            return test

        @router.put("/{test_id}", response_model=TestResponse)
        def update_test_endpoint(test_id: int, test_update: TestUpdate, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_TESTS["Test Management"]["permissions"][2]["name"]))
):
            return update_test(db, test_id, test_update)

        @router.delete("/{test_id}")
        def delete_test_endpoint(test_id: int, db: Session = Depends(self.db_session),currentUser: User = Depends(has_permission(PERMISSIONS_TESTS["Test Management"]["permissions"][3]["name"]))
):
            success = delete_test(db, test_id)
            if not success:
                raise HTTPException(status_code=404, detail="Test not found")
            return {"message": "Test deleted successfully"}

        return router
