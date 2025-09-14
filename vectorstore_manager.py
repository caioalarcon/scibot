import os
import time
from pathlib import Path
from openai import OpenAI
import subprocess

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_keywords(user_input: str) -> list[str]:
    """
    Usa GPT-3.5 para extrair palavras-chave em JSON.
    Se não houver termos científicos relevantes, retorna lista vazia.
    """
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Extraia palavras-chave científicas da pergunta. Responda só em JSON: {\"keywords\": [...]}"},
            {"role": "user", "content": user_input}
        ]
    )
    try:
        import json
        data = json.loads(resp.choices[0].message.content)
        return data.get("keywords", [])
    except Exception:
        return []

def process_user_input(session, user_input: str, max_results=10, timeout=300):
    """
    Processa input do usuário:
    - Extrai keywords
    - Busca no OpenAlex
    - Baixa artigos via script existente
    - Faz upload para o vector store
    - Bloqueia até indexação terminar ou timeout
    """
    keywords = extract_keywords(user_input)
    if not keywords:
        print("Nenhuma palavra-chave científica detectada.")
        return

    session_name = session["session_name"]
    vs_id = session["vector_store_id"]

    # Chama o script externo para baixar artigos
    cmd = ["python", "downloadarticlesfromscihub.py", session_name, str(max_results)] + keywords
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

    # Verifica diretório de saída
    outdir = Path("temp") / session_name
    pdfs = list(outdir.glob("*.pdf"))

    uploaded_ids = []
    for pdf in pdfs:
        with open(pdf, "rb") as f:
            file_obj = client.files.create(
                file=f,
                purpose="assistants"
            )
        # associa ao vector store
        client.vector_stores.files.create(
            vector_store_id=vs_id,
            file_id=file_obj.id
        )
        uploaded_ids.append(file_obj.id)
        print(f"Arquivo {pdf} enviado como {file_obj.id}")

    # aguarda indexação
    start = time.time()
    while True:
        done = True
        for fid in uploaded_ids:
            status = client.vector_stores.files.retrieve(
                vector_store_id=vs_id,
                file_id=fid
            ).status
            if status != "completed":
                done = False
                break
        if done:
            print("Todos arquivos indexados!")
            break
        if time.time() - start > timeout:
            print("Timeout esperando indexação.")
            break
        time.sleep(5)
