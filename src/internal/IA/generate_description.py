
from agno.agent import Agent
from ...utils.llmlite import switch_model
import os
model = switch_model(
    id="gemini-2.0-flash-exp",
    provider="gemini",
    api_key=os.environ["GEMINI_API_KEY"],
    instructions=[
        "Génère des descriptions d'offres d'emploi professionnelles et attrayantes",
        "Utilise un ton engageant mais professionnel",
        "Structure les informations dans une paragraphe cohérente"
    ],
    temperature=0.7
)

agent1 = Agent(model=model)
def generate_job_description(form_data: dict):
    title = form_data.get("title", "Non spécifié")
    desired_profile = form_data.get("desired_profile", "Non spécifié")
    responsabilities = form_data.get("responsabilities", "Non spécifié")
    criteres = form_data.get("criteres", "Non spécifié")

    prompt = f"""
Tu es un assistant RH spécialisé dans la rédaction d'offres d'emploi.
Ta tâche est de rédiger une description complète, claire et professionnelle à partir des informations fournies.

Informations de base :
- Poste : {title}
- Profil recherché : {desired_profile} 
- Responsabilités principales : {responsabilities}
- Critères d’évaluation : {criteres}

La description doit inclure :
1. **Introduction** : Une accroche engageante qui présente l’entreprise et le poste.  
2. **Missions et Responsabilités** : Détaille clairement les tâches quotidiennes et les objectifs attendus.  
3. **Compétences et Profil Recherché** : Distingue les compétences techniques ("hard skills") et les qualités personnelles ("soft skills").  
4. **Critères et Conditions** : Niveau d’expérience, diplômes, certifications, outils technologiques, langues exigées, etc.  
5. **Valeurs ajoutées** : Les atouts qui différencient ce poste (ex. télétravail, avantages, évolution de carrière, impact social/écologique).  
6. **Ton** : Utilise un style professionnel, attractif et motivant, comme une véritable offre publiée sur LinkedIn.

Enfin, rédige la description sous forme de texte fluide et cohérent, sans puces brutes mais avec des phrases complètes, pour être facilement exploitable par une IA de matching CV ↔ offre.
"""


    return agent1.run(prompt)

#result = generate_job_description(form_data)
#print(result.content)
