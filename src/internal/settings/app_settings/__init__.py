from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import AppSettings, SupportedLanguages
from .schemas import AppSettingsCreate, AppSettingsUpdate, AppSettingsResponse, SupportedLanguageResponse
from typing import List
from .supported_languages import SUPPORTED_LANGUAGES

# Create new AppSettings
def create_app_settings(db: Session, app_settings_create: AppSettingsCreate) -> AppSettingsResponse:
    db_app_settings = AppSettings(
        organization_name=app_settings_create.organization_name,
        setup_status=app_settings_create.setup_status,
        default_language= app_settings_create.default_language     
    )
    
    try:
        db.add(db_app_settings)
        db.commit()
        db.refresh(db_app_settings)
        return AppSettingsResponse.model_validate(db_app_settings)
    except IntegrityError:
        db.rollback()
        raise ValueError("AppSettings entry with this configuration already exists.")



# Get AppSettings by ID (This function remains the same as the default_reasoner is also part of the AppSettings model)
def get_app_settings(db: Session) -> AppSettingsResponse:
    db_app_settings = db.query(AppSettings).first()
    if db_app_settings:
        return AppSettingsResponse.model_validate(db_app_settings)
    return None

# Update AppSettings (Including the update of the default_reasoner_id)
def update_app_settings(db: Session,app_settings_update: AppSettingsUpdate) -> AppSettingsResponse:
    db_app_settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if db_app_settings:
        if app_settings_update.organization_name:
            db_app_settings.organization_name = app_settings_update.organization_name
        if app_settings_update.default_language:
            db_app_settings.default_language = app_settings_update.default_language
        db.commit()
        db.refresh(db_app_settings)
        return AppSettingsResponse.model_validate(db_app_settings)
    else:
        raise ValueError(f"AppSettings with ID {1} not found.")

# Check if AppSettings exist, and if not, create new AppSettings
def check_or_create_app_settings(db: Session, app_settings_create: AppSettingsCreate) -> AppSettingsResponse:
    # Try to find existing app settings
    db_app_settings = db.query(AppSettings).first()

    if db_app_settings:
        # If settings are found, return them
        return AppSettingsResponse.model_validate(db_app_settings)
    else:
        # If not found, create new app settings
        return create_app_settings(db, app_settings_create)


def create_app_language(db: Session, lang: dict) -> SupportedLanguageResponse:
    db_app_lang = SupportedLanguages(
        language=lang.get("name"),
        icon = lang.get("icon")  
    )
    try:
        db.add(db_app_lang)
        db.commit()
        db.refresh(db_app_lang)
        return SupportedLanguageResponse.model_validate(db_app_lang)
    except IntegrityError:
        db.rollback()

def get_supported_languages(db: Session) -> List[SupportedLanguageResponse]:
    return db.query(SupportedLanguages).all()





# Check if AppSettings exist, and if not, create new AppSettings
def create_app_languages(db: Session):
    for lang in SUPPORTED_LANGUAGES:
        create_app_language(db,lang)
    
def get_list_timezones() -> List[str]:
    import pytz
    # Get all timezones
    timezones = pytz.all_timezones
    return timezones

