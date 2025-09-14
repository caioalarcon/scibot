import os
import uuid
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_or_create_session(session_name: str = None):
    """
    Cria ou reutiliza uma sessão composta por:
      - vector store (expira após 7 dias inativo)
      - assistant ligado a esse vector store
      - thread para conversas

    Se session_name não for passado, gera um UUID novo.
    """
    if not session_name:
        session_name = str(uuid.uuid4())[:8]

    # cria vector store vazio
    vs = client.vector_stores.create(
        name=f"vs_{session_name}",
        expires_after={"anchor": "last_active_at", "days": 7}
    )

    # cria assistant ligado ao vector store
    asst = client.beta.assistants.create(
        name=f"SciBot_{session_name}",
        model="gpt-4.1",
        instructions=(
            "Você é um assistente científico. "
            "Use apenas os trechos dos arquivos responder perguntas. "
            "Sempre cite trechos literais para embasar cada resposta, de preferência mais de um trecho."
            "Se a resposta não estiver nas fontes, informe isso."
        ),
        tools=[{"type": "file_search"}],
        tool_resources={
            "file_search": {"vector_store_ids": [vs.id]}
        }
    )

    # cria thread vazia
    thread = client.beta.threads.create()

    return {
        "session_name": session_name,
        "vector_store_id": vs.id,
        "assistant_id": asst.id,
        "thread_id": thread.id,
    }
