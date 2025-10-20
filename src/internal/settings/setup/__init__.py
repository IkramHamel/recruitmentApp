from sqlalchemy.orm import Session
from src.internal.settings.app_settings import get_app_settings
from src.internal.settings.app_settings.models import SetupStatus

from src.internal.iam.users import create_user
from src.internal.settings.elevanlabs import create_credential
from src.internal.settings.reasoners import create_reasoner
from sqlalchemy.exc import IntegrityError
from .schemas import SetupInput


# Function to handle the setup
def setup_application(db: Session, setup_input: SetupInput):
    # Fetch current app settings
    app_settings = get_app_settings(db)
    
    # Check if setup is already finished (setup_status == 1)
    if app_settings and app_settings.setup_status == SetupStatus.DONE:
        return {"message": "Setup already completed. No further actions needed."}
    
    # 1. Set Organization Name (if needed)
    # Assuming organizationName is directly stored or used in app settings
    app_settings.organizationName = setup_input.organizationName
    
    # 2. Create Admin User
    try:
        admin_user = create_user(db, setup_input.admin_account)  # Create the admin user
    except IntegrityError:
        raise ValueError("Admin account already exists.")
    
    # 3. Create ElevanLabs Credentials
    created_credentials = []
    for credential in setup_input.credentials:
        created_credential = create_credential(db, credential)  # Create each ElevanLab credential
        created_credentials.append(created_credential)
    
    # 4. Create Reasoners and set default reasoner
    default_reasoner = None
    for reasoner in setup_input.reasoners:
        create_reasoner(db, reasoner)  # Create each reasoner

    """assemblyAI = []
    for assembly in setup_input.assemblyAI:
        created_assembly = created_assembly(db, assembly)  # Create each assembly
        assemblyAI.append(created_assembly)"""
   
    
    # 5. Update setup status to 4 (completed)
    app_settings.setup_status = SetupStatus.DONE
    
    # Commit changes to the database
    db.commit()
    db.refresh(app_settings)
    
    return {"message": "Setup completed successfully!", "organization": app_settings.organizationName, "admin_user": admin_user.username, "default_reasoner": default_reasoner.name}


def get_setup_status(db:Session):
    # Fetch current app settings
    app_settings = get_app_settings(db)
    
    return app_settings.setup_status