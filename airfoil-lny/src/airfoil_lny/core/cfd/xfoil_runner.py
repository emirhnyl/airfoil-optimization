import subprocess
import os
import tempfile


def run_xfoil(airfoil_dat, alpha=5, re=1e6, mach=0.0, timeout=20):
    """
    Runs XFOIL for given airfoil file and returns (CL, CD).
    Returns None if XFOIL fails.
    """

    if not os.path.exists(airfoil_dat):
        print("DAT file not found:", airfoil_dat)
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        polar_path = os.path.join(tmpdir, "polar.txt")

        cmd = f"""
LOAD {airfoil_dat}
PANE
OPER
VISC {re}
MACH {mach}
ITER 200
PACC
{polar_path}

ALFA {alpha}
PACC
QUIT
"""

        try:
            process = subprocess.Popen(
                ["xfoil"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            out, err = process.communicate(cmd, timeout=timeout)
            print("--- XFOIL STDOUT ---")
            print(out)
            print("--- XFOIL STDERR ---")
            print(err)
        except Exception as e:
            print("XFOIL execution error:", e)
            return None

        # Polar dosyası oluşmadıysa -> başarısız
        if not os.path.exists(polar_path):
            return None

        # Polar parse
        try:
            with open(polar_path, "r") as f:
                lines = f.readlines()

            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        cl = float(parts[1])
                        cd = float(parts[2])
                        return cl, cd
                    except:
                        continue

        except:
            return None

    return None