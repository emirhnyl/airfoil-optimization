from __future__ import annotations
from pathlib import Path
import typer

from airfoil_lny.core.reporting.utils import read_yaml, ensure_dir, timestamp_slug, write_json
from airfoil_lny.core.reporting.tracker import Tracker, IterRecord
from airfoil_lny.core.geometry.parametric import naca4_coords
from airfoil_lny.core.geometry.constraints import evaluate_constraints
from airfoil_lny.core.optimization.optimizers.random_search import RandomSearchOptimizer

from airfoil_lny.core.cfd.xfoil_runner import XFoilConfig, run_xfoil_polar
from airfoil_lny.core.cfd.xfoil_parse import parse_xfoil_polar, pick_nearest_alpha

from airfoil_lny.core.export.drawing_2d import airfoil_closed_polyline, export_svg, export_dxf_polyline
from airfoil_lny.core.export.plots import plot_polars
from airfoil_lny.core.export.mesh_3mf import write_3mf_from_polyline
from airfoil_lny.core.export.packager import zip_outputs


app = typer.Typer(add_completion=False)


def _make_run_dir(cfg: dict) -> Path:
    out_dir = Path(cfg["project"]["out_dir"])
    if not out_dir.is_absolute():
        out_dir = PROJECT_ROOT / out_dir
    name = cfg["project"]["name"]
    run_dir = out_dir / f"{name}_{timestamp_slug()}"
    return ensure_dir(run_dir)


def _write_dat(dat_path: Path, px, py, title: str):
    with dat_path.open("w") as f:
        f.write(f"{title}\n")
        for xx, yy in zip(px, py):
            f.write(f"{float(xx):.7f} {float(yy):.7f}\n")


def _score_ld(cl: float, cd: float) -> float:
    if cd <= 0:
        return -1e9
    return cl / cd


