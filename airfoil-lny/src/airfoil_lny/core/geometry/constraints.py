from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ConstraintResult:
    ok: bool
    values: dict
    penalty: float

def evaluate_constraints(params: dict, cfg_constraints: dict) -> ConstraintResult:
    t = float(params["t"])
    vals = {"t": t}
    penalty = 0.0
    ok = True

    if "max_thickness" in cfg_constraints:
        tmax = float(cfg_constraints["max_thickness"]["target"])
        if t > tmax:
            ok = False
            penalty += (t - tmax)

    if "min_thickness" in cfg_constraints:
        tmin = float(cfg_constraints["min_thickness"]["target"])
        if t < tmin:
            ok = False
            penalty += (tmin - t)

    return ConstraintResult(ok=ok, values=vals, penalty=penalty)
