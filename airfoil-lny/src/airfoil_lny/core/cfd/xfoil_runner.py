from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess
import textwrap
import time
import shutil

@dataclass
class XFoilConfig:
    exe: str
    timeout_sec: int = 20
    ncrit: float = 9.0
    xtr_top: float = 1.0
    xtr_bot: float = 1.0

def run_xfoil_polar(
    *,
    xfoil: XFoilConfig,
    airfoil_dat_path: Path,
    out_polar_path: Path,
    Re: float,
    Mach: float,
    aoa_start: float,
    aoa_end: float,
    aoa_step: float,
    work_dir: Path,
) -> tuple[int, str]:
    work_dir.mkdir(parents=True, exist_ok=True)

    exe = xfoil.exe
    if exe == "xfoil":
        found = shutil.which("xfoil")
        if found:
            exe = found

    script = textwrap.dedent(f"""
    PLOP
    G

    LOAD {airfoil_dat_path.as_posix()}

    PANE

    OPER
    VISC {Re}
    MACH {Mach}
    VPAR
    N {xfoil.ncrit}
    XTR {xfoil.xtr_top} {xfoil.xtr_bot}

    PACC
    {out_polar_path.as_posix()}

    ASEQ {aoa_start} {aoa_end} {aoa_step}

    PACC

    QUIT
    """).strip() + "\n"

    t0 = time.time()
    try:
        proc = subprocess.run(
            [exe],
            input=script,
            text=True,
            capture_output=True,
            cwd=str(work_dir),
            timeout=xfoil.timeout_sec,
        )
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        out += f"\n[elapsed_sec={time.time()-t0:.2f}]"
        return proc.returncode, out
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") + "\n" + (e.stderr or "")
        return 124, f"XFOIL TIMEOUT after {xfoil.timeout_sec}s\n{out}"
