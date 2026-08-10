import argparse
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import httpx

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

FITZPATRICK17K_CSV_URL = (
    "https://raw.githubusercontent.com/mattgroh/fitzpatrick17k/main/fitzpatrick17k.csv"
)
FIGSHARE_API_URL = "https://api.figshare.com/v2/articles/{article_id}"
MEMI_DS_ARTICLE_ID = 29209229
MEMI_DS_FILES_URL = "https://ndownloader.figshare.com/files/{file_id}"
ACNE04_HF_REPO = "ManuelHettich/acne04"


def _download(url: str, target: Path) -> None:
    if target.exists() and target.stat().st_size > 0:
        print(f"Ya existe, omitiendo: {target}")
        return
    print(f"Descargando {url} -> {target}")
    with httpx.stream("GET", url, follow_redirects=True, timeout=600.0) as response:
        response.raise_for_status()
        with target.open("wb") as handle:
            for chunk in response.iter_bytes(chunk_size=1 << 20):
                handle.write(chunk)
    print(f"OK: {target} ({target.stat().st_size / 1e6:.1f} MB)")


def _figshare_files(article_id: int) -> list[dict]:
    with httpx.Client(timeout=60.0) as client:
        response = client.get(FIGSHARE_API_URL.format(article_id=article_id))
        response.raise_for_status()
        return response.json()["files"]


def _download_figshare_file(file_meta: dict, out_dir: Path) -> tuple[str, Path]:
    name = file_meta["name"]
    ext = Path(name).suffix.lower()
    if ext == ".jpg":
        target = out_dir / "images" / name
    elif ext == ".png":
        target = out_dir / "masks" / name
    else:
        target = out_dir / name
    if target.exists() and target.stat().st_size > 0:
        return name, target
    url = MEMI_DS_FILES_URL.format(file_id=file_meta["id"])
    for attempt in range(3):
        try:
            with httpx.stream("GET", url, follow_redirects=True, timeout=300.0) as response:
                response.raise_for_status()
                with target.open("wb") as handle:
                    for chunk in response.iter_bytes(chunk_size=1 << 20):
                        handle.write(chunk)
            return name, target
        except httpx.HTTPError as exc:
            target.unlink(missing_ok=True)
            print(f"Reintento {attempt + 1}/3 para {name}: {exc}")
            time.sleep(1.0 + attempt)
    raise SystemExit(f"No se pudo descargar {name}")


def download_fitzpatrick17k() -> Path:
    out_dir = DATA_DIR / "fitzpatrick17k"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "fitzpatrick17k.csv"
    _download(FITZPATRICK17K_CSV_URL, target)
    return target


def download_memi_ds() -> Path:
    out_dir = DATA_DIR / "memi-ds"
    (out_dir / "images").mkdir(parents=True, exist_ok=True)
    (out_dir / "masks").mkdir(parents=True, exist_ok=True)
    files = _figshare_files(MEMI_DS_ARTICLE_ID)
    print(f"Descargando {len(files)} archivos de MEMI-DS...")
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(_download_figshare_file, file_meta, out_dir): file_meta["name"]
            for file_meta in files
        }
        for future in as_completed(futures):
            name, target = future.result()
            print(f"OK {target.relative_to(out_dir)} ({name})")
    return out_dir


def download_acne04_hf() -> Path:
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        sys.exit('Requiere: pip install -e ".[data]" (huggingface_hub)')
    target = DATA_DIR / "acne04-hf"
    target.mkdir(parents=True, exist_ok=True)
    print("Descargando ACNE04 desde HuggingFace (puede tardar)...")
    snapshot_download(repo_id=ACNE04_HF_REPO, repo_type="dataset", local_dir=target)
    return target


def download_roboflow(workspace: str, project: str) -> Path:
    api_key = os.environ.get("RF_API_KEY")
    if not api_key:
        sys.exit("Variable RF_API_KEY requerida (cuenta gratuita en roboflow.com)")
    try:
        from roboflow import Roboflow
    except ImportError:
        sys.exit('Requiere: pip install -e ".[data]" (roboflow)')
    rf = Roboflow(api_key=api_key)
    target = str(DATA_DIR / f"roboflow-{workspace}-{project}")
    print(f"Descargando Roboflow {workspace}/{project}...")
    dataset = (
        rf.workspace(workspace).project(project).version(1).download("yolov8", location=target)
    )
    return Path(dataset.location)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descarga datasets públicos de skin analysis (ver docs/DATASETS.md)"
    )
    parser.add_argument(
        "--dataset",
        choices=["fitzpatrick17k", "memi-ds", "acne04-hf", "roboflow"],
        required=True,
    )
    parser.add_argument("--workspace", default=None, help="Workspace de Roboflow")
    parser.add_argument("--project", default=None, help="Proyecto de Roboflow")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.dataset == "fitzpatrick17k":
        print(download_fitzpatrick17k())
    elif args.dataset == "memi-ds":
        print(download_memi_ds())
    elif args.dataset == "acne04-hf":
        print(download_acne04_hf())
    elif args.dataset == "roboflow":
        if not args.workspace or not args.project:
            sys.exit("roboflow requiere --workspace y --project")
        print(download_roboflow(args.workspace, args.project))


if __name__ == "__main__":
    main()
