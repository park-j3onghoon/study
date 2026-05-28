"""Disk-backed ConversationRepository. One JSON file per conversation: {root}/{id}.json"""
from datetime import datetime
from pathlib import Path

from ..domain.exceptions import InvalidConversationId
from ..domain.models import Conversation, ConversationId, ConversationSummary
from ..domain.ports import ConversationRepository
from . import _jsonio


class DiskConversationRepository(ConversationRepository):
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, conversation: Conversation) -> None:
        _jsonio.write_json(self._path(conversation.id), {
            "id": conversation.id.value,
            "title": conversation.title,
            "created": conversation.created.isoformat(),
            "messages": list(conversation.messages),
        })

    def find(self, id: ConversationId) -> Conversation | None:
        path = self._path(id)
        if not path.exists():
            return None
        data = _jsonio.read_json(path)
        return Conversation(
            id=ConversationId(data["id"]),
            title=data["title"],
            created=datetime.fromisoformat(data["created"]),
            messages=tuple(data.get("messages", [])),
        )

    def list_summaries(self) -> list[ConversationSummary]:
        summaries: list[ConversationSummary] = []
        for path in sorted(self.root.glob("*.json")):
            data = _jsonio.read_json(path)
            try:
                cid = ConversationId(data["id"])
            except (InvalidConversationId, KeyError):
                continue
            summaries.append(ConversationSummary(
                id=cid,
                title=data["title"],
                created=datetime.fromisoformat(data["created"]),
                message_count=len(data.get("messages", [])),
            ))
        summaries.sort(key=lambda s: s.created, reverse=True)
        return summaries

    def exists(self, id: ConversationId) -> bool:
        return self._path(id).exists()

    def _path(self, id: ConversationId) -> Path:
        # ConversationId regex (^[0-9a-f]{32}$) prevents path traversal.
        return self.root / f"{id.value}.json"
