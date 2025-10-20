# test_matching.py
from pydantic import BaseModel
from typing import Optional,List
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector, SearchType
from agno.knowledge.embedder.google import GeminiEmbedder
from datetime import date
from pydantic import BaseModel
from typing import Optional
from agno.agent import Agent
from agno.models.google import Gemini
import os
from typing import Optional, List
from pydantic import BaseModel, Field

class CandidateStrength(BaseModel):
    strength: str

class CandidateAreaForImprovement(BaseModel):
    area_for_improvement: str

class PersonalInformation(BaseModel):
    summary: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None

class Education(BaseModel):
    degree: str
    institution: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = None

class WorkExperience(BaseModel):
    job_title: str
    company_name: str
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    responsibilities: Optional[str] = None
    achievements: Optional[str] = None

class Certification(BaseModel):
    certification_name: str
    institution: str
    date_earned: Optional[date] = None

class Language(BaseModel):
    language: str
    proficiency: Optional[str] = None

class Project(BaseModel):
    project_name: str
    description: Optional[str] = None
    dates: Optional[str] = None
    role: Optional[str] = None

class AwardAndHonor(BaseModel):
    award_name: str
    institution: Optional[str] = None
    date_awarded: Optional[date] = None

class VolunteerWork(BaseModel):
    role: str
    organization: Optional[str] = None
    dates: Optional[str] = None
    description: Optional[str] = None


class CVCandidate(BaseModel):
    match_score: Optional[int] = Field(
        None, description="Score global de correspondance du candidat avec l'offre (0-100)."
    )
    skills_match: Optional[int] = Field(
        None, description="Score de correspondance basé sur les compétences techniques (0-100)."
    )
    experience_match: Optional[int] = Field(
        None, description="Score de correspondance basé sur l'expérience professionnelle (0-100)."
    )
    cultural_fit_feedback: Optional[str] = Field(
        None, description="Commentaires sur la compatibilité culturelle du candidat avec l'entreprise."
    )
    overall_feedback: Optional[str] = Field(
        None, description="Évaluation générale et synthèse du profil du candidat."
    )
    strengths: Optional[List[str]] = Field(
        None, description="Liste des points forts identifiés dans le profil du candidat."
    )
    weaknesses: Optional[List[str]] = Field(
        None, description="Liste des points faibles ou des aspects à améliorer."
    )
    recommendation: Optional[str] = Field(
        None, description="Recommandation finale : 'ACCEPTER', 'À CONSIDÉRER' ou 'REFUSER'."
    )
    decision_reasoning: Optional[str] = Field(
        None, description="Raisonnement ou justification de la recommandation donnée."
    )
 



