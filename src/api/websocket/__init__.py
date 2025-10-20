from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from src.core.logging import logger
from src.internal.exam.assessment.models import Assessment
from src.internal.exam.results.models import Result
from src.internal.job_positions.models import JobCandidate
from datetime import datetime
from src.internal.anti_cheat.models import AntiCheatRule
from src.db.session import get_db

class WebSocketEndpoints:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logger
    
    def get_routers(self) -> List[APIRouter]:
        router = APIRouter()

        active_connections: List[WebSocket] = []

        async def connect(websocket: WebSocket):
            await websocket.accept()
            active_connections.append(websocket)
            print
        def disconnect(websocket: WebSocket):
            if websocket in active_connections:
                active_connections.remove(websocket)

        # Dictionnaire global pour garder le score par candidat
        candidate_scores = {}

        @router.websocket("/ws/anti-cheat")
        async def anti_cheat_socket(websocket: WebSocket):
            await connect(websocket)
            db = next(get_db())
            try:
                while True:
                    data = await websocket.receive_json()
                    print("🔔 Anti-cheat event reçu:", data)

                    candidate_id = data.get("candidateId")
                    assessment_id = data.get("assessmentId")
                    event_type = data.get("type")
                    timestamp = data.get("timestamp")

                    if not candidate_id or not assessment_id or not event_type:
                        print("⚠️ Event ignoré car données incomplètes:", data)
                        continue

                    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
                    if not assessment:
                        print(f"❌ Assessment introuvable pour ID {assessment_id}")
                        continue

                    rule = db.query(AntiCheatRule).filter(AntiCheatRule.id == assessment.rules_id).first()
                    if not rule:
                        print(f"⚠️ Règle anti-triche non trouvée pour l'ID: {assessment.rules_id}")
                        continue

                    if candidate_id not in candidate_scores:
                        candidate_scores[candidate_id] = rule.initial_score

                    score = candidate_scores[candidate_id]

                    # Gestion des événements
                    if event_type == "copy_paste" and rule.copy_paste:
                        score -= rule.copy_paste_weight
                        print(f"✂️ Copy detected → -{rule.copy_paste_weight} | New score: {score}")

                    elif event_type == "window_switch" and rule.window_switches:
                        score -= rule.window_switches_weight
                        print(f"🪟 Window switch detected → -{rule.window_switches_weight} | New score: {score}")

                    elif event_type == "inspect_element" and rule.inspect_element:
                        score -= rule.inspect_element_weight
                        print(f"🔎 Inspect detected → -{rule.inspect_element_weight} | New score: {score}")

                    elif event_type == "tab_switch" and rule.tab_switches:
                        score -= rule.tab_switch_weight
                        print(f"📑 Tab switch detected → -{rule.tab_switch_weight} | New score: {score}")

                    else:
                        print(f"⚠️ Event {event_type} reçu mais non activé dans la règle")

                    candidate_scores[candidate_id] = score

                    # Vérification seuil critique
                    if score <= 0:
                        print(f"🚨 Candidat {candidate_id} disqualifié pour triche (score épuisé) !")

                        job_candidate = db.query(JobCandidate).filter(JobCandidate.candidate_id == candidate_id).first()
                        if job_candidate:

                            # Création automatique du Result si inexistant
                            if not job_candidate.results:
                                new_result = Result(
                                    score=0,
                                    responses=[],
                                    jobcandidate_id=job_candidate.id,
                                    assessment_id=assessment_id,
                                    is_cheating=True,
                                    createdAt=datetime.utcnow(),
                                    updatedAt=datetime.utcnow()
                                )
                                db.add(new_result)

                            db.commit()

                        # Notifie le front et ferme la session
                        await websocket.send_json({
    "status": "cheating_detected",
    "message": "Session terminée pour triche",
    "score": score,
    "redirect": "/recruitment/avertissement"  # page résultat ou avertissement
})
                        job_candidate.quiz_submitted = True
                        db.add(job_candidate)
                        db.commit()
                        await websocket.close()

                        break

                    # Sinon renvoie le score actuel au front
                    else:
                        await websocket.send_json({
                            "status": "received",
                            "event": event_type,
                            "score": score
                        })

            except WebSocketDisconnect:
                disconnect(websocket)
                print(f"❌ Candidat {candidate_id} déconnecté")

        return [router]