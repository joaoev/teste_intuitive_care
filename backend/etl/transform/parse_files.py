from __future__ import annotations
from pathlib import Path
import pandas as pd
import chardet


def _detect_encoding(path: Path) -> str:
    raw = path.read_bytes()[:200_000]
    guess = chardet.detect(raw)
    return guess.get("encoding") or "utf-8"


def read_any_table(path: Path) -> pd.DataFrame:
    ext = path.suffix.lower()

    if ext in [".xlsx", ".xls"]:
        return pd.read_excel(path)

    # CSV/TXT: tenta detectar separador e encoding
    enc = _detect_encoding(path)
    try:
        return pd.read_csv(path, encoding=enc, sep=None, engine="python")
    except Exception:
        # fallback comum em pt-br
        return pd.read_csv(path, encoding=enc, sep=";", engine="python")
