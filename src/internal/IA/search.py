from typing import List
from pydantic import BaseModel
from agno.vectordb.pgvector import PgVector, SearchType
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from ...utils.llmlite import switch_model
from agno.db.postgres import PostgresDb
from agno.knowledge.embedder.google import GeminiEmbedder
import os

# --- Configuration du modèle et de l'agent ---
model = switch_model(
    id="gemini/gemini-2.0-flash-exp",
    provider="gemini",
    api_key=os.environ["GEMINI_API_KEY"],
    instructions=[
        "Tu es un recruteur IA expert en analyse de CV.",
        "Analyse chaque candidat et explique pourquoi il correspond à la recherche.",
        "Réponds uniquement en JSON valide, avec les candidats pertinents."
    ],
    max_tokens=300,
    temperature=0.7
)

embedder = GeminiEmbedder(dimensions=1536, api_key=os.environ["GEMINI_API_KEY"])

vector_db = PgVector(
    table_name="knowledge_vectors",
    db_url=os.environ["DATABASE_URL"],
    embedder=embedder,
    search_type=SearchType.hybrid
)

contents_db = PostgresDb(
    db_url=os.environ["DATABASE_URL"],
    knowledge_table="knowledge_contents"
)

knowledge = Knowledge(
    vector_db=vector_db,
    contents_db=contents_db
)

# --- Modèle Pydantic ---
class CandidateResult(BaseModel):
    id_candidate: int
    reason: str
class CandidateSearchResponse(BaseModel):
    results: List[CandidateResult]



# --- Agent RH ---
hr_agent = Agent(
    name="Recruteur IA",
    model=model,
    knowledge=knowledge,
    search_knowledge=True,
    output_schema=CandidateSearchResponse  # ← LISTE directement
)

# --- Fonction de recherche (candidats valides uniquement) ---
def search_valid_candidates(query: str, top_k: int = 10) -> List[CandidateResult]:
    results = vector_db.search(query, limit=top_k)
    
    if not results:
        print(" Aucun candidat trouvé dans la base.")
        return []

    # Construire le texte des candidats pour le prompt
    candidates_text = ""
    for result in results:
        print("DEBUG candidate_id:", result.meta_data.get("candidate_id"))
        print("DEBUG content:", result.content)
        candidate_id = result.meta_data.get("candidate_id", 0)
        content = result.content
        candidates_text += f"\nID: {candidate_id}\nProfil: {content}\n"
    print("canddd",candidates_text)
    prompt = f"""

Tu es un recruteur IA expert en analyse de CV.

Étapes :
1. Réécris et clarifie la requête utilisateur : {query}.
2. Décompose la requête en critères précis (compétences, expérience, formation...).
3. Analyse chaque candidat ci-dessous.
4. Retourne UNIQUEMENT les candidats qui correspondent.
5. Pour chaque candidat valide, fournis :
   - id_candidate : identifiant
   - reason : raison détaillée
6. Si aucun candidat ne correspond, renvoie un tableau vide [].
7. Réponds uniquement en JSON valide.

Candidats à analyser :
{candidates_text}
"""

    try:
        response = hr_agent.run(input=prompt)

        if hasattr(response, "content") and hasattr(response.content, "results"):
            results_list = response.content.results
            print("DEBUG results_list:", results_list)
            return results_list

        return []

    except Exception as e:
        print(f"⚠️ Erreur lors de l'analyse: {e}")
        return []

def get_talent_recommendations(search_query: str, top_k: int = 10) -> List[CandidateResult]:
    print(f"🔍 Lancement de la recherche pour: '{search_query}'")
    return search_valid_candidates(search_query, top_k)
