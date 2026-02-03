from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def parse_br_number(value: object) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    s = str(value).strip()

    if not s:
        return 0.0
    s = s.replace(".", "").replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return 0.0


def quarter_from_date(value: object) -> tuple[int, int]:
    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        return 0, 0
    quarter = ((dt.month - 1) // 3) + 1
    return int(dt.year), int(quarter)


def consolidate_filtered_files(files: Iterable[Path]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for file in files:
        df = pd.read_csv(file, dtype=str)

        if "reg_ans" not in df.columns or "valor" not in df.columns:
            continue

        for _, row in df.iterrows():
            ano, trimestre = quarter_from_date(row.get("data_referencia"))
            rows.append(
                {
                    "RegistroANS": str(row.get("reg_ans", "")).strip(),
                    "Ano": ano,
                    "Trimestre": trimestre,
                    "ValorDespesas": parse_br_number(row.get("valor")),
                }
            )

    out = pd.DataFrame(rows)

    if out.empty:
        return pd.DataFrame(
            columns=["RegistroANS", "Ano", "Trimestre", "ValorDespesas"]
        )

    out = (
        out.groupby(["RegistroANS", "Ano", "Trimestre"],
                    as_index=False)["ValorDespesas"]
        .sum()
        .sort_values(["Ano", "Trimestre", "RegistroANS"])
    )

    return out


def run(input_dir: Path, output_csv: Path) -> Path:
    files = sorted(input_dir.glob("*_filtered.csv"))
    consolidated = consolidate_filtered_files(files)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    consolidated.to_csv(output_csv, index=False, encoding="utf-8-sig")

    return output_csv
