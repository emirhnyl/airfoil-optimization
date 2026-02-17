from __future__ import annotations
import numpy as np

def cosine_spacing(n: int) -> np.ndarray:
    beta = np.linspace(0.0, np.pi, n)
    return (1 - np.cos(beta)) / 2

def naca4_coords(m: float, p: float, t: float, n_points: int = 181):
    x = cosine_spacing(n_points)

    yt = 5 * t * (
        0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4
    )

    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)
    for i, xi in enumerate(x):
        if p <= 1e-9:
            yc[i] = 0.0
            dyc_dx[i] = 0.0
        elif xi < p:
            yc[i] = m/(p**2) * (2*p*xi - xi**2)
            dyc_dx[i] = 2*m/(p**2) * (p - xi)
        else:
            yc[i] = m/((1-p)**2) * ((1 - 2*p) + 2*p*xi - xi**2)
            dyc_dx[i] = 2*m/((1-p)**2) * (p - xi)

    theta = np.arctan(dyc_dx)

    xu = x - yt*np.sin(theta)
    yu = yc + yt*np.cos(theta)
    xl = x + yt*np.sin(theta)
    yl = yc - yt*np.cos(theta)

    return x, xu, yu, xl, yl
