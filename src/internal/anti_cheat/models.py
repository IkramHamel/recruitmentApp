from sqlalchemy import Column, Integer, String, DateTime, Enum,Table,ForeignKey,Boolean,JSON
from sqlalchemy.orm import relationship
from src.db.session import Base
from datetime import datetime, timezone
from enum import Enum
class AntiCheatRule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String,nullable=True)
    initial_score = Column(Integer)  

    tab_switches = Column(Boolean,default=True)  
    tab_switch_weight = Column(Integer)  

    copy_paste = Column(Boolean,default=True)  
    copy_paste_weight = Column(Integer)  

    inspect_element = Column(Boolean,default=True)  
    inspect_element_weight = Column(Integer)  

    window_switches = Column(Boolean,default=True)  
    window_switches_weight = Column(Integer) 

    assessments = relationship("Assessment", back_populates="rules",passive_deletes=True)  

    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    


    
    
    