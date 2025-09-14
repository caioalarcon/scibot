#!/usr/bin/env python3
import sys
import requests
import json

BASE_URL = "https://api.openalex.org/works"

def search_openalex(limit, keywords, sort="cited_by_count:desc", filter_field=None):
    """
    Busca artigos no OpenAlex com base em palavras-chave.

    Args:
        limit (int): número máximo de resultados
        keywords (list[str]): lista de palavras-chave
        sort (str): campo de ordenação (default: mais citados)
        filter_field (str): campo específico para busca (ex: "title.search", "abstract.search")

    Returns:
        dict: {"dois": [lista de DOIs]}
    """
    query = " ".join(keywords)
    if filter_field:
        url = f"{BASE_URL}?filter={filter_field}:{query}&per_page={limit}&sort={sort}"
    else:
        url = f"{BASE_URL}?q={query}&per_page={limit}&sort={sort}"

    resp = requests.get(url)

    if resp.status_code != 200:
        raise RuntimeError(f"Erro {resp.status_code}: {resp.text}")

    data = resp.json()
    dois = []
    for work in data.get("results", []):
        doi = work.get("doi")
        if doi:
            dois.append(doi)

    return {"dois": dois}


def main():
    if len(sys.argv) < 3:
        print("Uso: python openalex.py <limite> <palavra1> <palavra2> ... [--filter=title.search] [--sort=cited_by_count:desc]")
        sys.exit(1)

    try:
        limit = int(sys.argv[1])
    except ValueError:
        print("O primeiro argumento deve ser um número (limite de resultados).")
        sys.exit(1)

    # parâmetros extras
    keywords = []
    sort = "cited_by_count:desc"
    filter_field = None

    for arg in sys.argv[2:]:
        if arg.startswith("--filter="):
            filter_field = arg.split("=", 1)[1]
        elif arg.startswith("--sort="):
            sort = arg.split("=", 1)[1]
        else:
            keywords.append(arg)

    result = search_openalex(limit, keywords, sort=sort, filter_field=filter_field)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
