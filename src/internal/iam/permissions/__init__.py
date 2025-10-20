from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from .models import Permission,GroupPermission
from ..roles.models import Role,role_permission_association
from sqlalchemy.orm import joinedload
from .schemas import PermissionCreate,GroupPermissionResponse,PermissionResponse

from typing import List
 

# Create Permission
def create_permission(db: Session, permission_create: PermissionCreate) -> Permission:
    # Crée un nouvel objet Permission avec les données reçues
    db_permission = Permission(
        name=permission_create.name,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
    )

    try:
        # Ajouter à la session
        db.add(db_permission)
        # Valider les changements dans la base de données
        db.commit()
        # Rafraîchir l'objet pour obtenir les valeurs mises à jour (ex : id généré)
        db.refresh(db_permission)
        return db_permission  # Retourner l'objet Permission créé
    except IntegrityError:
        # En cas d'erreur d'intégrité (par exemple, nom de permission déjà existant)
        db.rollback()
        raise HTTPException(status_code=400, detail="Permission name already exists.")



def get_groupPerms(db: Session) -> List[GroupPermissionResponse]:
    db_groupPerms = db.query(GroupPermission).all()
    return [
        GroupPermission(
            id=groupPerm.id,  
            name=groupPerm.name,  
            description=groupPerm.description,  
            permissions=groupPerm.permissions ,
            createdAt=groupPerm.createdAt,
            updatedAt=groupPerm.updatedAt,
        )
        for groupPerm in db_groupPerms
    ]
        

# Get groupPerm by ID
def get_groupPerm_by_id(db: Session, groupPerm_id: int) -> GroupPermissionResponse:
    db_groupPerm = db.query(GroupPermission).filter(GroupPermission.id == groupPerm_id).first()
    print(f"groupPerms : {db_groupPerm}")

    if db_groupPerm:
        return GroupPermissionResponse(
            id=db_groupPerm.id,  
            name=db_groupPerm.name,  
            description=db_groupPerm.description,  

            permissions=[permission.id for permission in db_groupPerm.permissions] ,
            createdAt=db_groupPerm.createdAt,
            updatedAt=db_groupPerm.updatedAt,
        ) 
    return None


def get_permissions_by_role(db: Session, role_id: int) -> List[PermissionResponse]:
    # Récupérer le rôle avec ses permissions
    role = db.query(Role).filter(Role.id == role_id).options(joinedload(Role.permissions)).first()
    
    if not role:
        return []

    # Retourner les permissions sous forme de réponse
    return [
        PermissionResponse(
            id=permission.id,
            name=permission.name,
            description=permission.description,
            createdAt=permission.createdAt,
            updatedAt=permission.updatedAt
        )
        for permission in role.permissions  # Utilisation de 'role.permissions'
    ]


