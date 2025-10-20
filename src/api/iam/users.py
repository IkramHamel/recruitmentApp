from fastapi import APIRouter, Depends, HTTPException,Body
from sqlalchemy.orm import Session
from src.internal.iam.users.schemas import UserCreate, UserUpdate, UserResponse
from src.internal.iam.users import create_user, get_user_by_id, update_user, delete_user, get_users
from src.core.logging import logger  # Assuming you have a logger set up (if not, use standard logging)
from typing import List
from src.api.endpoint import BaseEndpoint
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from src.internal.iam.users.models import User
from src.internal.iam.users.permissions import PERMISSIONS_USERRS

from src.api.endpoint import BaseEndpoint

from src.api.middlewares.authz import has_permission
"""
dependencies=[Depends(requiresAuth)]
current_user: User = Depends(require_roles("ADMINISTRATOR"))
current_user: User = Depends(require_roles("ADMINISTRATOR"))
"""
class UsersEndpoint(BaseEndpoint):
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger  # You can use standard logging or a custom logger

    def get_router(self) -> APIRouter:
        router = APIRouter(prefix="/users")
        
        @router.post("/", response_model=UserResponse)
        def create_user_endpoint(user: UserCreate, db: Session = Depends(self.db_session),
              currentUser: User = Depends(has_permission(PERMISSIONS_USERRS["User Management"]["permissions"][0]["name"]))):
            print(f"this is user {currentUser}")
            self.logger.info(f"Attempting to create user with username: {user.username}")
            created_user = create_user(db, user)
            self.logger.info(f"User created with ID: {created_user.id}")
            return created_user

        @router.get("/{user_id}", response_model=UserResponse)
        def get_user_endpoint(user_id: int, db: Session = Depends(self.db_session),
                              currentUser: User = Depends(has_permission(PERMISSIONS_USERRS["User Management"]["permissions"][4]["name"]))):
            self.logger.info(f"Attempting to fetch user with ID: {user_id}")
            db_user = get_user_by_id(db, user_id)
            if db_user is None:
                self.logger.error(f"User with ID {user_id} not found.")
                raise HTTPException(status_code=404, detail="User not found")
            self.logger.info(f"User found with ID: {db_user.id}")
            return db_user
        """ , dependencies=[Depends(require_permission("view_users"))] """
        @router.get("/", response_model=List[UserResponse])

        def get_users_endpoint(db: Session = Depends(self.db_session),
                               currentUser: User = Depends(has_permission(PERMISSIONS_USERRS["User Management"]["permissions"][1]["name"]))):
            """Fetch all users."""
            self.logger.info("Attempting to fetch all users")
            db_users = get_users(db)  # No user_id passed, fetch all users
            return db_users

        @router.put("/{user_id}", response_model=UserResponse)
        def update_user_endpoint(user_id: int, user_update: UserUpdate, db: Session = Depends(self.db_session),
                                 currentUser: User = Depends(has_permission(PERMISSIONS_USERRS["User Management"]["permissions"][2]["name"]))):
            self.logger.info(f"Attempting to update user with ID: {user_id}")
            updated_user = update_user(db, user_id, user_update)
            if updated_user is None:
                self.logger.error(f"User with ID {user_id} not found.")
                raise HTTPException(status_code=404, detail="User not found")
            self.logger.info(f"User updated with ID: {updated_user.id}")
            return updated_user

        @router.delete("/{user_id}")
        def delete_user_endpoint(user_id: int, db: Session = Depends(self.db_session),
                                 currentUser: User = Depends(has_permission(PERMISSIONS_USERRS["User Management"]["permissions"][3]["name"]))):
            self.logger.info(f"Attempting to delete user with ID: {user_id}")
            success = delete_user(db, user_id)
            if not success:
                self.logger.error(f"User with ID {user_id} not found.")
                raise HTTPException(status_code=404, detail="User not found")
            self.logger.info(f"User with ID {user_id} deleted.")
            return {"message": "User deleted successfully"}
        @router.post("/send-email")
        def send_email(
        email: str = Body(...),
        password: str = Body(...),
        username: str = Body(...),
        
):
            try:
                subject = "Vos identifiants de connexion - 3S RH"

                message = f""" 
<html>
  <body style="font-family: Arial, sans-serif; color: #333; background-color: #f4f4f4; margin: 0; padding: 20px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
      <tr>
        <td style="background-color: #003366; color: #ffffff; text-align: center; padding: 20px;">
          <h2 style="margin: 0;">3S RH</h2>
        </td>
      </tr>

      <tr>
        <td style="padding: 25px;">
          <p>Bonjour {username},</p>
          <p>Votre compte a été créé avec succès sur la plateforme <strong>3S RH</strong>.</p>
          <p>Voici vos identifiants de connexion :</p>
          <ul style="list-style: none; padding: 0;">
            <li><strong>Email :</strong> {email}</li>
            <li><strong>Mot de passe :</strong> {password}</li>
          </ul>
          <p>➡️ Vous pouvez dès à présent vous connecter à votre compte et changer votre mot de passe.</p>
          <p>Cordialement,<br>L’équipe <strong>3S RH</strong></p>
        </td>
      </tr>

      <tr>
        <td style="background-color: #f4f4f4; text-align: center; padding: 15px; font-size: 12px; color: #777;">
          © 2025 3S RH — Tous droits réservés.
        </td>
      </tr>
    </table>
  </body>
</html>
"""

                msg = MIMEMultipart()
                msg["From"] = os.getenv("SENDER_EMAIL")
                msg["To"] = email
                msg["Subject"] = subject
                msg.attach(MIMEText(message, "html"))

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))
                server.sendmail(os.getenv("SENDER_EMAIL"), email, msg.as_string())
                server.quit()

                return {"status": "success", "message": "Email envoyé avec succès ✅"}

            except Exception as e:
                return {"status": "error", "message": str(e)}

        return router
