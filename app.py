import streamlit as st
from session_manager import get_or_create_session
from assistant_runner import run_assistant_message

st.set_page_config(page_title="Assistente Científico", layout="wide")
st.title("🔬 Assistente Científico com PDFs")

# Entrada de sessão manual (ou gera nova se vazio)
session_name = st.text_input("ID da sessão (deixe em branco para nova):", "")

if "session" not in st.session_state:
    st.session_state.session = get_or_create_session(session_name or None)
    st.session_state.history = []

user_input = st.text_input("Digite sua pergunta:")

if user_input:
    st.session_state.history.append(("Você", user_input))
    st.write("🔎 Hook disparado → aqui vamos buscar novos artigos futuramente!")

    answer = run_assistant_message(st.session_state.session, user_input)
    if answer:
        st.session_state.history.append(("Assistente", answer))

# Mostra histórico
for role, text in st.session_state.history:
    st.markdown(f"**{role}:** {text}")
