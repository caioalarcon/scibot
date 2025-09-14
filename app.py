import streamlit as st
import requests
import os
from openai import OpenAI

# Configure sua API key do OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="Assistente Científico", layout="wide")
st.title("🔬 Assistente Científico com GPT + OpenAlex")

# Histórico de conversa
if "history" not in st.session_state:
    st.session_state.history = []

# Entrada do usuário
user_input = st.text_input("Digite sua pergunta:")

def search_openalex(query, max_results=3):
    url = f"https://api.openalex.org/works?q={query}&per_page={max_results}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    data = resp.json()
    results = []
    for work in data.get("results", []):
        title = work.get("title", "Sem título")
        doi = work.get("doi", "Sem DOI")
        authors = [a["author"]["display_name"] for a in work.get("authorships", [])]
        results.append({
            "title": title,
            "doi": doi,
            "authors": ", ".join(authors)
        })
    return results

if user_input:
    # Busca artigos no OpenAlex
    articles = search_openalex(user_input)

    # Monta contexto com artigos encontrados
    articles_context = "\n".join(
        [f"- {a['title']} ({a['doi']})" for a in articles]
    ) or "Nenhum artigo encontrado."

    prompt = f"""
    Pergunta: {user_input}

    Aqui estão alguns artigos encontrados no OpenAlex:
    {articles_context}

    Responda de forma clara, usando os artigos como referência quando possível.
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Você é um assistente científico."},
                  {"role": "user", "content": prompt}]
    )

    answer = completion.choices[0].message.content

    # Armazena no histórico
    st.session_state.history.append(("Você", user_input))
    st.session_state.history.append(("Assistente", answer))

# Mostra histórico
for role, text in st.session_state.history:
    st.markdown(f"**{role}:** {text}")
