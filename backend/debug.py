# backend/debug.py
print("Test 1 : imports...")
from app.state import MedicalState
print("OK - state")

from app.nodes.supervisor import supervisor_node
print("OK - supervisor")

from app.nodes.diagnostic_agent import diagnostic_agent_node
print("OK - diagnostic_agent")

print("\nTest 2 : supervisor direct...")
state = {
    "messages": [],
    "patient_answers": [],
    "question_count": 0,
}
result = supervisor_node(state)
print(f"  next = {result.get('next')}")

print("\nTest 3 : diagnostic_agent direct...")
result2 = diagnostic_agent_node(state)
print(f"  question_count = {result2.get('question_count')}")
messages = result2.get("messages", [])
if messages:
    print(f"  message = {messages[-1].content}")
else:
    print("  (aucun message)")

print("\nTest 4 : LLM direct...")
from app.llm_config import get_llm
from langchain_core.messages import HumanMessage
llm = get_llm()
print("  LLM créé, envoi message...")
response = llm.invoke([HumanMessage(content="Dis bonjour en français.")])
print(f"  Réponse : {response.content}")

print("\n✅ Tous les tests passent !")