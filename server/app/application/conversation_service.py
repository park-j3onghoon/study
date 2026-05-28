"""ConversationService — use cases for chat history. Strict CQS."""
from datetime import datetime, timezone

from ..domain.exceptions import ConversationNotFound
from ..domain.models import Conversation, ConversationId, ConversationSummary
from ..domain.ports import ConversationRepository


class ConversationService:
    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    # ── Commands ────────────────────────────────────────────────────────────
    def create(self, id: ConversationId, title: str) -> None:
        self.repo.save(Conversation(
            id=id,
            title=title,
            created=datetime.now(timezone.utc),
            messages=(),
        ))

    def add_turn(self, id: ConversationId, user_content: str, assistant_content: str) -> None:
        conv = self.repo.find(id)
        if conv is None:
            raise ConversationNotFound(id.value)
        self.repo.save(conv.add_turn(user_content, assistant_content))

    # ── Queries ─────────────────────────────────────────────────────────────
    def get(self, id: ConversationId) -> Conversation:
        conv = self.repo.find(id)
        if conv is None:
            raise ConversationNotFound(id.value)
        return conv

    def find(self, id: ConversationId) -> Conversation | None:
        return self.repo.find(id)

    def list_summaries(self) -> list[ConversationSummary]:
        return self.repo.list_summaries()
