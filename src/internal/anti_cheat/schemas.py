# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AntiCheatRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    initial_score: Optional[int] = 20

    tab_switches: Optional[bool] = True
    tab_switch_weight: Optional[int] = 3

    copy_paste: Optional[bool] = True
    copy_paste_weight: Optional[int] = 5

    inspect_element: Optional[bool] = True
    inspect_element_weight: Optional[int] = 1

    window_switches: Optional[bool] = True
    window_switches_weight: Optional[int] = 3

class AntiCheatRuleCreate(AntiCheatRuleBase):
    pass

class AntiCheatRuleUpdate(AntiCheatRuleBase):
    pass

class AntiCheatRuleResponse(AntiCheatRuleBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
