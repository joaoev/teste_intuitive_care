from __future__ import annotations
import pandas as pd

KEYWORDS = [
    "sinistro",
    "eventos",
    "eventos_indennizaveis",
    "eventos indeniz",
    "despesas assist",
    "assistencial",
]


def filter_despesas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # tenta achar uma coluna de texto provável
    text_cols = [c for c in ["conta", "descricao",
                             "descricao_conta"] if c in df.columns]
    if not text_cols:
        return df.iloc[0:0]

    col = text_cols[0]
    s = df[col].astype(str).str.lower()

    mask = False
    for k in KEYWORDS:
        mask = mask | s.str.contains(k, na=False)

    return df[mask]
