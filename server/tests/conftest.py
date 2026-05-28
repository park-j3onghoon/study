"""Shared pytest fixtures."""
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

import pytest

from app.adapters.disk_conversation_repository import DiskConversationRepository
from app.adapters.disk_repository import DiskLessonRepository
from app.application.chat_service import ChatService
from app.application.conversation_service import ConversationService
from app.application.lesson_service import LessonService
from app.domain.models import (
    ConceptId, Lesson, Question, new_conversation_id,
)
from app.domain.ports import Agent


@pytest.fixture
def tmp_lessons_repo(tmp_path: Path) -> DiskLessonRepository:
    return DiskLessonRepository(tmp_path / "lessons")


@pytest.fixture
def tmp_conversations_repo(tmp_path: Path) -> DiskConversationRepository:
    return DiskConversationRepository(tmp_path / "conversations")


@pytest.fixture
def lesson_service(tmp_lessons_repo) -> LessonService:
    return LessonService(tmp_lessons_repo)


@pytest.fixture
def conversation_service(tmp_conversations_repo) -> ConversationService:
    return ConversationService(tmp_conversations_repo)


@pytest.fixture
def sample_lesson() -> Lesson:
    return Lesson(
        concept_id=ConceptId("sample-concept"),
        title="Sample",
        html="<!DOCTYPE html><html><body>hi</body></html>",
        questions=(
            Question(id="q1", type="multiple_choice", prompt="Pick one",
                     options=("a", "b"), correct="a"),
            Question(id="q2", type="short_answer", prompt="Explain X",
                     expected_keywords=("kw1",)),
        ),
        created=datetime(2026, 5, 28, tzinfo=timezone.utc),
        model="claude-opus-4-7",
        thinking_budget=2000,
    )


class StubAgent(Agent):
    """Agent that replays a fixed list of events. Used for ChatService tests."""

    def __init__(self, events: list[dict]):
        self.events = events
        self.received_messages: list[dict] | None = None

    async def stream(
        self,
        messages: list[dict],
        model: str | None = None,
        thinking_budget: int | None = None,
    ) -> AsyncIterator[dict]:
        self.received_messages = messages
        for ev in self.events:
            yield dict(ev)


@pytest.fixture
def make_stub_agent():
    return StubAgent


@pytest.fixture
def chat_service(make_stub_agent) -> ChatService:
    return ChatService(make_stub_agent([
        {"type": "text_delta", "text": "hello "},
        {"type": "text_delta", "text": "world"},
        {"type": "message_stop", "stop_reason": "end_turn"},
    ]))


@pytest.fixture
def fresh_conversation_id():
    return new_conversation_id
