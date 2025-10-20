from pydantic import BaseModel
from typing import List
from src.internal.iam.users.schemas import UserCreate
from src.internal.settings.reasoners.schemas import ReasonerCreate
from src.internal.settings.elevanlabs.schemas import ElevanLabCredentialCreate
from src.internal.settings.assemblyAI.schemas import AssemblyAICredentialCreate
from src.internal.settings.communication.schemas import CommunicationCreate



class SetupInput(BaseModel):
    organizationName: str
    admin_account: UserCreate  # Assuming UserCreate is defined elsewhere for the admin
    credentials: List[ElevanLabCredentialCreate]  # List of credentials, at least 1
    reasoners: List[ReasonerCreate]  # List of reasoners, at least 1
    assemblyAI: List[AssemblyAICredentialCreate]  # List of reasoners, at least 1
    communication: List[CommunicationCreate]  # List of reasoners, at least 1





