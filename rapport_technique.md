# Rapport Technique — ClinicalFlow AI

## 1. Introduction

ClinicalFlow AI est un système multi-agents d'orientation clinique préliminaire développé dans le cadre d'un projet académique. Il simule un workflow médical structuré en utilisant LangGraph pour l'orchestration des agents, FastAPI pour l'exposition des services, MCP pour l'intégration des outils, et Streamlit pour l'interface utilisateur.

> ⚠️ Ce système est un exercice académique et ne remplace pas une consultation médicale professionnelle.

---

## 2. Architecture générale

### 2.1 Vue d'ensemble

Le système suit une architecture en couches :

```
Frontend (Streamlit)
        ↕ HTTP
API Layer (FastAPI)
        ↕ Python
Orchestration (LangGraph)
        ↕
Agents (Supervisor / DiagnosticAgent / PhysicianReview / ReportAgent)
        ↕
LLM (Ollama / tinyllama)
        ↕
MCP Server (FastMCP)
```

### 2.2 État partagé (MedicalState)

L'état partagé est le cœur du système. Chaque agent lit et écrit dans cet état :

```python
class MedicalState(TypedDict, total=False):
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]
    question_count: int
    patient_answers: List[str]
    current_question: str
    interim_care: str
    diagnostic_summary: str
    physician_treatment: str
    final_report: str
```

**Choix technique :** Nous avons supprimé le champ `messages: Annotated[list, add_messages]` après avoir constaté des conflits internes dans le channel LangGraph avec `add_messages`. L'état est géré via des champs explicites, ce qui simplifie le débogage et évite les boucles infinies.

---

## 3. LangGraph — Conception du graphe

### 3.1 Structure du graphe

```
supervisor ──► diagnostic_agent ──► supervisor
supervisor ──► physician_review ──► supervisor  
supervisor ──► report_agent ──► supervisor
supervisor ──► END
```

### 3.2 Mécanisme d'interruption (Human-in-the-Loop)

Deux types d'interruptions sont utilisés :

- `interrupt_after=["diagnostic_agent"]` : le graphe s'arrête après chaque question posée, attendant la réponse du patient
- `interrupt_before=["physician_review"]` : le graphe s'arrête avant la revue médecin, attendant la validation

Ce mécanisme est essentiel pour permettre l'interaction humaine sans bloquer le serveur.

### 3.3 Persistance avec MemorySaver

```python
memory = MemorySaver()
graph = builder.compile(
    checkpointer=memory,
    interrupt_after=["diagnostic_agent"],
    interrupt_before=["physician_review"]
)
```

Chaque consultation est identifiée par un `thread_id` unique, permettant de reprendre une consultation interrompue.

### 3.4 Problèmes rencontrés et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| `GraphRecursionError` | Boucle infinie supervisor ↔ diagnostic_agent | Ajout de `interrupt_after` sur diagnostic_agent |
| `add_messages` conflict | Channel LangGraph incompatible | Suppression de `messages`, utilisation de `current_question` |
| RAM insuffisante | Modèle trop lourd (llama3.2 = 2GB) | Migration vers tinyllama (600MB) avec `num_ctx=512` |

---

## 4. Agents

### 4.1 Supervisor

Agent de routage pur — ne fait aucun appel LLM. Décide du prochain nœud selon l'état :

```python
def supervisor_node(state):
    if state.get("final_report"):       return {"next": "FINISH"}
    if state.get("physician_treatment"): return {"next": "report_agent"}
    if state.get("diagnostic_summary"): return {"next": "physician_review"}
    return {"next": "diagnostic_agent"}
```

**Avantage :** logique déterministe, pas de consommation LLM, transitions prévisibles.

### 4.2 DiagnosticAgent