def run_study(config_path: Path) -> Path:
    cfg = read_yaml(config_path)

    run_dir = _make_run_dir(cfg)
    write_json(run_dir / "config_resolved.json", cfg)

    seed = int(cfg["study"].get("seed", 0))
    n_iters = int(cfg["study"].get("n_iters", 30))

    bounds = cfg["design_vars"]["bounds"]
    opt_cfg = cfg["optimizer"]
    optimizer = RandomSearchOptimizer(
        bounds=bounds,
        n_candidates_per_iter=int(opt_cfg.get("n_candidates_per_iter", 30)),
        seed=seed,
    )

    tracker = Tracker(run_dir=run_dir)
    penalty_weight = float(cfg["objective"].get("penalty_weight", 50.0))
    aoa0 = float(cfg["objective"].get("aoa_deg", 4.0))

    flow = cfg.get("flow", {})
    Re = float(flow.get("Re", 8e5))
    Mach = float(flow.get("Mach", 0.0))
    ncrit = float(flow.get("ncrit", 9))
    xtr_top = float(flow.get("xtr_top", 1.0))
    xtr_bot = float(flow.get("xtr_bot", 1.0))

    geom_cfg = cfg.get("geometry", {})
    n_points = int(geom_cfg.get("n_points", 181))
    constraints_cfg = cfg.get("constraints", {})

    xcfg = cfg.get("xfoil", {})
    xfoil_cfg = XFoilConfig(
        exe=str(xcfg.get("executable", "xfoil")),
        timeout_sec=int(xcfg.get("timeout_sec", 20)),
        ncrit=ncrit,
        xtr_top=xtr_top,
        xtr_bot=xtr_bot,
    )
    max_retries = int(xcfg.get("max_retries", 1))

    baseline = geom_cfg.get("naca4", {"m": 0.02, "p": 0.4, "t": 0.12})
    write_json(run_dir / "baseline_params.json", baseline)

    tmp_dir = run_dir / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for it in range(n_iters):
        candidates = optimizer.ask()
        best_local: IterRecord | None = None

        for cand_i, cand in enumerate(candidates):
            # 1) geometry
            _, xu, yu, xl, yl = naca4_coords(cand["m"], cand["p"], cand["t"], n_points)
            px, py = airfoil_closed_polyline(xu, yu, xl, yl)

            # 2) constraints
            cres = evaluate_constraints(cand, constraints_cfg)

            # 3) XFOIL (küçük sweep: aoa0 ± 0.5)
            cand_dir = tmp_dir / f"it{it:04d}_c{cand_i:03d}"
            cand_dir.mkdir(parents=True, exist_ok=True)
            dat_path = cand_dir / "airfoil.dat"
            polar_path = cand_dir / "polar.txt"
            _write_dat(dat_path, px, py, title="AIRFOIL_LNY")

            a0 = aoa0 - 0.5
            a1 = aoa0 + 0.5
            astep = 0.5

            rows = []
            for _try in range(max_retries + 1):
                code, out = run_xfoil_polar(
                    xfoil=xfoil_cfg,
                    airfoil_dat_path=dat_path,
                    out_polar_path=polar_path,
                    Re=Re,
                    Mach=Mach,
                    aoa_start=a0,
                    aoa_end=a1,
                    aoa_step=astep,
                    work_dir=cand_dir,
                )
                if code == 0 and polar_path.exists():
                    rows = parse_xfoil_polar(polar_path)
                    if rows:
                        break

            pick = pick_nearest_alpha(rows, aoa0)
            if pick is None:
                cl, cd = 0.0, 1e9
            else:
                cl, cd = float(pick["cl"]), float(pick["cd"])

            raw = _score_ld(cl, cd)
            score = raw - penalty_weight * float(cres.penalty)

            rec = IterRecord(
                it=it,
                params=cand,
                constraints=cres.values,
                penalty=float(cres.penalty),
                L=float(cl),  # CL
                D=float(cd),  # CD
                score=float(score),
            )

            if (best_local is None) or (rec.score > best_local.score):
                best_local = rec

        tracker.log(best_local)

    # ---- POSTPROCESS EXPORTS ----
    best = tracker.best
    if best is not None:
        pp = cfg.get("postprocess", {})
        aoa_s = float(pp.get("aoa_start", -2.0))
        aoa_e = float(pp.get("aoa_end", 10.0))
        aoa_st = float(pp.get("aoa_step", 0.5))
        thick_mm = float(pp.get("extrude_thickness_mm", 40.0))

        export_dir = run_dir / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        # best geometry
        _, xu, yu, xl, yl = naca4_coords(best.params["m"], best.params["p"], best.params["t"], n_points)
        px, py = airfoil_closed_polyline(xu, yu, xl, yl)

        # 2D + 3D exports
        export_svg(px, py, export_dir / "airfoil.svg")
        export_dxf_polyline(px, py, export_dir / "airfoil.dxf")
        write_3mf_from_polyline(px, py, thick_mm, export_dir / "airfoil.3mf")

        # best polar sweep for plots
        best_dir = run_dir / "best"
        best_dir.mkdir(parents=True, exist_ok=True)
        dat_path = best_dir / "airfoil_best.dat"
        polar_path = best_dir / "polar_best.txt"
        _write_dat(dat_path, px, py, title="AIRFOIL_LNY_BEST")

        code, out = run_xfoil_polar(
            xfoil=xfoil_cfg,
            airfoil_dat_path=dat_path,
            out_polar_path=polar_path,
            Re=Re,
            Mach=Mach,
            aoa_start=aoa_s,
            aoa_end=aoa_e,
            aoa_step=aoa_st,
            work_dir=best_dir,
        )

        rows = parse_xfoil_polar(polar_path) if polar_path.exists() else []
        if rows:
            plot_polars(rows, export_dir)
            write_json(export_dir / "polar.json", rows)

        # zip all exports
        zip_outputs(export_dir, run_dir / "download_all.zip")

        write_json(run_dir / "study_summary.json", {
            "run_dir": str(run_dir),
            "n_iters": n_iters,
            "best_score": best.score,
            "best_params": best.params,
            "exports": {
                "dir": str(export_dir),
                "download_all_zip": str(run_dir / "download_all.zip"),
            }
        })
    else:
        write_json(run_dir / "study_summary.json", {
            "run_dir": str(run_dir),
            "n_iters": n_iters,
            "best_score": None,
            "best_params": None,
        })

    return run_dir


@app.command()
def run(config: Path = typer.Option(..., exists=True, help="Path to YAML config")):
    run_dir = run_study(config)
    typer.echo(f"Done. Outputs in: {run_dir}")


if __name__ == "__main__":
    app()
