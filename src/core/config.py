import os
from pathlib import Path
from dotenv import load_dotenv


# Using Pathlib to set a relative path
dotenv_path = Path(__file__).resolve().parent / "../../.env"
# Load the .env file
load_dotenv(dotenv_path=dotenv_path, override=True)
# .env
class Config:
    """Configuration class to manage app settings."""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./talentscoutr.db")
    AUDIO_ITEMS_FOLDERS: str = os.getenv("AUDIO_ITEMS_FOLDERS", "./uploads/items")
  

    # Cloudinary Configuration
   
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")


# Create a config instance to use throughout the app
config = Config()