Gère deux responsabilités selon le nombre de réponses :
- Si `len(answers) < 5` → retourne la question suivante (pas d'appel LLM)
- Si `len(answers) == 5` → appelle le LLM pour générer la synthèse

**Choix technique :** Les questions sont codées en dur (liste Python) plutôt que générées par LLM, garantissant une cohérence et économisant des ressources.

### 4.3 PhysicianReview (Human-in-the-Loop)

Nœud passif — retourne l'état inchangé. L'interruption est gérée par LangGraph via `interrupt_before`. Le médecin soumet son traitement via l'API `/consultation/resume`.

### 4.4 ReportAgent

Génère le rapport final en assemblant les données de l'état. Dans la version actuelle (tinyllama), le rapport est généré par template pour garantir la structure et éviter les hallucinations du petit modèle.

---

## 5. API FastAPI

### 5.1 Endpoints implémentés

| Endpoint | Rôle |
|----------|------|
| `POST /consultation/start` | Initialise l'état, lance le graphe, retourne Q1 |
| `POST /consultation/answer` | Injecte la réponse, reprend le graphe |
| `POST /consultation/resume` | Injecte le traitement médecin, génère le rapport |
| `GET /consultation/{id}` | Retourne l'état complet |
| `GET /consultation/{id}/report` | Retourne le rapport final |

### 5.2 Gestion de l'état entre requêtes

Chaque requête utilise le même `thread_id` pour récupérer l'état persisté dans `MemorySaver`. Le pattern est :

```
1. graph.update_state(config, nouvelles_données)
2. graph.invoke(None, config)  # reprendre depuis l'interruption
3. graph.get_state(config).values  # lire le nouvel état
```

---

## 6. Intégration MCP

Le serveur MCP (Model Context Protocol) expose 3 outils via FastMCP :

- `get_patient_question(index)` — accès aux questions standardisées
- `generate_interim_care(symptoms)` — recommandation intermédiaire
- `evaluate_severity(symptoms, temperature)` — évaluation du niveau de gravité (bénin / modéré / urgent)

Le serveur tourne en mode `stdio`, connecté au backend via subprocess.

---

## 7. Frontend Streamlit

### 7.1 Navigation par état

L'interface utilise `st.session_state` pour naviguer entre 4 écrans :

```
start → questions → physician → report
```

### 7.2 Écrans implémentés

- **Écran 1** : saisie du cas initial avec `st.text_area`
- **Écran 2** : questions successives avec barre de progression `st.progress`
- **Écran 3** : synthèse clinique + formulaire médecin avec `st.expander`
- **Écran 4** : rapport final avec `st.markdown` + bouton nouvelle consultation

---

## 8. Choix technologiques

### Pourquoi LangGraph ?
LangGraph permet de modéliser des workflows complexes avec état partagé, interruptions humaines, et cycles conditionnels — impossible avec une simple chaîne LangChain.

### Pourquoi Ollama ?
Solution locale, sans coût d'API, fonctionnant hors-ligne. Adapté aux contraintes d'un projet académique sur machine personnelle.

### Pourquoi Streamlit ?
Rapidité de développement pour un prototype académique. Interface fonctionnelle en moins de 100 lignes de code Python.

### Pourquoi FastMCP ?
Implémentation Python simple du protocole MCP, compatible avec l'écosystème LangChain/LangGraph.

---

## 9. Limitations et améliorations possibles

| Limitation | Amélioration possible |
|------------|----------------------|
| tinyllama produit des réponses en anglais | Utiliser llama3.1:8b ou mistral sur machine plus puissante |
| MemorySaver (RAM) | Remplacer par SQLiteSaver pour la persistance |
| Une seule consultation à la fois | Ajouter une base de données et historique |
| Pas d'authentification | Ajouter JWT pour sécuriser l'API |
| Rapport en template | Générer avec LLM sur modèle plus capable |

---

## 10. Conclusion

Le système ClinicalFlow AI démontre avec succès l'utilisation de LangGraph pour orchestrer un workflow médical multi-agents avec Human-in-the-Loop. Les objectifs pédagogiques sont atteints :

- ✅ Workflow multi-agents avec LangGraph
- ✅ État partagé entre agents  
- ✅ Human-in-the-Loop (patient + médecin)
- ✅ API FastAPI exposant le graphe
- ✅ Intégration MCP
- ✅ Frontend Streamlit fonctionnel
- ✅ Testable dans LangGraph Studio

Le système respecte le cadre éthique du projet : aucun diagnostic définitif n'est posé, le médecin valide obligatoirement avant le rapport final, et chaque sortie mentionne explicitement les limites du système.
