# backend/app/tools/mcp_client.py
import subprocess
import sys
import os

def get_mcp_tools():
    """Retourne les tools MCP sous forme de LangChain tools."""
    from langchain_core.tools import tool

    @tool
    def mcp_get_question(index: int) -> str:
        """Obtient une question patient via MCP."""
        result = subprocess.run(
            [sys.executable, "../../mcp_server/server.py"],
            input=f'{{"tool": "get_patient_question", "index": {index}}}',
            capture_output=True, text=True,
            cwd=os.path.dirname(__file__)
        )
        return result.stdout.strip() or f"Question {index+1}"

    @tool
    def mcp_evaluate_severity(symptoms: str, temperature: float = 37.0) -> str:
        """Évalue la gravité via MCP."""
        import json
        result = subprocess.run(
            [sys.executable,
             os.path.join(os.path.dirname(__file__),
                          "../../../mcp_server/server.py")],
            input=json.dumps({
                "tool": "evaluate_severity",
                "symptoms": symptoms,
                "temperature": temperature
            }),
            capture_output=True, text=True
        )
        return result.stdout.strip()

    return [mcp_get_question, mcp_evaluate_severity]