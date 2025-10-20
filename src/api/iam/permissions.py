from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.iam.permissions.schemas import  PermissionResponse ,GroupPermissionResponse
from src.core.logging import logger
from typing import List
from src.api.endpoint import BaseEndpoint
from ...internal.iam.permissions import get_groupPerms , get_permissions_by_role

class PermissionsEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger  # Utiliser ton logger personnalisé ou standard

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/permissions")
        
        @router.get("/", response_model=List[GroupPermissionResponse])
        def get_GroupPermissions_endpoint(db: Session = Depends(self.db_session)):
            """Fetch all group permissions."""
            self.logger.info("Attempting to fetch all group permissions")
            db_grp = get_groupPerms(db) 
            return db_grp
        @router.get("/{role_id}", response_model=List[PermissionResponse])
        def getPermissionsByRole_endpoint(role_id: int, db: Session = Depends(self.db_session)):
            self.logger.info(f"Attempting to fetch role with ID: {role_id}")
            db_role = get_permissions_by_role(db, role_id)
            if db_role is None:
                self.logger.error(f"Role with ID {role_id} not found.")
                raise HTTPException(status_code=404, detail="Role not found")
            return db_role
        
        """@router.post("/", response_model=PermissionResponse)
        def create_permission_endpoint(permission: PermissionCreate, db: Session = Depends(self.db_session)):
            created_permission = create_permission(db, permission)
            return created_permission
    

        @router.post("/", response_model=GroupPermissionResponse)
        def create_groupPerm_endpoint(groupPerm: GroupPermissionCreate, db: Session = Depends(self.db_session)):
            created_groupPerm = create_groupPerm(db, groupPerm)
            return created_groupPerm"""

        
        
        return router




