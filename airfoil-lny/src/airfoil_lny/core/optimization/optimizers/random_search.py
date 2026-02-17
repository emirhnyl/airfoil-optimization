from __future__ import annotations
import numpy as np

class RandomSearchOptimizer:
    def __init__(self, bounds: dict, n_candidates_per_iter: int, seed: int = 0):
        self.bounds = bounds
        self.n_candidates = int(n_candidates_per_iter)
        self.rng = np.random.default_rng(seed)

    def ask(self) -> list[dict]:
        cands = []
        for _ in range(self.n_candidates):
            cand = {}
            for k, (lo, hi) in self.bounds.items():
                cand[k] = float(self.rng.uniform(float(lo), float(hi)))
            cands.append(cand)
        return cands
