
from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.vectordb.pgvector import PgVector, SearchType
from agno.db.postgres import PostgresDb
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.agent import Agent
from ...utils.llmlite import switch_model
import os

# --- Pydantic schemas (unchanged) ---
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

class CVVersion(BaseModel):
    strengths: Optional[List[CandidateStrength]] = []
    areas_for_improvement: Optional[List[CandidateAreaForImprovement]] = []
    personal_information: Optional[PersonalInformation] = None
    education: Optional[List[Education]] = []
    work_experience: Optional[List[WorkExperience]] = []
    certifications: Optional[List[Certification]] = []
    languages: Optional[List[Language]] = []
    projects: Optional[List[Project]] = []
    awards_and_honors: Optional[List[AwardAndHonor]] = []
    volunteer_work: Optional[List[VolunteerWork]] = []

#DB_URL = "postgresql://postgres:ikram@localhost/recruitement_db"
#os.environ["GEMINI_API_KEY"] = "AIzaSyDhsQrPwZNfW5MlMa1cPAiasWYS7AoA7Us"

#CV_PATH = "C:/Users/Asus/Desktop/cv-developpeur-web.pdf"

# Step 1: init models, embedder, vector DB, reader, knowledge
def init_services() -> Dict[str, Any]:
    model = switch_model(
        id="gemini-2.0-flash-exp",
        provider="gemini",
        api_key=os.environ["GEMINI_API_KEY"],
        instructions=["analyse cv en details"],
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
    

    pdf_reader = PDFReader(
        name="CV Experience Extractor",
        chunking_strategy=SemanticChunking(similarity_threshold=0.5, embedder=GeminiEmbedder(dimensions=1536), chunk_size=1200),
        split_on_pages=True, 
    )

    knowledge = Knowledge(
        vector_db=vector_db,
        contents_db=contents_db
    )

    return {
        "model": model,
        "embedder": embedder,
        "vector_db": vector_db,
        "contents_db": contents_db,
        "pdf_reader": pdf_reader,
        "knowledge": knowledge
    }

# Helper: extract text from PDF using the project's PDFReader (robust)
def extract_text_from_pdf(pdf_path: str, pdf_reader: PDFReader) -> tuple[str, List[Any]]:
    docs = pdf_reader.read(pdf_path)
    full_cv_txt = ""
    for doc in docs:
        full_cv_txt += doc.content
        
    return full_cv_txt, docs

# Step 2: ask model for structured JSON and parse into Candidate
def extract_candidate_structured(cv_text: str) -> CVVersion:
    
    model = switch_model(
        id="gemini-2.0-flash-exp",
        provider="gemini",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.7
    )

    agent = Agent(
        model=model,
        description="Extract candidate information from CV text",
        output_schema=CVVersion,
        instructions=[
            "Extract all relevant candidate information from the CV and map it precisely to the provided schema.",
            "Search deeply in the CV: consider headers, footers, contact sections, and context clues.",
            "For location fields (education, work experience, projects, etc.), extract city and country if present, "
            "or infer from institution/company name if mentioned (but never invent information that does not exist).",
            "Fill in each field whenever possible; leave fields null only if no information is explicitly available.",
            "Normalize all dates to ISO format (YYYY-MM-DD). If only month/year are provided, default to the first day of the month.",
            "For phone numbers, include international country code if available.",
            "For LinkedIn or other URLs, return full valid URLs.",
            "Be thorough: extract all education entries, work experiences, skills, projects, certifications, languages, awards, and volunteer work.",
            "Maintain fidelity: copy responsibilities, achievements, and descriptions as written, without altering meaning.",
            "If multiple entries exist (e.g., several jobs or degrees), include them all in chronological order where possible.",
            "Avoid hallucinations: never generate information not present in the CV, but prefer partial/approximate extraction over null values (e.g., capture institution name even if exact dates are missing).",
            "Ensure consistency in formatting (names, institutions, job titles).",
            "Return data strictly in the format defined by the Candidate schema."
        ]
    )
    
    response = agent.run(f"Extract candidate information from this CV:\n\n{cv_text}")
    return response.content  # Already a Candidate object    
    

# Step 3: ingest structured candidate into knowledge base
def ingest_candidate_into_kb(candidate: CVVersion, knowledge: Knowledge, docs,candidate_id: int):
    try:
        # Use add_content for each document individually (synchronous)
        for i, doc in enumerate(docs):
            knowledge.add_content(
                name=f"candidate_doc_{i}",
                text_content=doc.content,  # Use text_content parameter
                metadata={
                    "document_type": "candidate_cv",
                    "document_index": i,
                    "candidate_id": candidate_id, 
                }
            )
        print(f"Successfully ingested {len(docs)} documents for candidate")
    except Exception as e:
        raise RuntimeError(f"Unable to ingest candidate documents: {str(e)}")
    
'''def main():
    services = init_services()
    pdf_reader = services["pdf_reader"]
    knowledge = services["knowledge"]

    # Step A: extract raw text from PDF
    cv_text, docs = extract_text_from_pdf(CV_PATH, pdf_reader)

    # Step B: structured extraction
    candidate = extract_candidate_structured(cv_text)
    print("Extracted Candidate (summary):", candidate.model_dump())
    print(docs)
    # Step C: ingest structured candidate
    ingest_candidate_into_kb(candidate, knowledge, docs=docs)
    # print("Ingested structured CV into knowledge base.")

if __name__ == "__main__":
    main()
'''
def analyze_cv(file_path: str,candidate_id: int) -> CVVersion:
    print("Analyse CV démarrée pour:", file_path)
    services = init_services()
    pdf_reader = services["pdf_reader"]
    knowledge = services["knowledge"]

    # 1️⃣ Extraire texte du PDF
    cv_text, docs = extract_text_from_pdf(file_path, pdf_reader)

    # 2️⃣ Extraction structurée (vers Candidate)
    candidate = extract_candidate_structured(cv_text)

    # 3️⃣ Ingestion dans Knowledge base
    ingest_candidate_into_kb(candidate, knowledge, docs=docs,candidate_id=candidate_id)
    print("Analyse CV terminé pou")

    return candidate