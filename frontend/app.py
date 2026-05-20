# frontend/app.py
import streamlit as st
import requests

API = "http://localhost:8000"

# ── Config page ───────────────────────────────────────────────
st.set_page_config(
    page_title="ClinicalFlow AI",
    page_icon="🏥",
    layout="centered"
)

st.title("🏥 ClinicalFlow AI")
st.caption("⚠️ Ce système ne remplace pas une consultation médicale professionnelle.")
st.divider()

# ── Init session ──────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = "start"
    st.session_state.thread_id = None
    st.session_state.question = ""
    st.session_state.question_num = 1
    st.session_state.summary = ""
    st.session_state.interim = ""

# ════════════════════════════════════════════════════════════
# ÉCRAN 1 — Saisie du cas patient
# ════════════════════════════════════════════════════════════
if st.session_state.step == "start":
    st.subheader("📋 Étape 1 — Description du cas patient")
    case = st.text_area(
        "Décrivez brièvement votre problème de santé :",
        placeholder="Ex: J'ai de la toux et de la fièvre depuis quelques jours...",
        height=120
    )
    if st.button("🚀 Démarrer la consultation", type="primary"):
        if not case.strip():
            st.warning("Veuillez décrire votre cas patient.")
        else:
            with st.spinner("Démarrage..."):
                r = requests.post(f"{API}/consultation/start",
                                  json={"patient_case": case})
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.thread_id = data["thread_id"]
                    st.session_state.question = data["question"]
                    st.session_state.question_num = 2
                    st.session_state.step = "questions"
                    st.rerun()
                else:
                    st.error(f"Erreur API : {r.text}")

# ════════════════════════════════════════════════════════════
# ÉCRAN 2 — Questions / Réponses
# ════════════════════════════════════════════════════════════
elif st.session_state.step == "questions":
    st.subheader("💬 Étape 2 — Questions du diagnostic")

    # Barre de progression
    progress = (st.session_state.question_num - 1) / 5
    st.progress(progress, text=f"Question {st.session_state.question_num - 1} / 5")

    st.info(f"**{st.session_state.question}**")

    answer = st.text_input(
        "Votre réponse :",
        key=f"answer_{st.session_state.question_num}",
        placeholder="Tapez votre réponse ici..."
    )

    if st.button("➡️ Envoyer", type="primary"):
        if not answer.strip():
            st.warning("Veuillez entrer une réponse.")
        else:
            with st.spinner("Analyse en cours..."):
                r = requests.post(f"{API}/consultation/answer", json={
                    "thread_id": st.session_state.thread_id,
                    "answer": answer
                })
                if r.status_code == 200:
                    data = r.json()
                    if data["status"] == "awaiting_physician":
                        st.session_state.summary = data["diagnostic_summary"]
                        st.session_state.interim = data["interim_care"]
                        st.session_state.step = "physician"
                        st.rerun()
                    else:
                        st.session_state.question = data["question"]
                        st.session_state.question_num += 1
                        st.rerun()
                else:
                    st.error(f"Erreur : {r.text}")

# ════════════════════════════════════════════════════════════
# ÉCRAN 3 — Revue médecin
# ════════════════════════════════════════════════════════════
elif st.session_state.step == "physician":
    st.subheader("👨‍⚕️ Étape 3 — Revue du médecin traitant")

    with st.expander("📊 Synthèse clinique préliminaire", expanded=True):
        st.write(st.session_state.summary)

    with st.expander("💊 Recommandation intermédiaire", expanded=True):
        st.write(st.session_state.interim)

    st.divider()
    st.markdown("**👨‍⚕️ Médecin traitant — veuillez saisir votre traitement :**")
    treatment = st.text_area(
        "Traitement ou conduite à tenir :",
        placeholder="Ex: Paracétamol 1g toutes les 8h, repos 3 jours...",
        height=100
    )

    if st.button("✅ Valider et générer le rapport", type="primary"):
        if not treatment.strip():
            st.warning("Veuillez saisir le traitement.")
        else:
            with st.spinner("Génération du rapport final..."):
                r = requests.post(f"{API}/consultation/resume", json={
                    "thread_id": st.session_state.thread_id,
                    "physician_treatment": treatment
                })
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.report = data["final_report"]
                    st.session_state.step = "report"
                    st.rerun()
                else:
                    st.error(f"Erreur : {r.text}")

# ════════════════════════════════════════════════════════════
# ÉCRAN 4 — Rapport final
# ════════════════════════════════════════════════════════════
elif st.session_state.step == "report":
    st.subheader("📄 Étape 4 — Rapport final")
    st.success("✅ Consultation terminée !")

    st.markdown(st.session_state.get("report", ""))

    st.divider()
    st.warning("⚠️ Ce système ne remplace pas une consultation médicale professionnelle.")

    if st.button("🔄 Nouvelle consultation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()