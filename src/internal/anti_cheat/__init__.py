# crud.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from .models import AntiCheatRule
from .schemas import AntiCheatRuleCreate, AntiCheatRuleUpdate, AntiCheatRuleResponse
from typing import List


def create_anti_cheat_rule(db: Session, rule_create: AntiCheatRuleCreate) -> AntiCheatRuleResponse:
    existing = db.query(AntiCheatRule).filter(AntiCheatRule.name == rule_create.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rule name already exists.")

    rule = AntiCheatRule(**rule_create.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return AntiCheatRuleResponse.model_validate(rule)


def get_all_anti_cheat_rules(db: Session) -> List[AntiCheatRuleResponse]:
    rules = db.query(AntiCheatRule).all()
    return [AntiCheatRuleResponse.model_validate(rule) for rule in rules]


def get_anti_cheat_rule_by_id(db: Session, rule_id: int) -> AntiCheatRuleResponse:
    rule = db.query(AntiCheatRule).filter(AntiCheatRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return AntiCheatRuleResponse.model_validate(rule)


def update_anti_cheat_rule(db: Session, rule_id: int, rule_update: AntiCheatRuleUpdate) -> AntiCheatRuleResponse:
    rule = db.query(AntiCheatRule).filter(AntiCheatRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    for field, value in rule_update.dict(exclude_unset=True).items():
        setattr(rule, field, value)

    rule.updatedAt = datetime.now(timezone.utc)
    db.commit()
    db.refresh(rule)
    return AntiCheatRuleResponse.model_validate(rule)


def delete_anti_cheat_rule(db: Session, rule_id: int) -> bool:
    rule = db.query(AntiCheatRule).filter(AntiCheatRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
    return True
