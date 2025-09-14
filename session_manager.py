# session_manager.py
import os
import uuid
from openai_manager import get_client, get_prompt

client = get_client()

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

    # pega prompt do .env
    assistant_prompt = get_prompt("PROMPT_ASSISTANT")

    # cria assistant ligado ao vector store
    asst = client.beta.assistants.create(
        name=f"SciBot_{session_name}",
        model="gpt-4.1",
        instructions=assistant_prompt,
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vs.id]}}
    )

    # cria thread vazia
    thread = client.beta.threads.create()

    return {
        "session_name": session_name,
        "vector_store_id": vs.id,
        "assistant_id": asst.id,
        "thread_id": thread.id,
    }
