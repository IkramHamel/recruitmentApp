from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.logging import logger
from src.internal.iam.users.schemas import TokenResponse,UserLogin,UserResponse,UserUpdateProfile
from src.internal.iam.users.models import User
from src.internal.iam.users import get_user_by_username_for_auth
from typing import List
from src.utils.bcrypt import verify_password,hash_password
from src.utils.jwt import create_access_token
from typing import List
from src.api.middlewares.authz import get_current_user


class AuthEndpoints:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger

    def get_routers(self) -> List[APIRouter]:
        router = APIRouter()

        @router.post("/login", response_model=TokenResponse)
        def login(user: UserLogin, db: Session = Depends(self.db_session)):
            db_user = get_user_by_username_for_auth(db, user.username)
            if not db_user or not verify_password(db_user.password, user.password):
                raise HTTPException(status_code=401, detail="Invalid username or password")

            access_token = create_access_token({"sub": db_user.username, "role": str(db_user.role.name)})

            return {
        "access_token": access_token,
        "token_type": "bearer"  
    }

        
        @router.get("/me", response_model=UserResponse)
        def get_current_user_info(current_user: User = Depends(get_current_user)):  
          return current_user 
        


        @router.put("/me/update", response_model=UserResponse)
        def update_profile(
        data: UserUpdateProfile,
        db: Session = Depends(self.db_session),
        current_user: User = Depends(get_current_user)
):
    # 🔹 1. Récupérer l'utilisateur connecté
            user = db.query(User).filter(User.id == current_user.id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # 🔹 2. Mettre à jour les champs simples
            if data.firstName:
                user.firstName = data.firstName
            if data.lastName:
                user.lastName = data.lastName
            if data.username:
                user.username = data.username
            if data.email:
                user.email = data.email

    # 🔹 3. Changement du mot de passe
            if data.new_password:
                if not data.old_password or not verify_password(user.password, data.old_password):
                    raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
                user.password = hash_password(data.new_password)

            db.commit()
            db.refresh(user)
            return user


        return [router]
