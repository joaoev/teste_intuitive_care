from __future__ import annotations

from pathlib import Path

import pandas as pd


def run(input_csv: Path, output_csv: Path) -> Path:
    df = pd.read_csv(input_csv, dtype=str)
    df["ValorDespesas"] = pd.to_numeric(
        df["ValorDespesas"], errors="coerce").fillna(0)
    df["RazaoSocial"] = df["RazaoSocial"].fillna("")
    df["UF"] = df["UF"].fillna("")

    grouped = (
        df.groupby(["RazaoSocial", "UF"], as_index=False)["ValorDespesas"]
        .agg(["sum", "mean", "std"])
        .reset_index()
        .rename(
            columns={
                "sum": "TotalDespesas",
                "mean": "MediaDespesasTrimestre",
                "std": "DesvioPadraoDespesas",
            }
        )
    )
    grouped["DesvioPadraoDespesas"] = grouped["DesvioPadraoDespesas"].fillna(0)
    grouped = grouped.sort_values("TotalDespesas", ascending=False)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(output_csv, index=False, encoding="utf-8-sig")

    return output_csv
