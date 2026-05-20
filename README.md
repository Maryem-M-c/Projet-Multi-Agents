# ClinicalFlow AI — Système d'orientation clinique multi-agents

> ⚠️ Ce système est un exercice académique. Il ne remplace pas une consultation médicale professionnelle.

## Description

ClinicalFlow AI est une application multi-agents basée sur **LangGraph** simulant un workflow d'orientation clinique préliminaire. Le système collecte les informations patient via 5 questions, produit une synthèse clinique, intègre une validation humaine par un médecin traitant, et génère un rapport final structuré.

## Architecture

```
medical-diagnostic/
├── backend/
│   ├── app/
│   │   ├── graph.py              # Graphe LangGraph principal
│   │   ├── state.py              # État partagé MedicalState
│   │   ├── llm_config.py         # Configuration Ollama
│   │   ├── api.py                # API FastAPI
│   │   ├── nodes/
│   │   │   ├── supervisor.py     # Agent orchestrateur
│   │   │   ├── diagnostic_agent.py  # Agent de diagnostic
│   │   │   ├── physician_review.py  # Human-in-the-Loop
│   │   │   └── report_agent.py   # Agent de rapport
│   │   └── tools/
│   │       ├── care_tools.py     # Tool recommandation
│   │       └── mcp_client.py     # Client MCP
│   └── requirements.txt
├── mcp_server/
│   └── server.py                 # Serveur MCP (FastMCP)
├── frontend/
│   └── app.py                    # Interface Streamlit
└── README.md
```

## Technologies utilisées

| Composant | Technologie |
|-----------|-------------|
| Orchestration agents | LangGraph 0.2+ |
| LLM | Ollama (tinyllama / llama3.2) |
| Framework LLM | LangChain |
| API Backend | FastAPI + Uvicorn |
| Protocole outils | MCP (FastMCP) |
| Frontend | Streamlit |
| Langage | Python 3.11 |

## Prérequis

- Python 3.11+
- [Ollama](https://ollama.com) installé et en cours d'exécution
- 2 GB RAM minimum disponible

## Installation

### 1. Cloner le projet
```bash
git clone <repo>
cd medical-diagnostic
```

### 2. Installer les dépendances Python
```bash
pip install -r backend/requirements.txt
pip install streamlit
```

### 3. Installer le modèle Ollama
```bash
# Modèle léger (recommandé si RAM < 4GB)
ollama pull tinyllama

# Modèle de meilleure qualité (recommandé si RAM >= 6GB)
ollama pull llama3.2
```

### 4. Configurer l'environnement
Créer `backend/.env` :
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
```

## Lancement

Ouvrir **3 terminaux** :

```bash
# Terminal 1 — API Backend
cd backend
uvicorn app.api:app --reload --port 8000

# Terminal 2 — Serveur MCP
cd mcp_server
python server.py

# Terminal 3 — Frontend
cd frontend
streamlit run app.py
```

- API : http://localhost:8000
- Documentation API : http://localhost:8000/docs
- Frontend : http://localhost:8501

## Workflow du système

```
START
  └─► Supervisor
        └─► DiagnosticAgent (5 questions successives)
              ├─► Tool: ask_patient (questions 1 à 5)
              └─► Tool: recommend_interim_care
        └─► Supervisor
        └─► PhysicianReview ⏸ (Human-in-the-Loop)
        └─► Supervisor
        └─► ReportAgent
        └─► Supervisor
END
```

## Agents

### Supervisor
Orchestre le workflow. Décide du prochain nœud selon l'état partagé :
- Pas de synthèse → `diagnostic_agent`
- Synthèse prête → `physician_review` (interruption)
- Médecin validé → `report_agent`
- Rapport généré → `FINISH`

### DiagnosticAgent
- Pose 5 questions successives au patient
- Génère une synthèse clinique préliminaire via LLM
- Produit une recommandation intermédiaire

### PhysicianReview (Human-in-the-Loop)
- Interruption du graphe via `interrupt_before`
- Le médecin soumet son traitement via `POST /consultation/resume`

### ReportAgent
- Génère le rapport final structuré
- Intègre synthèse + recommandation + traitement médecin

## API Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/consultation/start` | Démarrer une consultation |
| POST | `/consultation/answer` | Soumettre une réponse patient |
| POST | `/consultation/resume` | Validation médecin |
| GET | `/consultation/{thread_id}` | État de la consultation |
| GET | `/consultation/{thread_id}/report` | Rapport final |

## Intégration MCP

Le serveur MCP expose 3 outils :
- `get_patient_question(index)` — questions patient
- `generate_interim_care(symptoms)` — recommandation intermédiaire
- `evaluate_severity(symptoms, temperature)` — évaluation de gravité

## Jeux de tests

### Cas 1 — Syndrome respiratoire simple
- Symptômes : toux sèche, fièvre 38°C
- Durée : 3 jours
- Résultat attendu : orientation vers repos + hydratation

### Cas 2 — Red flags
- Symptômes : douleur thoracique, difficulté à respirer
- Résultat attendu : consultation immédiate recommandée

### Cas 3 — Cas bénin
- Symptômes : légère fatigue, nez qui coule
- Résultat attendu : surveillance à domicile

## Écrans de l'interface

1. **Écran 1** — Saisie du cas patient initial
2. **Écran 2** — Questions/réponses (5 questions avec barre de progression)
3. **Écran 3** — Revue médecin (synthèse + recommandation + saisie traitement)
4. **Écran 4** — Rapport final structuré

## Contraintes éthiques

- Le système ne pose pas de diagnostic définitif
- Tous les rapports mentionnent explicitement la limite du système
- Les termes utilisés : "orientation clinique préliminaire", "synthèse clinique"
- Le médecin traitant valide obligatoirement avant le rapport final

## Auteurs

Projet académique — Pr. Mohamed YOUSSFI  
Système multi-agents médical avec LangGraph
