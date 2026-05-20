# mcp_server/server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ClinicalFlow MCP Server")

# ── Tool 1 : Questions patient ────────────────────────────────
QUESTIONS = [
    "Quels sont vos symptômes principaux ?",
    "Depuis combien de temps avez-vous ces symptômes ?",
    "Avez-vous de la fièvre ou des frissons ?",
    "Avez-vous des antécédents médicaux importants ?",
    "Prenez-vous des médicaments actuellement ?"
]

@mcp.tool()
def get_patient_question(index: int) -> str:
    """Retourne la question à poser au patient selon l'index (0 à 4)."""
    if 0 <= index < len(QUESTIONS):
        return QUESTIONS[index]
    return "Toutes les questions ont été posées."

# ── Tool 2 : Recommandation intermédiaire ─────────────────────
@mcp.tool()
def generate_interim_care(symptoms: str) -> str:
    """Génère une recommandation de soins intermédiaire prudente."""
    return (
        f"Recommandation intermédiaire basée sur : {symptoms}\n\n"
        "- Repos et hydratation suffisante\n"
        "- Surveiller l'évolution des symptômes\n"
        "- Éviter les efforts physiques\n"
        "- Consulter rapidement si aggravation\n\n"
        "⚠️ Ne remplace pas l'avis d'un médecin."
    )

# ── Tool 3 : Évaluation gravité ───────────────────────────────
@mcp.tool()
def evaluate_severity(symptoms: str, temperature: float = 0.0) -> dict:
    """Évalue le niveau de gravité selon les symptômes."""
    red_flags = [
        "difficulté à respirer", "douleur thoracique",
        "perte de conscience", "convulsion",
        "saignement important", "confusion"
    ]

    symptoms_lower = symptoms.lower()
    has_red_flag = any(flag in symptoms_lower for flag in red_flags)
    high_fever = temperature >= 39.5

    if has_red_flag or high_fever:
        level = "URGENT"
        advice = "Consultation médicale immédiate recommandée."
    elif temperature >= 38.0:
        level = "MODÉRÉ"
        advice = "Consultation dans les 24-48h recommandée."
    else:
        level = "BÉNIN"
        advice = "Surveillance à domicile, consulter si aggravation."

    return {
        "severity": level,
        "advice": advice,
        "red_flags_detected": has_red_flag,
        "high_fever": high_fever,
    }

# ── Resource : Infos système ──────────────────────────────────
@mcp.resource("clinicalflow://info")
def system_info() -> str:
    """Informations sur le système ClinicalFlow."""
    return (
        "ClinicalFlow AI — Système d'orientation clinique préliminaire\n"
        "Version: 1.0.0\n"
        "⚠️ Ce système ne remplace pas une consultation médicale."
    )

if __name__ == "__main__":
    mcp.run(transport="stdio")