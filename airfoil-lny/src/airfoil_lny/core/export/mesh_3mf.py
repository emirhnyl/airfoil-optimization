from __future__ import annotations
from pathlib import Path
import zipfile
import numpy as np

def _triangulate_extrude(poly_x: np.ndarray, poly_y: np.ndarray, thickness_mm: float):
    z0 = 0.0
    z1 = float(thickness_mm)

    n = len(poly_x)
    vb = np.column_stack([poly_x, poly_y, np.full(n, z0)])
    vt = np.column_stack([poly_x, poly_y, np.full(n, z1)])
    V = np.vstack([vb, vt])

    tris = []

    # sides
    for i in range(n):
        j = (i + 1) % n
        bi, bj = i, j
        ti, tj = i + n, j + n
        tris.append([bi, bj, tj])
        tris.append([bi, tj, ti])

    # caps (fan)
    center_b = len(V)
    center_t = len(V) + 1
    V = np.vstack([V, [poly_x.mean(), poly_y.mean(), z0], [poly_x.mean(), poly_y.mean(), z1]])

    for i in range(1, n - 1):
        tris.append([center_b, i, i + 1])
        tris.append([center_t, i + n + 1, i + n])

    return V, np.array(tris, dtype=int)

def write_3mf_from_polyline(poly_x, poly_y, thickness_mm: float, out_3mf: Path):
    poly_x = np.asarray(poly_x, dtype=float)
    poly_y = np.asarray(poly_y, dtype=float)
    V, T = _triangulate_extrude(poly_x, poly_y, thickness_mm)

    vertices_xml = "\n".join(
        [f'<vertex x="{v[0]:.6f}" y="{v[1]:.6f}" z="{v[2]:.6f}"/>' for v in V]
    )
    triangles_xml = "\n".join(
        [f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in T]
    )

    model_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <resources>
    <object id="1" type="model">
      <mesh>
        <vertices>
          {vertices_xml}
        </vertices>
        <triangles>
          {triangles_xml}
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1"/>
  </build>
</model>
"""

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
"""

    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="/3D/3dmodel.model"/>
</Relationships>
"""

    out_3mf.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_3mf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model_xml)
