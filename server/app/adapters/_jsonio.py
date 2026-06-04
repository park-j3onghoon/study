"""Tiny JSON/text I/O helpers shared by disk-backed adapters."""
import json
import os
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    _atomic_write(path, content)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    _atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False))


def _atomic_write(path: Path, content: str) -> None:
    # Write to a sibling temp file then os.replace — a same-directory rename is
    # atomic on POSIX, so readers never observe a half-written file.
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
