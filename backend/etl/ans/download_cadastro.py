from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = (
    "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
)


def _list_links(url: str) -> list[str]:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    return [a.get("href") for a in soup.select("a[href]") if a.get("href")]


def _pick_cadastro_csv() -> str:
    links = _list_links(BASE_URL)
    csv_links = [l for l in links if l.lower().endswith(".csv")]
    if not csv_links:
        raise RuntimeError(
            "Nenhum CSV de cadastro encontrado na pasta da ANS.")

    return urljoin(BASE_URL, csv_links[-1])


def run(output_file: Path) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    url = _pick_cadastro_csv()
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    output_file.write_bytes(r.content)

    return output_file
