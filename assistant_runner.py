from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def run_assistant_message(session, user_input):
    """
    Envia mensagem do usuário para a thread e roda o assistant vinculado.
    """
    # Adiciona mensagem
    client.beta.threads.messages.create(
        thread_id=session["thread_id"],
        role="user",
        content=user_input
    )

    # Executa o assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=session["thread_id"],
        assistant_id=session["assistant_id"],
    )

    # Recupera mensagens
    messages = client.beta.threads.messages.list(
        thread_id=session["thread_id"]
    )

    # Pega a última resposta do assistant
    answer = None
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            answer = msg.content[0].text.value
            break

    return answer
