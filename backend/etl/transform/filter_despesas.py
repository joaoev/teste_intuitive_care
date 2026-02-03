from __future__ import annotations
import pandas as pd
import unicodedata

TARGET_PHRASES = [
    "despesas com eventos sinistros",
    "despesa com evento sinistro",
]


def _to_number(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce").fillna(0.0)


def _normalize_text(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.lower().str.strip()
    s = s.map(lambda v: unicodedata.normalize("NFKD", v))
    s = s.map(lambda v: "".join(ch for ch in v if not unicodedata.combining(ch)))
    s = s.str.replace(r"[^\w\s]", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    return s


def _keep_leaf_account_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove linhas de contas agregadoras (ex: 41, 411, 4111...) quando
    existem contas-filhas mais detalhadas para a mesma operadora/período.
    """
    required = {"reg_ans", "data_referencia", "codigo_conta"}
    if not required.issubset(df.columns):
        return df

    out_groups: list[pd.DataFrame] = []
    grouped = df.groupby(["reg_ans", "data_referencia"], dropna=False, sort=False)
    for _, g in grouped:
        g = g.copy()
        g["codigo_conta"] = g["codigo_conta"].astype(str).str.strip()
        codes = [c for c in g["codigo_conta"].unique() if c]

        prefixes: set[str] = set()
        for code in codes:
            for i in range(1, len(code)):
                prefixes.add(code[:i])

        leaf_codes = {c for c in codes if c not in prefixes}
        out_groups.append(g[g["codigo_conta"].isin(leaf_codes)])

    if not out_groups:
        return df.iloc[0:0]

    return pd.concat(out_groups, ignore_index=True)


def filter_despesas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # tenta achar uma coluna de texto provável
    text_cols = [c for c in ["conta", "descricao",
                             "descricao_conta"] if c in df.columns]
    if not text_cols:
        return df.iloc[0:0]

    col = text_cols[0]
    s = _normalize_text(df[col])

    mask = False
    for k in TARGET_PHRASES:
        mask = mask | s.str.contains(k, na=False)

    out = df[mask].copy()

    # Mantém somente valores positivos para evitar ruído de linhas zeradas.
    if "valor" in out.columns:
        out = out[_to_number(out["valor"]) > 0]

    # Evita dupla contagem por hierarquia de plano de contas.
    out = _keep_leaf_account_rows(out)

    return out
