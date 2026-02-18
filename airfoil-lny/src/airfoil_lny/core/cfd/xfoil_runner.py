from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess
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

    # XFOIL script - convergence iyileştirmeleriyle
    commands = [
        "PLOP",
        "G",
        "",  # PLOP'tan çık
        f"LOAD {airfoil_dat_path.name}",
        "PANE",  # Otomatik panelleme
        "OPER",
        f"VISC {Re}",
        f"MACH {Mach}",
        "ITER 200",  # İterasyon limitini artır (default ~100)
        "VPAR",
        f"N {xfoil.ncrit}",
        "",  # VPAR'dan çık
        "PACC",
        f"{out_polar_path.name}",
        "",  # dump dosyası yok
        f"ASEQ {aoa_start} {aoa_end} {aoa_step}",
        "",  # OPER'de kal
        "PACC",  # PACC kapat
        "",  # OPER'den çık
        "QUIT",
    ]
    script = "\n".join(commands) + "\n"

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
