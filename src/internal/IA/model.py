# prepare_dataset.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import joblib  # pour sauvegarder le vectorizer

# --------------------------
# Charger le dataset
# --------------------------
df = pd.read_csv("data/dataset_cvs_offres_400.csv")

# Vérifier les colonnes importantes
required_columns = ['competences', 'experience', 'education', 'certifications', 'offre_description', 'experience_years', 'job_required_years', 'offre_criteres']
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"La colonne '{col}' est manquante dans le dataset")

# --------------------------
# Combiner les champs du CV en un seul texte
# --------------------------
df['cv_text'] = df.apply(
    lambda row: " ".join([
        str(row['competences']), 
        str(row['experience']), 
        str(row['education']), 
        str(row['certifications'])
    ]), axis=1
)

# --------------------------
# Vectorisation TF-IDF
# --------------------------
vectorizer = TfidfVectorizer(max_features=2000)
cv_vectors = vectorizer.fit_transform(df['cv_text'])
job_vectors = vectorizer.transform(df['offre_description'])

# Sauvegarder le vectorizer pour l'utiliser plus tard
joblib.dump(vectorizer, "vectorizer_tfidf.joblib")

# --------------------------
# Split pour ML (si tu veux entraîner un modèle supervisé)
# --------------------------
# Exemple simple : si tu as un score de matching déjà présent dans le dataset
if 'match_score' in df.columns:
    X_text = df['cv_text'] + " " + df['offre_description']
    y = df['match_score']  # ou une colonne cible binaire/score
    X_train, X_test, y_train, y_test = train_test_split(X_text, y, test_size=0.2, random_state=42)
    print("Dataset prêt pour entraînement ML")
else:
    print("Pas de colonne 'match_score', prêt uniquement pour scoring TF-IDF/cosine similarity")
