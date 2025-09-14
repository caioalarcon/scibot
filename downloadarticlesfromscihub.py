#!/usr/bin/env python3
import sys
import requests
from pathlib import Path
import openalex
import re

# Sci-Hub (domínio pode mudar)
SCIHUB_URL = "https://sci-hub.se"

def download_from_scihub(doi, outdir):
    """Tenta baixar um artigo do Sci-Hub dado um DOI cru (ex: 10.1016/xxxx)."""
    try:
        safe_doi = doi.replace("/", "_").replace(":", "_")
        filepath = Path(outdir) / f"{safe_doi}.pdf"

        # já existe, não baixa de novo
        if filepath.exists():
            print(f"✅ Já existe: {filepath}")
            return str(filepath)

        url = f"{SCIHUB_URL}/{doi}"
        resp = requests.get(url, timeout=1)

        if resp.status_code != 200:
            print(f"Falha ao acessar Sci-Hub para {doi}")
            return None

        # Extrai link do embed
        match = re.search(r'<embed[^>]+src="([^"]+)"', resp.text)
        if not match:
            print(f"PDF embed não encontrado para {doi}")
            return None

        src_url = match.group(1)
        if src_url.startswith("//"):
            pdf_url = "https:" + src_url
        elif src_url.startswith("/"):
            pdf_url = SCIHUB_URL + src_url
        else:
            pdf_url = src_url

        pdf_url = pdf_url.split("#")[0]

        # Faz download real do PDF
        pdf_resp = requests.get(pdf_url, timeout=2)
        if pdf_resp.status_code == 200 and b"%PDF" in pdf_resp.content[:10]:
            with open(filepath, "wb") as f:
                f.write(pdf_resp.content)
            print(f"⬇️ Baixado: {filepath}")
            return str(filepath)
        else:
            print(f"Falha ao baixar PDF de {doi} em {pdf_url}")
            return None

    except Exception as e:
        print(f"Erro ao processar {doi}: {e}")
        return None


def download_articles(session_name, limit, keywords, sort="cited_by_count:desc", filter_field="title.search"):
    """
    Busca artigos no OpenAlex e tenta baixar PDFs do Sci-Hub.
    Agora busca cada keyword separadamente e acumula DOIs únicos.
    """
    outdir = Path("temp") / session_name
    outdir.mkdir(parents=True, exist_ok=True)

    all_dois = set()

    for kw in keywords:
        print(f"🔍 Buscando por keyword: {kw}")
        try:
            results = openalex.search_openalex(limit, [kw], sort=sort, filter_field=filter_field)
            for doi in results.get("dois", []):
                all_dois.add(doi)
        except Exception as e:
            print(f"Erro na busca por {kw}: {e}")

    downloaded = []
    for doi_url in list(all_dois):
        if doi_url.startswith("https://doi.org/"):
            doi = doi_url.replace("https://doi.org/", "")
        else:
            doi = doi_url
        pdf = download_from_scihub(doi, outdir)
        if pdf:
            downloaded.append(pdf)

    return {"session": session_name, "downloaded": downloaded}


def main():
    if len(sys.argv) < 4:
        print("Uso: python downloadarticlesfromscihub.py <session_name> <limite> <palavra1> <palavra2> ... [--filter=title.search] [--sort=cited_by_count:desc]")
        sys.exit(1)

    session_name = sys.argv[1]
    try:
        limit = int(sys.argv[2])
    except ValueError:
        print("O limite precisa ser um número.")
        sys.exit(1)

    keywords = []
    sort = "cited_by_count:desc"
    filter_field = "title.search"

    for arg in sys.argv[3:]:
        if arg.startswith("--filter="):
            filter_field = arg.split("=", 1)[1]
        elif arg.startswith("--sort="):
            sort = arg.split("=", 1)[1]
        else:
            keywords.append(arg)

    result = download_articles(session_name, limit, keywords, sort=sort, filter_field=filter_field)
    print(result)


if __name__ == "__main__":
    main()
