from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.internal.anti_cheat.schemas import (
    AntiCheatRuleCreate,
    AntiCheatRuleUpdate,
    AntiCheatRuleResponse,
)
from src.internal.anti_cheat import (
    create_anti_cheat_rule,
    get_all_anti_cheat_rules,
    get_anti_cheat_rule_by_id,
    update_anti_cheat_rule,
    delete_anti_cheat_rule,
)
from src.core.logging import logger
from typing import List
from src.api.endpoint import BaseEndpoint
from src.internal.iam.users.models import User
from src.api.middlewares.authz import has_permission
from src.internal.anti_cheat.permissions import PERMISSIONS_ANTICHEAT
from fastapi import  WebSocket,WebSocketDisconnect
from fastapi.responses import HTMLResponse

class AntiCheatRulesEndpoint:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger
    
   

    def get_routers(self) -> List[APIRouter]:
        router = APIRouter()

        @router.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            await websocket.send_text("✅ Connecté au serveur FastAPI")

            try:
                while True:
                    data = await websocket.receive_text()
                    print(f"📩 Message reçu: {data}")
                    await websocket.send_text(f"Echo: {data}")

            except WebSocketDisconnect:
                print("❌ Client déconnecté proprement")
            except Exception as e:
                print(f"⚠️ Erreur WebSocket: {e}")
            finally:
                print("🚪 Fermeture de la connexion WebSocket")

        @router.post("/", response_model=AntiCheatRuleResponse)
        def create_rule(rule: AntiCheatRuleCreate, db: Session = Depends(self.db_session),
                        currentUser: User = Depends(has_permission(PERMISSIONS_ANTICHEAT["Rules Management"]["permissions"][0]["name"]))):
            self.logger.info("Creating new anti-cheat rule")
            return create_anti_cheat_rule(db, rule)

        @router.get("/", response_model=List[AntiCheatRuleResponse])
        def get_rules(db: Session = Depends(self.db_session),
                    currentUser: User = Depends(has_permission(PERMISSIONS_ANTICHEAT["Rules Management"]["permissions"][1]["name"]))):

            self.logger.info("Fetching all anti-cheat rules")
            return get_all_anti_cheat_rules(db)

        @router.get("/{rule_id}", response_model=AntiCheatRuleResponse)
        def get_rule_by_id(rule_id: int, db: Session = Depends(self.db_session),
                    currentUser: User = Depends(has_permission(PERMISSIONS_ANTICHEAT["Rules Management"]["permissions"][3]["name"]))):

            self.logger.info(f"Fetching anti-cheat rule with ID {rule_id}")
            rule = get_anti_cheat_rule_by_id(db, rule_id)
            if not rule:
                self.logger.error(f"Anti-cheat rule with ID {rule_id} not found")
                raise HTTPException(status_code=404, detail="Rule not found")
            return rule

        @router.put("/{rule_id}", response_model=AntiCheatRuleResponse)
        def update_rule(rule_id: int, rule_update: AntiCheatRuleUpdate, db: Session = Depends(self.db_session),
                        currentUser: User = Depends(has_permission(PERMISSIONS_ANTICHEAT["Rules Management"]["permissions"][1]["name"]))):

            self.logger.info(f"Updating anti-cheat rule with ID {rule_id}")
            updated = update_anti_cheat_rule(db, rule_id, rule_update)
            if not updated:
                self.logger.error(f"Anti-cheat rule with ID {rule_id} not found")
                raise HTTPException(status_code=404, detail="Rule not found")
            return updated

        @router.delete("/{rule_id}")
        def delete_rule(rule_id: int, db: Session = Depends(self.db_session),
                        currentUser: User = Depends(has_permission(PERMISSIONS_ANTICHEAT["Rules Management"]["permissions"][3]["name"]))):

            self.logger.info(f"Deleting anti-cheat rule with ID {rule_id}")
            success = delete_anti_cheat_rule(db, rule_id)
            if not success:
                self.logger.error(f"Anti-cheat rule with ID {rule_id} not found")
                raise HTTPException(status_code=404, detail="Rule not found")
            return {"message": "Anti-cheat rule deleted successfully"}

        return [router]
