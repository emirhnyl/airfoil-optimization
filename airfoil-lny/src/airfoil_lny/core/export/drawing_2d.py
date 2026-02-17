from __future__ import annotations
from pathlib import Path
import numpy as np

def airfoil_closed_polyline(xu, yu, xl, yl) -> tuple[np.ndarray, np.ndarray]:
    x_upper = np.array(xu)
    y_upper = np.array(yu)
    x_lower = np.array(xl)
    y_lower = np.array(yl)

    x_poly = np.concatenate([x_upper[::-1], x_lower[1:]])
    y_poly = np.concatenate([y_upper[::-1], y_lower[1:]])
    return x_poly, y_poly

def export_svg(poly_x, poly_y, out_path: Path, margin: float = 0.05):
    xmin, xmax = float(poly_x.min()), float(poly_x.max())
    ymin, ymax = float(poly_y.min()), float(poly_y.max())
    dx = xmax - xmin
    dy = ymax - ymin
    xmin -= margin * dx
    xmax += margin * dx
    ymin -= margin * dy
    ymax += margin * dy

    pts = " ".join([f"{x:.6f},{-y:.6f}" for x, y in zip(poly_x, poly_y)])
    stroke_w = (xmax - xmin) / 900.0

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{xmin:.6f} {-ymax:.6f} {xmax-xmin:.6f} {ymax-ymin:.6f}">
  <polyline points="{pts}" fill="none" stroke="black" stroke-width="{stroke_w:.6f}" />
</svg>
"""
    out_path.write_text(svg)

def export_dxf_polyline(poly_x, poly_y, out_path: Path):
    n = len(poly_x)
    lines: list[str] = []
    lines += ["0", "SECTION", "2", "ENTITIES"]
    lines += ["0", "LWPOLYLINE"]
    lines += ["8", "0"]
    lines += ["90", str(n)]
    lines += ["70", "1"]
    for x, y in zip(poly_x, poly_y):
        lines += ["10", f"{float(x):.6f}", "20", f"{float(y):.6f}"]
    lines += ["0", "ENDSEC", "0", "EOF"]
    out_path.write_text("\n".join(lines))
