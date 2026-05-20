# backend/app/nodes/report_agent.py
from app.state import MedicalState

def report_agent_node(state: MedicalState) -> MedicalState:
    summary = state.get("diagnostic_summary", "Non disponible")
    interim = state.get("interim_care", "Non disponible")
    treatment = state.get("physician_treatment", "Non disponible")
    answers = state.get("patient_answers", [])

    QUESTIONS = [
        "Symptômes principaux",
        "Durée des symptômes",
        "Fièvre ou frissons",
        "Antécédents médicaux",
        "Médicaments actuels"
    ]

    qa_section = "\n".join([
        f"- {QUESTIONS[i]} : {answers[i]}"
        for i in range(min(5, len(answers)))
    ])

    report = f"""# Rapport d'orientation clinique

## 1. Informations patient
{qa_section}

## 2. Synthèse clinique préliminaire
{summary}

## 3. Recommandation intermédiaire
{interim}

## 4. Traitement proposé par le médecin traitant
{treatment}

## 5. Conclusion
Ce rapport a été généré suite à une consultation guidée de 5 questions,
une synthèse clinique préliminaire et une validation par le médecin traitant.

⚠️ Ce système ne remplace pas une consultation médicale professionnelle.
"""

    return {**state, "final_report": report}