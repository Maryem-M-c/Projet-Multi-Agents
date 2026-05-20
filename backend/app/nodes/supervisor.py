# backend/app/nodes/supervisor.py
from app.state import MedicalState

def supervisor_node(state: MedicalState) -> MedicalState:
    # Rapport généré → fin
    if state.get("final_report"):
        return {**state, "next": "FINISH"}
    
    # Médecin a validé → rapport
    if state.get("physician_treatment"):
        return {**state, "next": "report_agent"}
    
    # Synthèse prête → médecin
    if state.get("diagnostic_summary"):
        return {**state, "next": "physician_review"}
    
    # Pas encore 5 réponses → diagnostic agent
    answers = state.get("patient_answers", [])
    if len(answers) < 5:
        return {**state, "next": "diagnostic_agent"}
    
    # 5 réponses mais pas encore de synthèse → diagnostic agent pour générer
    return {**state, "next": "diagnostic_agent"}