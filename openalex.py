#!/usr/bin/env python3
import sys
import requests
import json

BASE_URL = "https://api.openalex.org/works"

def search_openalex(limit, keywords):
    """
    Busca artigos no OpenAlex com base em palavras-chave.
    
    Args:
        limit (int): número máximo de resultados
        keywords (list[str]): lista de palavras-chave

    Returns:
        dict: {"dois": [lista de DOIs]}
    """
    query = " ".join(keywords)
    url = f"{BASE_URL}?q={query}&per_page={limit}"
    resp = requests.get(url)

    if resp.status_code != 200:
        raise RuntimeError(f"Erro {resp.status_code}: {resp.text}")

    data = resp.json()
    dois = []
    for work in data.get("results", []):
        doi = work.get("doi")
        if doi:  # nem todo artigo tem DOI
            dois.append(doi)

    return {"dois": dois}


def main():
    if len(sys.argv) < 3:
        print("Uso: python openalex.py <limite> <palavra1> <palavra2> ...")
        sys.exit(1)

    try:
        limit = int(sys.argv[1])
    except ValueError:
        print("O primeiro argumento deve ser um número (limite de resultados).")
        sys.exit(1)

    keywords = sys.argv[2:]
    result = search_openalex(limit, keywords)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
