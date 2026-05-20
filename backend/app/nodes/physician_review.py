from app.state import MedicalState

def physician_review_node(state: MedicalState) -> MedicalState:
    # Nœud interrompu automatiquement par LangGraph (interrupt_before)
    # Le médecin soumet son traitement via POST /consultation/resume
    return state