def convert_candidate_data_to_text(
    personal_info: PersonalInformation,
    education_list: List[Education],
    work_experience_list: List[WorkExperience],
    certifications_list: List[Certification],
    languages_list: List[Language],
    projects_list: List[Project],
    awards_list: List[AwardAndHonor],
    volunteer_work_list: List[VolunteerWork],
    strengths_list: List[CandidateStrength],
    improvements_list: List[CandidateAreaForImprovement],
) -> str:
    
    sections = []

    # --- Infos perso ---
    sections.append(f"""
INFORMATIONS PERSONNELLES:
Résumé: {personal_info.summary or 'Non spécifié'}
Téléphone: {personal_info.phone or 'Non spécifié'}
Adresse: {personal_info.address or 'Non spécifié'}
LinkedIn: {personal_info.linkedin or 'Non spécifié'}
""")

    # --- Formation ---
    sections.append("FORMATION:\n" + "\n".join([
        f"- {edu.degree} à {edu.institution} ({edu.location or 'Lieu non spécifié'})\n"
        f"  Période: {edu.start_date or 'Non spécifié'} - {edu.end_date or 'Non spécifié'}"
        for edu in education_list
    ]) if education_list else "- Aucune formation spécifiée")

    # --- Expériences ---
    sections.append("EXPÉRIENCE PROFESSIONNELLE:\n" + "\n".join([
        f"- {work.job_title} chez {work.company_name} ({work.location or 'Lieu non spécifié'})\n"
        f"  Période: {work.start_date or 'Non spécifié'} - {work.end_date or 'Non spécifié'}\n"
        f"  Responsabilités: {work.responsibilities or 'Non spécifié'}\n"
        f"  Réalisations: {work.achievements or 'Non spécifié'}"
        for work in work_experience_list
    ]) if work_experience_list else "- Aucune expérience spécifiée")

    # --- Certifications ---
    sections.append("CERTIFICATIONS:\n" + "\n".join([
        f"- {cert.certification_name} de {cert.institution} ({cert.date_earned or 'Date non spécifiée'})"
        for cert in certifications_list
    ]) if certifications_list else "- Aucune certification spécifiée")

    # --- Langues ---
    sections.append("LANGUES:\n" + "\n".join([
        f"- {lang.language}: {lang.proficiency or 'Niveau non spécifié'}"
        for lang in languages_list
    ]) if languages_list else "- Aucune langue spécifiée")

    # --- Projets ---
    sections.append("PROJETS:\n" + "\n".join([
        f"- {project.project_name}: {project.description or 'Description non spécifiée'}\n"
        f"  Rôle: {project.role or 'Non spécifié'} | Dates: {project.dates or 'Non spécifiées'}"
        for project in projects_list
    ]) if projects_list else "- Aucun projet spécifié")

    # --- Récompenses ---
    sections.append("RÉCOMPENSES ET DISTINCTIONS:\n" + "\n".join([
        f"- {award.award_name} de {award.institution or 'Institution non spécifiée'} ({award.date_awarded or 'Date non spécifiée'})"
        for award in awards_list
    ]) if awards_list else "- Aucune récompense spécifiée")

    # --- Bénévolat ---
    sections.append("TRAVAIL BÉNÉVOLE:\n" + "\n".join([
        f"- {volunteer.role} chez {volunteer.organization or 'Organisation non spécifiée'}\n"
        f"  Dates: {volunteer.dates or 'Non spécifiées'} | Description: {volunteer.description or 'Non spécifiée'}"
        for volunteer in volunteer_work_list
    ]) if volunteer_work_list else "- Aucun travail bénévole spécifié")

    # --- Points forts ---
    sections.append("POINTS FORTS:\n" + "\n".join([
        f"- {strength.strength}" for strength in strengths_list
    ]) if strengths_list else "- Non spécifié")

    # --- Axes d'amélioration ---
    sections.append("AXES D'AMÉLIORATION:\n" + "\n".join([
        f"- {improvement.area_for_improvement}" for improvement in improvements_list
    ]) if improvements_list else "- Non spécifié")

    # Joindre proprement toutes les sections
    return "\n\n".join(sections)

# Modèle ML entraîné sur ton dataset historique
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression  # exemple simple
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Supposons que tu as déjà ton dataset pour l'entraînement
# X_train = liste de textes CVs convertis (text_cv) pour entraînement
# y_train = liste de scores globaux correspondants (match_score) pour supervision
vectorizer = TfidfVectorizer()
X_train_vectors = vectorizer.fit_transform(X_train)

model = LinearRegression()
model.fit(X_train_vectors, y_train)

# --- Fonction d'évaluation pour un candidat spécifique ---
def evaluate_candidate(candidate_text: str, job_description: str):
    """
    Évalue un candidat à partir de son texte converti et du modèle entraîné.
    """
    # Convertir texte du candidat en vecteur
    candidate_vector = vectorizer.transform([candidate_text])

    # Score global prédit par le modèle ML
    match_score = int(model.predict(candidate_vector)[0])

    # Score de similarité texte entre CV et job description
    job_vector = vectorizer.transform([job_description])
    text_sim_score = int(cosine_similarity(candidate_vector, job_vector)[0][0]*100)

    # Exemple simple pour skills et experience
    # Ici tu peux utiliser des règles ou un modèle séparé entraîné sur ces features
    skills_score = text_sim_score  # placeholder, ou calcul séparé
    experience_score = text_sim_score  # placeholder

    # Feedback et recommandation basiques
    feedback = f"Score global: {match_score}, Skills: {skills_score}, Expérience: {experience_score}"
    recommendation = "ACCEPTER" if match_score > 85 else "À CONSIDÉRER" if match_score > 60 else "REFUSER"

    return CVCandidate(
        match_score=match_score,
        skills_match=skills_score,
        experience_match=experience_score,
        overall_feedback=feedback,
        recommendation=recommendation
    )
