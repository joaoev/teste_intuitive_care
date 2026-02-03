from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "output"
ENRICHED_CSV = OUTPUT_DIR / "consolidado_validado.csv"

app = FastAPI(title="Teste Intuitive Care API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_cache_stats: dict[str, object] = {"data": None, "expires_at": 0.0}


def _load_data() -> pd.DataFrame:
    if not ENRICHED_CSV.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ENRICHED_CSV}")

    df = pd.read_csv(ENRICHED_CSV, dtype=str)
    if "ValorDespesas" in df.columns:
        df["ValorDespesas"] = pd.to_numeric(
            df["ValorDespesas"], errors="coerce").fillna(0)
    else:
        df["ValorDespesas"] = 0.0

    for col in ["CNPJ", "RazaoSocial", "RegistroANS", "Modalidade", "UF"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)

    for col in ["Ano", "Trimestre"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


def _operator_list(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.sort_values(["Ano", "Trimestre"])
        .groupby("CNPJ", as_index=False)
        .agg(
            RazaoSocial=("RazaoSocial", "last"),
            RegistroANS=("RegistroANS", "last"),
            Modalidade=("Modalidade", "last"),
            UF=("UF", "last"),
            TotalDespesas=("ValorDespesas", "sum"),
        )
    )
    out = out[out["CNPJ"] != ""]
    return out


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/operadoras")
def list_operadoras(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    search: str = Query(default=""),
):
    df = _operator_list(_load_data())
    if search:
        q = search.strip().lower()
        df = df[
            df["RazaoSocial"].str.lower().str.contains(q, na=False)
            | df["CNPJ"].str.contains(q, na=False)
        ]

    total = len(df)
    start = (page - 1) * limit
    end = start + limit
    page_data = df.sort_values(
        "TotalDespesas", ascending=False).iloc[start:end]

    return {
        "data": page_data.to_dict(orient="records"),
        "total": total,
        "page": page,
        "limit": limit,
    }


@app.get("/api/operadoras/{cnpj}")
def detail_operadora(cnpj: str):
    df = _operator_list(_load_data())
    row = df[df["CNPJ"] == cnpj]
    if row.empty:
        raise HTTPException(
            status_code=404, detail="Operadora não encontrada.")
    return row.iloc[0].to_dict()


@app.get("/api/operadoras/{cnpj}/despesas")
def historico_despesas(cnpj: str):
    df = _load_data()
    rows = (
        df[df["CNPJ"] == cnpj]
        .sort_values(["Ano", "Trimestre"])
        .loc[:, ["Ano", "Trimestre", "ValorDespesas", "UF"]]
    )
    if rows.empty:
        raise HTTPException(
            status_code=404, detail="Operadora não encontrada.")
    return {"cnpj": cnpj, "data": rows.to_dict(orient="records")}


@app.get("/api/estatisticas")
def estatisticas():
    now = time.time()
    if _cache_stats["data"] is not None and now < float(_cache_stats["expires_at"]):
        return _cache_stats["data"]

    df = _operator_list(_load_data())
    total_despesas = float(df["TotalDespesas"].sum()) if not df.empty else 0.0
    media_despesas = float(df["TotalDespesas"].mean()) if not df.empty else 0.0
    top5 = (
        df.sort_values("TotalDespesas", ascending=False)
        .head(5)
        .to_dict(orient="records")
    )

    payload = {
        "total_despesas": total_despesas,
        "media_despesas": media_despesas,
        "top5_operadoras": top5,
    }
    _cache_stats["data"] = payload
    _cache_stats["expires_at"] = now + 300

    return payload
