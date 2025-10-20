from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import NotificationTemplate
from .schemas import (
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    NotificationTemplateResponse
)
from typing import List

# Create a new NotificationTemplate
def create_notification_template(
    db: Session,
    template_create: NotificationTemplateCreate
) -> NotificationTemplateResponse:
    db_template = NotificationTemplate(
        title=template_create.title,
        content=template_create.content,
        contentType=template_create.contentType  # New field added
    )
    try:
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return NotificationTemplateResponse.model_validate(db_template)
    except IntegrityError:
        db.rollback()
        raise ValueError("NotificationTemplate with this title already exists.")

# Get all NotificationTemplates
def get_notification_templates(db: Session) -> List[NotificationTemplateResponse]:
    db_templates = db.query(NotificationTemplate).all()
    return [NotificationTemplateResponse.model_validate(template) for template in db_templates]

# Get NotificationTemplate by ID
def get_notification_template_by_id(
    db: Session,
    template_id: int
) -> NotificationTemplateResponse:
    db_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if db_template:
        return NotificationTemplateResponse.model_validate(db_template)
    raise ValueError(f"NotificationTemplate with ID {template_id} not found.")

# Update NotificationTemplate
def update_notification_template(
    db: Session,
    template_id: int,
    template_update: NotificationTemplateUpdate
) -> NotificationTemplateResponse:
    db_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()

    if db_template:
        if template_update.title:
            db_template.title = template_update.title
        if template_update.content:
            db_template.content = template_update.content
        if template_update.contentType:
            db_template.contentType = template_update.contentType  # Update content type

        db.commit()
        db.refresh(db_template)
        return NotificationTemplateResponse.model_validate(db_template)
    else:
        raise ValueError(f"NotificationTemplate with ID {template_id} not found.")

# Delete NotificationTemplate
def delete_notification_template(db: Session, template_id: int) -> bool:
    db_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()

    if db_template:
        db.delete(db_template)
        db.commit()
        return True
    else:
        raise ValueError(f"NotificationTemplate with ID {template_id} not found.")
