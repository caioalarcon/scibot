# openai_manager.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis do .env
load_dotenv()

# Inicializa cliente único
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY não encontrado no .env")

client = OpenAI(api_key=OPENAI_API_KEY)

def get_client() -> OpenAI:
    """Retorna cliente OpenAI já configurado."""
    return client

def get_prompt(name: str) -> str:
    """Retorna um prompt definido no .env pelo nome."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Prompt {name} não encontrado no .env")
    return value
