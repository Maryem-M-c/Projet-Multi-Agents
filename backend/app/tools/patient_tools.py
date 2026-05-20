from langchain_core.tools import tool

QUESTIONS = [
    "Quels sont vos symptômes principaux ?",
    "Depuis combien de temps avez-vous ces symptômes ?",
    "Avez-vous de la fièvre ou des frissons ?",
    "Avez-vous des antécédents médicaux importants ?",
    "Prenez-vous des médicaments actuellement ?"
]

@tool
def ask_patient(question_index: int) -> str:
    """Retourne la question à poser au patient selon l'index (0 à 4)."""
    if 0 <= question_index < len(QUESTIONS):
        return QUESTIONS[question_index]
    return "Toutes les questions ont été posées."