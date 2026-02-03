import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"

ZIP_REGEX = re.compile(r"(?P<tri>[1-4])T(?P<ano>\d{4})\.zip$", re.IGNORECASE)


def _list_links(url: str) -> list[str]:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    return [a.get("href") for a in soup.select("a[href]") if a.get("href")]


def _list_year_dirs() -> list[int]:
    links = _list_links(BASE_URL)
    years = []
    for href in links:
        m = re.fullmatch(r"(\d{4})/", href)
        if m:
            years.append(int(m.group(1)))
    return sorted(set(years))


def _list_zips_for_year(year: int) -> list[tuple[int, int, str]]:
    year_url = urljoin(BASE_URL, f"{year}/")
    links = _list_links(year_url)
    out = []

    for href in links:
        m = ZIP_REGEX.search(href)
        if m:
            tri = int(m.group("tri"))
            ano = int(m.group("ano"))
            out.append((ano, tri, urljoin(year_url, href)))

    return out


def get_latest_quarter_zips(n: int = 3) -> list[tuple[int, int, str]]:
    years = _list_year_dirs()
    all_zips = []

    for y in years[-5:]:
        all_zips.extend(_list_zips_for_year(y))
    all_zips.sort(key=lambda x: (x[0], x[1]), reverse=True)

    return all_zips[:n]


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))

        with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as p:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)
                    p.update(len(chunk))


def run(out_dir: Path) -> list[Path]:
    zips = get_latest_quarter_zips(3)
    paths = []

    for ano, tri, url in zips:
        filename = f"{tri}T{ano}.zip"
        dest = out_dir / filename
        download(url, dest)
        paths.append(dest)

    return paths
