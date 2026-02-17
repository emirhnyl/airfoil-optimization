from __future__ import annotations
from pathlib import Path
import zipfile

def zip_outputs(out_dir: Path, zip_path: Path):
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in out_dir.rglob("*"):
            if p.is_file():
                z.write(p, arcname=str(p.relative_to(out_dir)))
