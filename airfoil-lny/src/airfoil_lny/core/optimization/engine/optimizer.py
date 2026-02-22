import random
import json
from pathlib import Path

from airfoil_lny.core.cfd.xfoil_runner import run_xfoil


def run_optimization(run_dir: Path):

    population_size = 10
    generations = 5

    best_score = -999
    history = []

    population = [random.uniform(0.08, 0.15) for _ in range(population_size)]

    for gen in range(generations):

        print(f"GENERATION {gen}")

        scores = []


        for thickness in population:
            result = run_xfoil(thickness)
            if result is None:
                continue
            score = result["cl"] / result["cd"]
            scores.append((thickness, score))
            history.append({
                "gen": gen,
                "thickness": thickness,
                "score": score,
            })
            if score > best_score:
                best_score = score

        scores.sort(key=lambda x: x[1], reverse=True)

        survivors = [s[0] for s in scores[:5]]

        population = survivors + [
            s + random.uniform(-0.01, 0.01)
            for s in survivors
        ]

    with open(run_dir / "history.json", "w") as f:
        json.dump(history, f, indent=2)

    return {"best_score": best_score}