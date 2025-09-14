import streamlit as st
import os
from openai import OpenAI

# Configuração
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ID real do assistant
ASSISTANT_ID = "asst_p0BqoG3q2co3G18GyYUDh7bg"

st.set_page_config(page_title="Assistente Científico", layout="wide")
st.title("🔬 Assistente Científico com PDFs")

# Inicializa thread e histórico
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.history = []

# Input do usuário
user_input = st.text_input("Digite sua pergunta:")

if user_input:
    # adiciona a mensagem do usuário na thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    # executa o assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID,
    )

    # pega todas as mensagens da thread
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    # encontra a última resposta do assistant
    answer = None
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            answer = msg.content[0].text.value
            break

    if answer:
        st.session_state.history.append(("Você", user_input))
        st.session_state.history.append(("Assistente", answer))

# mostra o histórico
for role, text in st.session_state.history:
    st.markdown(f"**{role}:** {text}")
