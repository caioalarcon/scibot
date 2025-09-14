# assistant_runner.py
from openai_manager import get_client

client = get_client()

def run_assistant_message(session, user_input):
    """
    Envia mensagem do usuário para a thread e roda o assistant vinculado.
    O prompt já foi definido no momento da criação do assistant (session_manager).
    """
    # Adiciona mensagem do usuário na thread
    client.beta.threads.messages.create(
        thread_id=session["thread_id"],
        role="user",
        content=user_input
    )

    # Executa o assistant já criado na sessão
    run = client.beta.threads.runs.create_and_poll(
        thread_id=session["thread_id"],
        assistant_id=session["assistant_id"]
    )

    # Recupera mensagens
    messages = client.beta.threads.messages.list(thread_id=session["thread_id"])

    # Pega a última resposta do assistant
    answer = None
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            answer = msg.content[0].text.value
            break

    return answer
