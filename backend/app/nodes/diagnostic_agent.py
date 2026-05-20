# backend/app/nodes/diagnostic_agent.py
from langchain_core.messages import HumanMessage
from app.state import MedicalState
from app.llm_config import get_llm

QUESTIONS = [
    "Quels sont vos symptômes principaux ?",
    "Depuis combien de temps avez-vous ces symptômes ?",
    "Avez-vous de la fièvre ou des frissons ?",
    "Avez-vous des antécédents médicaux importants ?",
    "Prenez-vous des médicaments actuellement ?"
]

INTERIM_CARE = (
    "Recommandation intermédiaire (non définitive) :\n"
    "- Repos et hydratation suffisante\n"
    "- Surveiller l'évolution des symptômes\n"
    "- Éviter les efforts physiques importants\n"
    "- Consulter rapidement en cas d'aggravation\n"
    "⚠️ Cette recommandation ne remplace pas l'avis d'un médecin."
)

def diagnostic_agent_node(state: MedicalState) -> MedicalState:
    answers = state.get("patient_answers", [])
    q_count = len(answers)

    # Encore des questions à poser
    if q_count < 5:
        question = QUESTIONS[q_count]
        return {
            **state,
            "question_count": q_count + 1,
            "current_question": question,
        }

    # 5 réponses → synthèse avec LLM local
    llm = get_llm()
    answers_text = "\n".join(
        [f"Q{i+1}: {QUESTIONS[i]} => {answers[i]}" for i in range(5)]
    )

    prompt = f"""Patient info:
{answers_text}

Write 3 short sentences in French summarizing the clinical orientation.
Do not diagnose. Use "orientation clinique préliminaire"."""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        summary = response.content
    except Exception:
        summary = f"Orientation clinique préliminaire basée sur : {answers_text}"

    return {
        **state,
        "question_count": 5,
        "current_question": "",
        "diagnostic_summary": summary,
        "interim_care": INTERIM_CARE,
    }