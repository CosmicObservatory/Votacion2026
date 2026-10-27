"""Repara shapefiles del INE con anillos de polígono sin cerrar.

Algunas capas publicadas en https://pautas.ine.mx/transparencia/mapas/
traen anillos cuyo último vértice difiere del primero por ~1e-9 a 1e-4 m
(redondeo de coordenadas en la exportación). GEOS/pyogrio (engine por
defecto de geopandas) exige cierre exacto y lanza:

    IllegalArgumentException: Points of LinearRing do not form a
    closed linestring

Este script detecta esos registros a nivel binario y copia el primer
vértice sobre el último (parche de 16 bytes por anillo; el tamaño del
archivo y el índice .shx no cambian). Casos conocidos en 2019/2020:
ENTIDAD (Tlaxcala) y SECCION.

Uso:
    python -m vothmo.repair_shp            # repara data/Mapas
    python -m vothmo.repair_shp --check    # solo reporta, no modifica
    python -m vothmo.repair_shp RUTA_DIR   # otro directorio con .shp
"""

import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from vothmo.config import FOLDER_DATA

# Tipos de geometría con anillos: Polygon, PolygonZ, PolygonM, MultiPatch
POLYGON_TYPES = {5, 15, 25, 31}
SHP_HEADER = 100


def find_unclosed_rings(data: bytes | bytearray) -> list[tuple[int, int, int]]:
    """Devuelve [(byte_offset_ultimo_punto, off_primero, npts), ...]."""
    bad = []
    pos = SHP_HEADER
    while pos + 8 <= len(data):
        content_len = struct.unpack(">i", data[pos + 4 : pos + 8])[0] * 2
        shape_type = struct.unpack("<i", data[pos + 8 : pos + 12])[0]
        if shape_type in POLYGON_TYPES:
            num_parts, num_points = struct.unpack(
                "<ii", data[pos + 44 : pos + 52]
            )
            parts = np.frombuffer(
                data, dtype="<i4", count=num_parts, offset=pos + 52
            )
            pts_off = pos + 52 + 4 * num_parts
            pts = np.frombuffer(
                data, dtype="<f8", count=2 * num_points, offset=pts_off
            ).reshape(-1, 2)
            ends = np.append(parts[1:], num_points)
            for i in range(num_parts):
                s, e = parts[i], ends[i]
                if e - s >= 4 and not np.array_equal(pts[s], pts[e - 1]):
                    bad.append((pts_off + 16 * (e - 1), pts_off + 16 * s, e - s))
        pos += 8 + content_len
    return bad


def repair_file(shp: Path, check_only: bool = False) -> tuple[int, int]:
    """Repara los anillos abiertos de un .shp. Devuelve (anillos, delta_max)."""
    data = bytearray(shp.read_bytes())
    bad = find_unclosed_rings(data)
    if not bad or check_only:
        return len(bad), 0

    backup = shp.with_suffix(
        shp.suffix + "." + datetime.now().strftime("%Y%m%d%H%M%S") + ".bak"
    )
    shutil.copy2(shp, backup)
    for last_off, first_off, _ in bad:
        data[last_off : last_off + 16] = data[first_off : first_off + 16]
    shp.write_bytes(data)
    return len(bad), backup


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    check_only = "--check" in sys.argv
    root = Path(args[0]) if args else FOLDER_DATA / "Mapas"

    shp_files = sorted(root.rglob("*.shp")) + sorted(root.rglob("*.SHP"))
    if not shp_files:
        print(f"No hay shapefiles en {root}")
        return 1

    total = 0
    for shp in shp_files:
        stem = shp.with_suffix("")
        missing = [
            ext
            for ext in (".dbf", ".shx")
            if not stem.with_suffix(ext).exists()
            and not stem.with_suffix(ext.upper()).exists()
        ]
        if missing:
            print(f"ERROR  {shp.relative_to(root)}: faltan {missing}")
            continue

        n, info = repair_file(shp, check_only)
        if n:
            total += n
            tag = "ABIERTOS" if check_only else "REPARADO"
            extra = f" (respaldo: {info.name})" if info else ""
            print(f"{tag}  {shp.relative_to(root)}: {n} anillos{extra}")

    if total == 0:
        print("Todos los shapefiles están correctos.")
    elif check_only:
        print(f"\n{total} anillos abiertos encontrados (sin modificar).")
    else:
        print(f"\n{total} anillos reparados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
