from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.iam.roles.schemas import RoleCreate,RoleResponse,RoleUpdate
from src.internal.iam.roles import create_role,get_roles,get_role_by_id,delete_role,update_roles,count_permissions_by_roles
from src.core.logging import logger  
from typing import List
from src.api.endpoint import BaseEndpoint
from src.internal.iam.users.models import User
from src.internal.iam.roles.permissions import PERMISSIONS_ROLES
from src.api.middlewares.authz import has_permission
"""
dependencies=[Depends(requiresAuth)]
current_user: User = Depends(require_roles("ADMINISTRATOR"))
current_user: User = Depends(require_roles("ADMINISTRATOR"))
"""
class RolesEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger  # You can use standard logging or a custom logger

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/roles")

        @router.post("/", response_model=RoleResponse)
        def create_role_endpoint(role: RoleCreate, db: Session = Depends(self.db_session),
                                 currentUser: User = Depends(has_permission(PERMISSIONS_ROLES["Role Management"]["permissions"][0]["name"]))):
            created_role = create_role(db, role)
            return created_role

        
        
        @router.get("/", response_model=List[RoleResponse])
        def get_roles_endpoint(db: Session = Depends(self.db_session),
                               currentUser: User = Depends(has_permission(PERMISSIONS_ROLES["Role Management"]["permissions"][1]["name"]))):
            """Fetch all roles."""
            self.logger.info("Attempting to fetch all roles")
            db_roles = get_roles(db) 
            return db_roles
        
        @router.get("/{role_id}", response_model=RoleResponse)
        def get_role_endpoint(role_id: int, db: Session = Depends(self.db_session),
                              currentUser: User = Depends(has_permission(PERMISSIONS_ROLES["Role Management"]["permissions"][4]["name"]))):
            self.logger.info(f"Attempting to fetch role with ID: {role_id}")
            db_role = get_role_by_id(db, role_id)
            if db_role is None:
                self.logger.error(f"Role with ID {role_id} not found.")
                raise HTTPException(status_code=404, detail="Role not found")
            self.logger.info(f"Role found with ID: {db_role.id}")
            return db_role
        @router.put("/{role_id}", response_model=RoleResponse)
        def update_role_endpoint(role_id: int, role_update: RoleUpdate, db: Session = Depends(self.db_session),
                                 currentUser: User = Depends(has_permission(PERMISSIONS_ROLES["Role Management"]["permissions"][2]["name"]))):
            self.logger.info(f"Attempting to update role with ID: {role_id}")
            updated_role = update_roles(db,  role_update,role_id)
            if updated_role is None:
                self.logger.error(f"role with ID {role_id} not found.")
                raise HTTPException(status_code=404, detail="User not found")
            self.logger.info(f"User updated with ID: {updated_role.id}")
            return updated_role
        
        @router.delete("/{role_id}")
        def delete_role_endpoint(role_id: int, db: Session = Depends(self.db_session),
                                 currentUser: User = Depends(has_permission(PERMISSIONS_ROLES["Role Management"]["permissions"][3]["name"]))):
            self.logger.info(f"Attempting to delete user with ID: {role_id}")
            success = delete_role(db, role_id)
            if not success:
                self.logger.error(f"Roel with ID {role_id} not found.")
                raise HTTPException(status_code=404, detail="Role not found")
            self.logger.info(f"Role with ID {role_id} deleted.")
            return {"message": "Role deleted successfully"}
        @router.get("/permissions/count")
        def get_count_permissions(db: Session = Depends(self.db_session)):
            return count_permissions_by_roles(db)
    
        return router
