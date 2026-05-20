# backend/app/api.py

# backend/app/api.py  — ajoute en haut après les imports
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import graph

app = FastAPI(title="ClinicalFlow AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartRequest(BaseModel):
    patient_case: str

class AnswerRequest(BaseModel):
    thread_id: str
    answer: str

class ResumeRequest(BaseModel):
    thread_id: str
    physician_treatment: str

def get_config(thread_id: str):
    return {"configurable": {"thread_id": thread_id}}

def safe_state(thread_id: str):
    try:
        return graph.get_state(get_config(thread_id)).values
    except Exception:
        raise HTTPException(status_code=404, detail="Session introuvable")

def get_status(state: dict) -> str:
    if state.get("final_report"):
        return "completed"
    if state.get("diagnostic_summary"):
        return "awaiting_physician"
    return "in_progress"

@app.get("/")
def root():
    return {"status": "ok", "message": "ClinicalFlow AI API"}

@app.post("/consultation/start")
def start_consultation(req: StartRequest):
    thread_id = str(uuid.uuid4())
    config = get_config(thread_id)
    try:
        graph.invoke({
            "patient_answers": [req.patient_case],
            "question_count": 0,
        }, config)
        state = graph.get_state(config).values
        return {
            "thread_id": thread_id,
            "question": state.get("current_question", ""),
            "question_number": 1,
            "status": "in_progress",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consultation/answer")
def submit_answer(req: AnswerRequest):
    config = get_config(req.thread_id)
    state = safe_state(req.thread_id)

    # Ajouter la réponse
    answers = list(state.get("patient_answers", []))
    answers.append(req.answer)

    try:
        graph.update_state(config, {"patient_answers": answers})
        graph.invoke(None, config)
        state = graph.get_state(config).values
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur graphe: {str(e)}")

    if state.get("diagnostic_summary"):
        return {
            "status": "awaiting_physician",
            "diagnostic_summary": state.get("diagnostic_summary", ""),
            "interim_care": state.get("interim_care", ""),
            "question_number": len(answers),
        }

    return {
        "status": "question",
        "question": state.get("current_question", ""),
        "question_number": len(answers) + 1,
    }

@app.post("/consultation/resume")
def resume_with_physician(req: ResumeRequest):
    config = get_config(req.thread_id)
    safe_state(req.thread_id)
    try:
        graph.update_state(config, {
            "physician_treatment": req.physician_treatment
        })
        graph.invoke(None, config)
        state = graph.get_state(config).values
        return {
            "status": "completed",
            "final_report": state.get("final_report", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consultation/{thread_id}")
def get_consultation(thread_id: str):
    state = safe_state(thread_id)
    return {
        "thread_id": thread_id,
        "question_count": state.get("question_count", 0),
        "patient_answers": state.get("patient_answers", []),
        "current_question": state.get("current_question", ""),
        "diagnostic_summary": state.get("diagnostic_summary", ""),
        "interim_care": state.get("interim_care", ""),
        "physician_treatment": state.get("physician_treatment", ""),
        "final_report": state.get("final_report", ""),
        "status": get_status(state),
    }

@app.get("/consultation/{thread_id}/report")
def get_report(thread_id: str):
    state = safe_state(thread_id)
    if not state.get("final_report"):
        raise HTTPException(status_code=404, detail="Rapport pas encore généré")
    return {
        "thread_id": thread_id,
        "final_report": state.get("final_report"),
    }

# Dans backend/app/api.py — ajouter à la fin
@app.get("/graph/info")
def graph_info():
    """Info pour LangGraph Studio."""
    return {
        "graphs": {
            "medical_graph": {
                "nodes": ["supervisor", "diagnostic_agent", 
                         "physician_review", "report_agent"],
                "edges": [
                    "supervisor → diagnostic_agent",
                    "supervisor → physician_review", 
                    "supervisor → report_agent",
                    "diagnostic_agent → supervisor",
                    "physician_review → supervisor",
                    "report_agent → supervisor",
                ]
            }
        }
    }