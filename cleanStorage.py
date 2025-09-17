#!/usr/bin/env python3
import os
from openai import OpenAI

# precisa ter a OPENAI_API_KEY no ambiente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cleanup_files():
    files = client.files.list(purpose="assistants")
    print(f"Encontrados {len(files.data)} arquivos no storage.")
    for f in files.data:
        fid = f.id
        fname = f.filename if hasattr(f, "filename") else "<sem nome>"
        print(f"🗑️  Deletando {fid} ({fname})...")
        client.files.delete(fid)
    print("✅ Limpeza concluída.")

if __name__ == "__main__":
    cleanup_files()
