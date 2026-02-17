from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv
from .utils import ensure_dir, write_json

@dataclass
class IterRecord:
    it: int
    params: dict
    constraints: dict
    penalty: float
    L: float   # burada L = CL
    D: float   # burada D = CD
    score: float

class Tracker:
    def __init__(self, run_dir: Path):
        self.run_dir = ensure_dir(run_dir)
        self.history_path = self.run_dir / "history.csv"
        self.best_path = self.run_dir / "best.json"
        self._best: IterRecord | None = None

        if not self.history_path.exists():
            with self.history_path.open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["it", "m", "p", "t", "penalty", "CL", "CD", "score"])

    @property
    def best(self) -> IterRecord | None:
        return self._best

    def log(self, rec: IterRecord) -> None:
        with self.history_path.open("a", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                rec.it,
                rec.params.get("m"),
                rec.params.get("p"),
                rec.params.get("t"),
                rec.penalty,
                rec.L,
                rec.D,
                rec.score,
            ])

        if (self._best is None) or (rec.score > self._best.score):
            self._best = rec
            write_json(self.best_path, {
                "it": rec.it,
                "params": rec.params,
                "constraints": rec.constraints,
                "penalty": rec.penalty,
                "CL": rec.L,
                "CD": rec.D,
                "score": rec.score,
            })
