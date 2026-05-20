# backend/app/tools/care_tools.py
from langchain_core.tools import tool

@tool
def recommend_interim_care(symptoms: str) -> str:
    """Génère une recommandation de soins intermédiaire prudente."""
    return (
        "Recommandation intermédiaire (non définitive) :\n"
        "- Repos et hydratation suffisante\n"
        "- Surveiller l'évolution des symptômes\n"
        "- Éviter les efforts physiques importants\n"
        "- Consulter rapidement en cas d'aggravation\n\n"
        "⚠️ Cette recommandation ne remplace pas l'avis d'un médecin."
    )