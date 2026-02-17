from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from airfoil_lny.core.optimization.study import run_study

APP_ROOT = Path(__file__).resolve().parents[3]  # airfoil-lny/
RUNS_DIR = APP_ROOT / "data" / "runs"
CONFIGS_DIR = APP_ROOT / "configs"

app = FastAPI(title="Airfoil LnY API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def _safe_join(base: Path, rel: str) -> Path:
    target = (base / rel).resolve()
    base_res = base.resolve()
    if base_res != target and base_res not in target.parents:
        raise HTTPException(status_code=400, detail="Invalid path")
    return target

@app.get("/api/runs")
def list_runs():
    if not RUNS_DIR.exists():
        return {"runs": []}
    runs = sorted([d.name for d in RUNS_DIR.iterdir() if d.is_dir()], reverse=True)
    return {"runs": runs}

@app.get("/api/run/{run_id}/summary")
def run_summary(run_id: str):
    p = _safe_join(RUNS_DIR, f"{run_id}/study_summary.json")
    if not p.exists():
        raise HTTPException(status_code=404, detail="Run not found")
    return json.loads(p.read_text())

@app.get("/api/run/{run_id}/exports")
def list_exports(run_id: str):
    exp = _safe_join(RUNS_DIR, f"{run_id}/exports")
    if not exp.exists():
        raise HTTPException(status_code=404, detail="Exports not found")
    files = sorted([str(f.relative_to(RUNS_DIR / run_id)) for f in exp.rglob("*") if f.is_file()])
    return {"files": files}

@app.get("/api/run/{run_id}/file")
def get_file(run_id: str, rel: str):
    p = _safe_join(RUNS_DIR, f"{run_id}/{rel}")
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(p)

class StartRequest(BaseModel):
    config_name: str = "baseline.yaml"

@app.post("/api/start")
def start_optimization(req: StartRequest):
    cfg_path = _safe_join(CONFIGS_DIR, req.config_name)
    if not cfg_path.exists():
        raise HTTPException(status_code=404, detail=f"Config not found: {req.config_name}")
    run_dir = run_study(cfg_path)
    return {"run_id": run_dir.name}
