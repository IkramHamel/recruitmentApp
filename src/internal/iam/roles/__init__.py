
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .models import Role
from ..permissions.models import Permission
from .schemas import RoleCreate, RoleResponse,RoleUpdate
from src.utils.bcrypt import hash_password
from typing import List
from datetime import datetime, timezone
from src.core.logging import logger  
from typing import Dict
from sqlalchemy import func
# Create Role
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import Role  # Ensure this is the correct import for your model
from .schemas import RoleCreate, RoleResponse  # Ensure this is the correct import for your schemas

def create_role(db: Session, role_create: RoleCreate) -> RoleResponse:
    # Check if the role name already exists
    existing_role = db.query(Role).filter(Role.name == role_create.name).first()
    if existing_role:
        raise ValueError("Role name already exists.")
    db_role = Role(
        name=role_create.name,
    )
    try:
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return RoleResponse.model_validate(db_role)

    
    except IntegrityError:
        db.rollback()
        raise ValueError("An error occurred while saving the role.")


def get_roles(db: Session) -> List[RoleResponse]:
    db_roles = db.query(Role).all()
    return [
        RoleResponse(
            id=role.id,  
            name=role.name,  
            permissions=role.permissions ,
            createdAt=role.createdAt,
            updatedAt=role.updatedAt,
        )
        for role in db_roles
    ]

def update_roles(db: Session, role_update: RoleUpdate, id_role: int) -> RoleResponse:
    db_role = db.query(Role).filter(Role.id == id_role).first()

    if not db_role:
        raise HTTPException(status_code=404, detail=f"Role with ID {id_role} not found.")   
    if role_update.name:
        db_role.name = role_update.name

    # Remplacer complètement les permissions
    if role_update.permissions is not None:
        # Récupérer les objets Permission correspondant aux IDs
        new_permissions = db.query(Permission).filter(Permission.id.in_(role_update.permissions)).all()
        db_role.permissions = new_permissions  # Écrasement complet

    # Mettre à jour la date de mise à jour
    db_role.updatedAt = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_role)

    return RoleResponse(
        id=db_role.id,
        name=db_role.name,
        permissions=db_role.permissions,
        createdAt=db_role.createdAt,
        updatedAt=db_role.updatedAt,
    )

# Get Role by ID
def get_role_by_id(db: Session, role_id: int) -> RoleResponse:
    db_role = db.query(Role).filter(Role.id == role_id).first()
    print(f"roles : {db_role}")

    if db_role:
        return RoleResponse(
            id=db_role.id,  
            name=db_role.name,  
            permissions=db_role.permissions ,
            createdAt=db_role.createdAt,
            updatedAt=db_role.updatedAt,
        ) 
    return None

# Delete Role

def delete_role(db: Session, role_id: int) -> bool:
    db_role = db.query(Role).filter(Role.id == role_id).first()
    
    if not db_role:
        raise HTTPException(status_code=404, detail=f"Role with ID {role_id} not found.")  
    
    db.delete(db_role)
    db.commit()
    return True


def count_permissions_by_roles(db: Session) -> Dict[int, int]:
    results = (
        db.query(Role.id, func.count(Permission.id))
        .join(Role.permissions)
        .group_by(Role.id)
        .all()
    )
    return {role_id: count for role_id, count in results}

