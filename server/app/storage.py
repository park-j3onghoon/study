"""디스크 R/W 추상화. lessons/ 와 conversations/ 두 폴더만 다룬다."""
import json
from pathlib import Path
from typing import Any

from .config import settings


def lessons_root() -> Path:
    path = Path(settings.lessons_dir).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def conversations_root() -> Path:
    path = Path(settings.conversations_dir).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(data, indent=2, ensure_ascii=False)
    path.write_text(serialized, encoding="utf-8")
