from pathlib import Path
import zipfile


def extract_zip(zip_path: Path, out_dir: Path) -> Path:
    target = out_dir / zip_path.stem
    target.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(target)

    return target


def run(zips_dir: Path, extracted_dir: Path) -> list[Path]:
    extracted = []

    for zp in sorted(zips_dir.glob("*.zip")):
        extracted.append(extract_zip(zp, extracted_dir))

    return extracted
