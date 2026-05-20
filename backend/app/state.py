# backend/app/state.py
from typing import List
from typing_extensions import TypedDict, Literal

class MedicalState(TypedDict, total=False):
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]
    question_count: int
    patient_answers: List[str]
    current_question: str      # remplace messages
    interim_care: str
    diagnostic_summary: str
    physician_treatment: str
    final_report: str