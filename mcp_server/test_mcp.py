# mcp_server/test_mcp.py
# Test direct des fonctions sans passer par le protocole MCP
import sys
sys.path.insert(0, '.')

from server import mcp

print("=== Test MCP Tools ===\n")

# Simuler les appels directs aux fonctions
# Test 1 : get_patient_question
from server import get_patient_question
for i in range(5):
    result = get_patient_question(i)
    print(f"Question {i} : {result}")

print()

# Test 2 : generate_interim_care
from server import generate_interim_care
result = generate_interim_care("toux sèche, fièvre 38.5°C")
print("Interim care :", result)

print()

# Test 3 : evaluate_severity
from server import evaluate_severity
result = evaluate_severity("toux sèche et fièvre", 38.5)
print("Sévérité :", result)

print("\n✅ MCP tools fonctionnent !")