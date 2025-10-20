from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer,HTTPBearer,HTTPAuthorizationCredentials
from src.internal.iam.users.models import User
from src.internal.iam.users.models import Role
from src.utils.jwt import decode_access_token
from src.core.base import get_db
from ...internal.iam.permissions.models import Permission
from sqlalchemy.orm import joinedload
from fastapi import Depends


# Define the OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Define the HTTPBearer security scheme
security = HTTPBearer()
#def verify_quiz_token(token: str) -> dict:
    #try:
        #payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #return payload
    #except JWTError:
        #raise HTTPException(status_code=401, detail="Token invalide ou expiré")
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Retrieves the current user based on the provided token.
    """
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = (
        db.query(User)
        .options(joinedload(User.role).joinedload(Role.permissions))  
        .filter(User.username == username)
        .first()
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
   
    return user

def require_roles(*roles: str):
    """
    Decorator to enforce role-based access control on endpoints.
    :param roles: Allowed roles for the endpoint.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        # Assurez-vous que l'utilisateur a un seul rôle
        if current_user.role.name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user
    return role_checker
def has_permission(required_permission: str):
    def permission_checker(current_user: User = Depends(get_current_user)):
        if not current_user.role or not current_user.role.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No role or permissions found"
            )

        user_permissions = {perm.name for perm in current_user.role.permissions}

        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return current_user
    return permission_checker


# Dependency to check the authorization token
def requiresAuth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print(f"DEBUG: Received token: {token}")  # Debug
    if token == "":
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token
def require_permission(permission_name: str):
    """Vérifie si l'utilisateur possède la permission"""
    def permission_dependency(user_role: Role = Depends(require_roles)):
        if permission_name not in [perm.name for perm in user_role.permissions]:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user_role
    return permission_dependency