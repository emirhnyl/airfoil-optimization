from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))

def read_yaml(path: Path) -> dict:
    import yaml
    return yaml.safe_load(path.read_text())
