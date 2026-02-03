from __future__ import annotations

from pathlib import Path

import pandas as pd


def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lower_map = {str(c).lower(): c for c in df.columns}
    for name in candidates:
        if name in lower_map:
            return lower_map[name]
    for col in df.columns:
        lcol = str(col).lower()
        if any(name in lcol for name in candidates):
            return col
    return None


def _clean_cnpj(value: object) -> str:
    if value is None:
        return ""
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return digits.zfill(14) if digits else ""


def run(consolidated_csv: Path, cadastro_csv: Path, output_csv: Path) -> Path:
    despesas = pd.read_csv(consolidated_csv, dtype=str)
    try:
        cadastro = pd.read_csv(
            cadastro_csv, dtype=str, sep=None, encoding="utf-8", engine="python"
        )
    except Exception:
        cadastro = pd.read_csv(
            cadastro_csv, dtype=str, sep=";", encoding="utf-8", engine="python"
        )

    cad_reg_col = _find_col(
        cadastro,
        ["registro_ans", "reg_ans", "registro_operadora", "registro da operadora"],
    )
    cad_cnpj_col = _find_col(cadastro, ["cnpj"])
    cad_razao_col = _find_col(
        cadastro, ["razao_social", "nome_fantasia", "nome"])
    cad_modalidade_col = _find_col(cadastro, ["modalidade"])
    cad_uf_col = _find_col(cadastro, ["uf"])

    if not cad_reg_col or not cad_cnpj_col:
        raise ValueError("Cadastro sem colunas obrigatórias de REG_ANS/CNPJ.")

    cadastro = cadastro.rename(
        columns={
            cad_reg_col: "RegistroANS",
            cad_cnpj_col: "CNPJ",
            cad_razao_col: "RazaoSocial" if cad_razao_col else "RazaoSocial",
            cad_modalidade_col: "Modalidade" if cad_modalidade_col else "Modalidade",
            cad_uf_col: "UF" if cad_uf_col else "UF",
        }
    )

    for col in ["RazaoSocial", "Modalidade", "UF"]:
        if col not in cadastro.columns:
            cadastro[col] = ""

    cadastro["RegistroANS"] = cadastro["RegistroANS"].astype(str).str.strip()
    cadastro["CNPJ"] = cadastro["CNPJ"].map(_clean_cnpj)

    cadastro = cadastro.sort_values(["RegistroANS"]).drop_duplicates(
        subset=["RegistroANS"], keep="first"
    )

    despesas["RegistroANS"] = despesas["RegistroANS"].astype(str).str.strip()
    out = despesas.merge(
        cadastro[["RegistroANS", "CNPJ", "RazaoSocial", "Modalidade", "UF"]],
        on="RegistroANS",
        how="left",
    )
    out["RazaoSocial"] = out["RazaoSocial"].fillna("")
    out["Modalidade"] = out["Modalidade"].fillna("")
    out["UF"] = out["UF"].fillna("")
    out["CNPJ"] = out["CNPJ"].fillna("")
    out["StatusCadastro"] = out["CNPJ"].map(
        lambda x: "OK" if x else "SEM_MATCH")

    cols = [
        "CNPJ",
        "RazaoSocial",
        "Trimestre",
        "Ano",
        "ValorDespesas",
        "RegistroANS",
        "Modalidade",
        "UF",
        "StatusCadastro",
    ]
    out = out[cols]

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False, encoding="utf-8-sig")

    return output_csv
