# metashapes/utils/metaconv.py

# This module provides utility functions for converting metasurface objects to different formats.

import json
from pathlib import Path
from typing import List, Dict, Any, Iterator
from metashapes.metasurface import Metasurface

# --- Saving to JSON ---
def metasurfaces_to_json(metasurfaces: List['Metasurface'], *, pretty: bool = True) -> str:
    return json.dumps(
        [m.to_parametric() for m in metasurfaces],
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        sort_keys=True,
    )

def save_metasurfaces_json(path: str | Path, metasurfaces: List['Metasurface'], *, pretty: bool = True) -> None:
    Path(path).write_text(metasurfaces_to_json(metasurfaces, pretty=pretty), encoding="utf-8")

# Optional: NDJSON (one metasurface per line)
def save_metasurfaces_ndjson(path: str | Path, metasurfaces: List['Metasurface']) -> None:
    p = Path(path)
    p.write_text(
        "\n".join(json.dumps(m.to_parametric(), ensure_ascii=False) for m in metasurfaces),
        encoding="utf-8",
    )

# --- Reading from JSON ---
REQUIRED_KEYS = {"shapes", "canvas", "thickness", "inverted", "id"}

def _validate(d: Dict[str, Any]) -> None:
    missing = REQUIRED_KEYS - d.keys()
    if missing:
        raise ValueError(f"Parametric metasurface is missing keys: {sorted(missing)}")

def metasurfaces_from_json_str(s: str) -> List["Metasurface"]:
    """
    Expect a JSON array of metasurface dicts (as written by metasurfaces_to_json_str).
    Also supports an object with key 'metasurfaces'.
    """
    data = json.loads(s)
    if isinstance(data, dict) and "metasurfaces" in data:
        data = data["metasurfaces"]
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list of metasurfaces.")
    metas: List["Metasurface"] = []
    for i, d in enumerate(data):
        if not isinstance(d, dict):
            raise ValueError(f"Item #{i} is not an object.")
        _validate(d)
        metas.append(Metasurface.from_parametric(d))
    return metas

def load_metasurfaces_json(path: str | Path) -> List["Metasurface"]:
    """
    Load from a JSON file that contains an array (or {'metasurfaces': [...]})
    """
    s = Path(path).read_text(encoding="utf-8")
    return metasurfaces_from_json_str(s)

def iter_metasurfaces_from_ndjson(path: str | Path) -> Iterator["Metasurface"]:
    """
    Stream metasurfaces from an NDJSON file (one metasurface per line).
    """
    with Path(path).open("r", encoding="utf-8") as f:
        for ln, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if not isinstance(d, dict):
                raise ValueError(f"Line {ln}: not a JSON object.")
            _validate(d)
            yield Metasurface.from_parametric(d)

def load_metasurfaces_ndjson(path: str | Path) -> List["Metasurface"]:
    """
    Eagerly read all metasurfaces from NDJSON.
    """
    return list(iter_metasurfaces_from_ndjson(path))