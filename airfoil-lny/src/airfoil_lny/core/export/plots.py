from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt

def plot_polars(rows: list[dict], out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    alpha = [r["alpha"] for r in rows]
    cl = [r["cl"] for r in rows]
    cd = [r["cd"] for r in rows]
    ld = [(r["cl"] / r["cd"]) if r["cd"] > 0 else 0.0 for r in rows]

    def save(figpath: Path):
        plt.tight_layout()
        plt.savefig(figpath, dpi=200)
        plt.close()

    plt.figure()
    plt.plot(alpha, cl)
    plt.xlabel("AoA (deg)")
    plt.ylabel("CL")
    plt.grid(True)
    save(out_dir / "cl_vs_aoa.png")

    plt.figure()
    plt.plot(alpha, cd)
    plt.xlabel("AoA (deg)")
    plt.ylabel("CD")
    plt.grid(True)
    save(out_dir / "cd_vs_aoa.png")

    plt.figure()
    plt.plot(alpha, ld)
    plt.xlabel("AoA (deg)")
    plt.ylabel("L/D")
    plt.grid(True)
    save(out_dir / "ld_vs_aoa.png")

    plt.figure()
    plt.plot(cd, cl)
    plt.xlabel("CD")
    plt.ylabel("CL")
    plt.grid(True)
    save(out_dir / "cl_vs_cd.png")
