"""Disk-backed ConversationRepository. One JSON file per conversation: {root}/{id}.json"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ..domain.models import Conversation, ConversationId, ConversationSummary
from ..domain.ports import ConversationRepository


class DiskConversationRepository(ConversationRepository):
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    # ── Commands ────────────────────────────────────────────────────────────
    def save(self, conversation: Conversation) -> None:
        _write_json(self._path(conversation.id), {
            "id": conversation.id.value,
            "title": conversation.title,
            "created": conversation.created.isoformat(),
            "messages": list(conversation.messages),
        })

    # ── Queries ─────────────────────────────────────────────────────────────
    def find(self, id: ConversationId) -> Conversation | None:
        path = self._path(id)
        if not path.exists():
            return None
        data = _read_json(path)
        return Conversation(
            id=ConversationId(data["id"]),
            title=data["title"],
            created=datetime.fromisoformat(data["created"]),
            messages=tuple(data.get("messages", [])),
        )

    def list_summaries(self) -> list[ConversationSummary]:
        summaries: list[ConversationSummary] = []
        for path in sorted(self.root.glob("*.json")):
            data = _read_json(path)
            try:
                cid = ConversationId(data["id"])
            except Exception:
                continue
            summaries.append(ConversationSummary(
                id=cid,
                title=data["title"],
                created=datetime.fromisoformat(data["created"]),
                message_count=len(data.get("messages", [])),
            ))
        # newest first
        summaries.sort(key=lambda s: s.created, reverse=True)
        return summaries

    def exists(self, id: ConversationId) -> bool:
        return self._path(id).exists()

    def _path(self, id: ConversationId) -> Path:
        return self.root / f"{id.value}.json"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
