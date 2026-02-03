"""Interface de linha de comando para o ETL de dados da ANS."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from etl.ans import download, extract, download_cadastro
from etl.transform import (
    parse_files,
    normalize,
    filter_despesas,
    consolidate,
    enrich,
    validate,
    aggregate,
)


def cmd_download(args):
    """Baixa os arquivos ZIP mais recentes da ANS."""
    print("[download] Iniciando download dos arquivos da ANS...")
    try:
        paths = download.run(Path(args.out_dir))
        print(f"[ok] {len(paths)} arquivo(s) baixado(s):")
        for p in paths:
            print(f"  - {p}")
    except Exception as e:
        print(f"[erro] Erro no download: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_extract(args):
    """Extrai os arquivos ZIP baixados."""
    print("[extract] Extraindo arquivos ZIP...")
    try:
        paths = extract.run(Path(args.zips_dir), Path(args.out_dir))
        print(f"[ok] {len(paths)} arquivo(s) extraído(s):")
        for p in paths:
            print(f"  - {p}")
    except Exception as e:
        print(f"[erro] Erro na extração: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_parse(args):
    """Lê e normaliza arquivos CSV/Excel."""
    print("[parse] Processando arquivos...")
    in_dir = Path(args.in_dir)

    if not in_dir.exists():
        print(f"[erro] Diretório não encontrado: {in_dir}", file=sys.stderr)
        sys.exit(1)

    files = list(in_dir.rglob("*.csv")) + \
        list(in_dir.rglob("*.xlsx")) + list(in_dir.rglob("*.xls"))

    if not files:
        print(f"[aviso] Nenhum arquivo CSV/Excel encontrado em {in_dir}")
        return

    for f in files:
        try:
            print(f"\n[arquivo] Processando: {f.name}")
            df = parse_files.read_any_table(f)
            df_normalized, mapping = normalize.normalize_dataframe_columns(df)
            print(
                f"  Linhas: {len(df_normalized)} | Colunas: {len(df_normalized.columns)}")
            if mapping:
                print(f"  Mapeamento: {mapping}")
        except Exception as e:
            print(f"  [erro] Erro: {e}", file=sys.stderr)


def cmd_filter(args):
    """Filtra despesas relevantes de um arquivo."""
    print("[filtro] Filtrando despesas...")
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"[erro] Arquivo não encontrado: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = parse_files.read_any_table(file_path)
        df_normalized, _ = normalize.normalize_dataframe_columns(df)
        filtered = filter_despesas.filter_despesas(df_normalized)

        print(
            f"[ok] Registros filtrados: {len(filtered)}/{len(df_normalized)}")

        if args.output:
            output_path = Path(args.output)
            filtered.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"[salvo] Resultado salvo em: {output_path}")
        else:
            print("\n[preview] Primeiras 10 linhas:")
            print(filtered.head(10))

    except Exception as e:
        print(f"[erro] Erro ao filtrar: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_run(args):
    """Executa o pipeline completo: download -> extract -> parse -> filter."""
    print("[run] Executando pipeline completo...\n")

    base_dir = Path(args.base_dir)
    downloads_dir = base_dir / "downloads"
    extracted_dir = base_dir / "extracted"
    output_dir = base_dir / "output"
    cadastro_dir = base_dir / "cadastro"

    # Criar diretórios
    downloads_dir.mkdir(parents=True, exist_ok=True)
    extracted_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    cadastro_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Download
        print("=" * 50)
        paths = download.run(downloads_dir)
        print(f"[ok] Download concluído: {len(paths)} arquivo(s)\n")

        # 2. Extract
        print("=" * 50)
        extracted = extract.run(downloads_dir, extracted_dir)
        print(f"[ok] Extração concluída: {len(extracted)} arquivo(s)\n")

        # 3. Parse e Filter
        print("=" * 50)
        files = list(extracted_dir.rglob("*.csv")) + \
            list(extracted_dir.rglob("*.xlsx"))

        for f in files:
            print(f"\n[arquivo] Processando: {f.name}")
            df = parse_files.read_any_table(f)
            df_normalized, _ = normalize.normalize_dataframe_columns(df)
            filtered = filter_despesas.filter_despesas(df_normalized)

            output_file = output_dir / f"{f.stem}_filtered.csv"
            filtered.to_csv(output_file, index=False, encoding="utf-8-sig")
            print(f"  [ok] Filtrado e salvo: {output_file}")

        print("\n" + "=" * 50)
        consolidated_csv = output_dir / "consolidado_despesas.csv"
        consolidate.run(output_dir, consolidated_csv)
        print(f"[ok] Consolidado gerado: {consolidated_csv}")

        cadastro_csv = cadastro_dir / "operadoras_ativas.csv"
        download_cadastro.run(cadastro_csv)
        print(f"[ok] Cadastro baixado: {cadastro_csv}")

        enriched_csv = output_dir / "consolidado_enriquecido.csv"
        enrich.run(consolidated_csv, cadastro_csv, enriched_csv)
        print(f"[ok] CSV enriquecido: {enriched_csv}")

        validated_csv = output_dir / "consolidado_validado.csv"
        validate.run(enriched_csv, validated_csv, reject_invalid=False)
        print(f"[ok] CSV validado: {validated_csv}")

        agg_csv = output_dir / "despesas_agregadas.csv"
        aggregate.run(validated_csv, agg_csv)
        print(f"[ok] Agregado gerado: {agg_csv}")

        print("\n" + "=" * 50)
        print("[fim] Pipeline completo executado com sucesso!")
        print(f"[saida] Resultados em: {output_dir}")

    except Exception as e:
        print(f"\n[erro] Erro no pipeline: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_consolidate(args):
    input_dir = Path(args.input_dir)
    output = Path(args.output)
    out = consolidate.run(input_dir, output)
    print(f"[ok] Consolidado salvo em: {out}")


def cmd_enrich(args):
    out = enrich.run(Path(args.input), Path(args.cadastro), Path(args.output))
    print(f"[ok] Enriquecido salvo em: {out}")


def cmd_validate(args):
    out = validate.run(
        Path(args.input),
        Path(args.output),
        reject_invalid=bool(args.reject_invalid),
    )
    print(f"[ok] Validado salvo em: {out}")


def cmd_aggregate(args):
    out = aggregate.run(Path(args.input), Path(args.output))
    print(f"[ok] Agregado salvo em: {out}")


def main():
    parser = argparse.ArgumentParser(
        description="CLI para ETL de dados da ANS (Agência Nacional de Saúde)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s download --out-dir ./downloads
  %(prog)s extract --zips-dir ./downloads --out-dir ./extracted
  %(prog)s parse --in-dir ./extracted
  %(prog)s filter --file ./extracted/file.csv --output ./result.csv
  %(prog)s run --base-dir ./data
        """
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Comandos disponíveis")

    # Download
    p_dl = subparsers.add_parser("download", help="Baixa arquivos da ANS")
    p_dl.add_argument("--out-dir", required=True, help="Diretório de destino")
    p_dl.set_defaults(func=cmd_download)

    # Extract
    p_ex = subparsers.add_parser("extract", help="Extrai arquivos ZIP")
    p_ex.add_argument("--zips-dir", required=True, help="Diretório com ZIPs")
    p_ex.add_argument("--out-dir", required=True, help="Diretório de destino")
    p_ex.set_defaults(func=cmd_extract)

    # Parse
    p_parse = subparsers.add_parser("parse", help="Lê e normaliza arquivos")
    p_parse.add_argument("--in-dir", required=True,
                         help="Diretório com arquivos")
    p_parse.set_defaults(func=cmd_parse)

    # Filter
    p_filter = subparsers.add_parser(
        "filter", help="Filtra despesas de um arquivo")
    p_filter.add_argument("--file", required=True, help="Arquivo de entrada")
    p_filter.add_argument("--output", "-o", help="Arquivo de saída (opcional)")
    p_filter.set_defaults(func=cmd_filter)

    # Run (pipeline completo)
    p_run = subparsers.add_parser("run", help="Executa pipeline completo")
    p_run.add_argument("--base-dir", default="./data",
                       help="Diretório base (padrão: ./data)")
    p_run.set_defaults(func=cmd_run)

    p_cons = subparsers.add_parser(
        "consolidate", help="Consolida os *_filtered.csv")
    p_cons.add_argument("--input-dir", required=True,
                        help="Diretório com *_filtered.csv")
    p_cons.add_argument("--output", required=True, help="Arquivo CSV de saída")
    p_cons.set_defaults(func=cmd_consolidate)

    p_enrich = subparsers.add_parser(
        "enrich", help="Enriquece o consolidado com cadastro")
    p_enrich.add_argument("--input", required=True, help="CSV consolidado")
    p_enrich.add_argument("--cadastro", required=True,
                          help="CSV de cadastro de operadoras")
    p_enrich.add_argument("--output", required=True,
                          help="CSV de saída enriquecido")
    p_enrich.set_defaults(func=cmd_enrich)

    p_val = subparsers.add_parser("validate", help="Valida o CSV enriquecido")
    p_val.add_argument("--input", required=True, help="CSV de entrada")
    p_val.add_argument("--output", required=True, help="CSV de saída")
    p_val.add_argument("--reject-invalid", action="store_true",
                       help="Descarta linhas inválidas")
    p_val.set_defaults(func=cmd_validate)

    p_agg = subparsers.add_parser(
        "aggregate", help="Agrega despesas por RazaoSocial/UF")
    p_agg.add_argument("--input", required=True, help="CSV validado")
    p_agg.add_argument("--output", required=True, help="CSV de saída agregado")
    p_agg.set_defaults(func=cmd_aggregate)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
