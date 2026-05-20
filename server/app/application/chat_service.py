"""Application service for streaming chat.

When conversation_id is provided, the user's last message + this turn's assistant
text are appended to the conversation after the stream completes. Tool/thinking
events are not persisted (only the final user-visible exchange).
"""
from typing import AsyncIterator

from ..domain.exceptions import ConversationNotFound
from ..domain.models import ConversationId
from ..domain.ports import Agent
from .conversation_service import ConversationService


class ChatService:
    def __init__(self, agent: Agent, conversations: ConversationService):
        self.agent = agent
        self.conversations = conversations

    async def stream(
        self,
        messages: list[dict],
        model: str | None = None,
        thinking_budget: int | None = None,
        conversation_id: ConversationId | None = None,
    ) -> AsyncIterator[dict]:
        assistant_text_parts: list[str] = []
        async for event in self.agent.stream(
            messages=messages,
            model=model,
            thinking_budget=thinking_budget,
        ):
            if event.get("type") == "text_delta":
                assistant_text_parts.append(event.get("text", ""))
            yield event

        if conversation_id is not None:
            self._persist_turn(conversation_id, messages, assistant_text_parts)

    def _persist_turn(
        self,
        conversation_id: ConversationId,
        messages: list[dict],
        assistant_text_parts: list[str],
    ) -> None:
        new_messages: list[dict] = []
        last_user = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        if last_user is not None:
            new_messages.append({"role": "user", "content": last_user.get("content", "")})
        assistant_text = "".join(assistant_text_parts).strip()
        if assistant_text:
            new_messages.append({"role": "assistant", "content": assistant_text})
        if not new_messages:
            return
        try:
            self.conversations.append_messages(conversation_id, new_messages)
        except ConversationNotFound:
            # 대화가 없으면 그냥 무시 — 채팅 자체는 성공해야 함
            pass
