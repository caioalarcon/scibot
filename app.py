# app.py
import streamlit as st
import os
from openai import OpenAI
from session_manager import get_or_create_session
from vectorstore_manager import process_user_input

# Configuração
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Identificador da sessão
session_name = st.text_input("Nome da sessão:", value="default_session")

st.set_page_config(page_title="Assistente Científico", layout="wide")
st.title("🔬 Assistente Científico com Vector Store Dinâmico")

# Inicializa a sessão
if "session" not in st.session_state or st.session_state.session["session_name"] != session_name:
    st.session_state.session = get_or_create_session(session_name)
    st.session_state.history = []

# Entrada do usuário
user_input = st.text_input("Digite sua pergunta:")

if user_input:
    # ---- Hook síncrono: atualiza o vector store ----
    st.write("🔄 Atualizando vector store...")
    process_user_input(st.session_state.session, user_input)

    # ---- Agora sim, conversa com o Assistant ----
    client.beta.threads.messages.create(
        thread_id=st.session_state.session["thread_id"],
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state.session["thread_id"],
        assistant_id=st.session_state.session["assistant_id"],
    )

    # Pega todas as mensagens
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.session["thread_id"]
    )

    # Última resposta do Assistant
    answer = None
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            answer = msg.content[0].text.value
            break

    if answer:
        st.session_state.history.append(("Você", user_input))
        st.session_state.history.append(("Assistente", answer))

# Histórico
for role, text in st.session_state.history:
    st.markdown(f"**{role}:** {text}")
