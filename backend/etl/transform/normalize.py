from __future__ import annotations

import re
import unicodedata
from typing import Dict, Iterable, Optional

import pandas as pd


def slugify_col(name: str) -> str:
    """
    Normaliza um nome de coluna para um formato comparável.
    Ex: "Razão Social" -> "razao_social"
        "VL. SALDO FINAL" -> "vl_saldo_final"
    """
    s = str(name).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    # remove acentos
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^\w\s]", " ", s)  # tira pontuação
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


# Nomes canônicos que VOCÊ usa em todo o projeto
CANONICAL_COLS = {
    "cnpj": [
        "cnpj", "nr_cnpj", "cnpj_operadora", "cnpj_da_operadora", "cnpj_prestador"
    ],
    "razao_social": [
        "razao_social", "razao", "nome", "nome_operadora", "nm_razao_social", "nome_da_operadora"
    ],
    "descricao_conta": [
        "descricao_conta", "ds_conta", "conta", "descricao", "historico", "descricao_da_conta"
    ],
    "codigo_conta": [
        "codigo_conta", "cd_conta", "cod_conta", "conta_codigo", "cd_plano_contas"
    ],
    "valor": [
        "valor", "vl", "vl_saldo", "vl_saldo_final", "vl_total", "valor_total", "valor_despesa"
    ],
    "data_referencia": [
        "data_referencia", "dt_referencia", "data", "dt_competencia", "competencia"
    ],
}


def _match_exact_or_contains(cols: Iterable[str], options: Iterable[str]) -> Optional[str]:
    """
    Tenta achar coluna por:
    1) match exato
    2) "contém" (ex: 'nr_cnpj' contém 'cnpj')
    3) prefixo (ex: 'vl_saldo_final' começa com 'vl_')
    """
    cols = list(cols)
    opt = list(options)

    # 1) exato
    for o in opt:
        if o in cols:
            return o

    # 2) contém
    for c in cols:
        for o in opt:
            if o in c:
                return c

    # 3) prefixo (útil p/ vl_*)
    for c in cols:
        for o in opt:
            if c.startswith(o):
                return c

    return None


def normalize_dataframe_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, str]]:
    """
    Retorna:
    - df com colunas renomeadas (canônicas)
    - mapping original->canônico (pra log/depuração)
    """
    df = df.copy()

    original_cols = list(df.columns)
    normalized_cols = [slugify_col(c) for c in original_cols]

    # aplica slugify temporário
    temp_map = dict(zip(original_cols, normalized_cols))
    df.rename(columns=temp_map, inplace=True)

    # agora escolhe quais colunas viram canônicas
    rename_to_canonical: Dict[str, str] = {}
    for canonical, options in CANONICAL_COLS.items():
        match = _match_exact_or_contains(df.columns, options)
        if match:
            rename_to_canonical[match] = canonical

    df.rename(columns=rename_to_canonical, inplace=True)

    # gera mapping original -> canônico (só das colunas mapeadas)
    final_mapping: Dict[str, str] = {}
    # original -> slug
    # slug -> original (aproximação)
    inv_temp = {v: k for k, v in temp_map.items()}
    for slug_col, canon_col in rename_to_canonical.items():
        original_guess = inv_temp.get(slug_col, slug_col)
        final_mapping[original_guess] = canon_col

    return df, final_mapping
