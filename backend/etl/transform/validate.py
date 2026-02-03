from __future__ import annotations

from pathlib import Path

import pandas as pd


def _only_digits(value: object) -> str:
    return "".join(ch for ch in str(value) if ch.isdigit())


def is_valid_cnpj(value: object) -> bool:
    cnpj = _only_digits(value)
    if len(cnpj) != 14:
        return False
    if cnpj == cnpj[0] * 14:
        return False

    def calc_digit(base: str, weights: list[int]) -> int:
        total = sum(int(num) * w for num, w in zip(base, weights))
        rest = total % 11
        return 0 if rest < 2 else 11 - rest

    d1 = calc_digit(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = calc_digit(cnpj[:12] + str(d1),
                    [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return cnpj[-2:] == f"{d1}{d2}"


def run(input_csv: Path, output_csv: Path, reject_invalid: bool = False) -> Path:
    df = pd.read_csv(input_csv, dtype=str)

    df["ValorDespesas"] = pd.to_numeric(df["ValorDespesas"], errors="coerce")
    df["RazaoSocial"] = df["RazaoSocial"].fillna("").astype(str).str.strip()
    df["CNPJ"] = df["CNPJ"].fillna("").astype(str)

    cnpj_ok = df["CNPJ"].map(is_valid_cnpj)
    valor_ok = df["ValorDespesas"].fillna(0) > 0
    razao_ok = df["RazaoSocial"] != ""

    errors = []
    for _, row in pd.DataFrame(
        {"cnpj": cnpj_ok, "valor": valor_ok, "razao": razao_ok}
    ).iterrows():
        row_err = []
        if not row["cnpj"]:
            row_err.append("CNPJ_INVALIDO")
        if not row["valor"]:
            row_err.append("VALOR_INVALIDO")
        if not row["razao"]:
            row_err.append("RAZAO_VAZIA")
        errors.append("|".join(row_err))

    df["Valido"] = [err == "" for err in errors]
    df["ErrosValidacao"] = errors

    if reject_invalid:
        df = df[df["Valido"]].copy()

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    return output_csv
