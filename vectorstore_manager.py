# vectorstore_manager.py
import time
from pathlib import Path
import subprocess
import json
from openai_manager import get_client, get_prompt

client = get_client()

def extract_keywords(user_input: str) -> list[str]:
    """
    Usa GPT-4.1 para inferir palavras-chave em inglês que possam ser usadas
    para buscar artigos científicos. Se não aplicável, retorna lista vazia.
    """
    system_prompt = get_prompt("PROMPT_KEYWORDS")

    resp = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_input}]}
        ],
        text={"format": {"type": "json_object"}},
        store=True,
        temperature=1,
        max_output_tokens=2048,
        top_p=1
    )

    try:
        data = json.loads(resp.output_text)
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
            file_obj = client.files.create(file=f, purpose="assistants")
        client.vector_stores.files.create(vector_store_id=vs_id, file_id=file_obj.id)
        uploaded_ids.append(file_obj.id)
        print(f"Arquivo {pdf} enviado como {file_obj.id}")

    # Aguarda indexação
    start = time.time()
    while True:
        done = True
        for fid in uploaded_ids:
            status = client.vector_stores.files.retrieve(vector_store_id=vs_id, file_id=fid).status
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
