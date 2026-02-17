from __future__ import annotations
from pathlib import Path
import re

def parse_xfoil_polar(polar_path: Path) -> list[dict]:
    txt = polar_path.read_text(errors="ignore").splitlines()
    rows: list[dict] = []

    for line in txt:
        s = line.strip()
        if not s:
            continue
        if re.search(r"[A-Za-z]", s):
            continue
        parts = s.split()
        if len(parts) < 7:
            continue
        try:
            rows.append({
                "alpha": float(parts[0]),
                "cl": float(parts[1]),
                "cd": float(parts[2]),
                "cdp": float(parts[3]),
                "cm": float(parts[4]),
                "top_xtr": float(parts[5]),
                "bot_xtr": float(parts[6]),
            })
        except ValueError:
            continue

    return rows

def pick_nearest_alpha(rows: list[dict], target_alpha: float) -> dict | None:
    if not rows:
        return None
    return min(rows, key=lambda r: abs(r["alpha"] - target_alpha))
