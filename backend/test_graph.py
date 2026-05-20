# backend/test_graph.py
import uuid
from app.graph import graph

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print(f"=== Thread: {thread_id[:8]} ===\n")

# Étape 1 — démarrage
graph.invoke({
    "patient_answers": [],
    "question_count": 0,
}, config)

state = graph.get_state(config).values
print(f"Question 1 : {state.get('current_question')}\n")

# 5 réponses simulées
reponses = [
    "Toux sèche et fièvre",
    "Depuis 3 jours",
    "Oui, 38.5 degrés",
    "Aucun antécédent",
    "Aucun médicament",
]

for i, reponse in enumerate(reponses):
    print(f"  → Réponse : {reponse}")

    # Injecter la réponse
    current = graph.get_state(config).values
    answers = list(current.get("patient_answers", []))
    answers.append(reponse)
    graph.update_state(config, {"patient_answers": answers})

    # Reprendre le graphe
    graph.invoke(None, config)
    state = graph.get_state(config).values

    # Vérifier si synthèse générée
    if state.get("diagnostic_summary"):
        print(f"\n✅ Synthèse générée !\n")
        print("--- SYNTHÈSE ---")
        print(state["diagnostic_summary"])
        print("\n--- RECOMMANDATION ---")
        print(state["interim_care"])
        print("\n⏸  Attente médecin...")

        # Revue médecin
        graph.update_state(config, {
            "physician_treatment": "Paracétamol 1g/8h, repos 3 jours."
        })
        graph.invoke(None, config)
        final = graph.get_state(config).values

        print("\n✅ RAPPORT FINAL :\n")
        print(final.get("final_report", "(vide)"))
        break

    # Prochaine question
    q = state.get("current_question", "")
    if q:
        print(f"Question {i+2} : {q}\n")