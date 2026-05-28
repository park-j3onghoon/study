"""HTTP route smoke tests. Uses a hand-built FastAPI app with stub agent so we
don't need an Anthropic API key.
"""
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.adapters.disk_conversation_repository import DiskConversationRepository
from app.adapters.disk_repository import DiskLessonRepository
from app.application.chat_service import ChatService
from app.application.conversation_service import ConversationService
from app.application.lesson_service import LessonService
from app.domain.ports import EventStream
from app.interface.routes import chat, conversations, events, lessons

from .conftest import StubAgent


class _NoopEventStream(EventStream):
    async def watch(self):
        if False:
            yield {}


@pytest.fixture
def client(tmp_path: Path):
    lesson_svc = LessonService(DiskLessonRepository(tmp_path / "lessons"))
    conv_svc = ConversationService(DiskConversationRepository(tmp_path / "conv"))
    chat_svc = ChatService(StubAgent([
        {"type": "text_delta", "text": "ok"},
        {"type": "message_stop", "stop_reason": "end_turn"},
    ]))
    app = FastAPI()
    app.include_router(chat.make_router(chat_svc, conv_svc), prefix="/api")
    app.include_router(lessons.make_router(lesson_svc), prefix="/api")
    app.include_router(conversations.make_router(conv_svc), prefix="/api")
    app.include_router(events.make_router(_NoopEventStream()), prefix="/api")
    return TestClient(app)


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_lessons_empty_list(client):
    r = client.get("/api/lessons")
    assert r.status_code == 200
    assert r.json() == []


def test_lessons_invalid_id_400(client):
    r = client.post("/api/lessons/BAD_ID/answers", json={"answers": {}})
    assert r.status_code == 400


def test_conversations_create_then_get(client):
    r = client.post("/api/conversations", json={"title": "t"})
    assert r.status_code == 200
    cid = r.json()["id"]
    detail = client.get(f"/api/conversations/{cid}")
    assert detail.status_code == 200
    assert detail.json()["messages"] == []


def test_conversations_invalid_id_400(client):
    r = client.get("/api/conversations/not-hex")
    assert r.status_code == 400


def test_conversations_unknown_id_404(client):
    # valid hex32 that doesn't exist
    r = client.get("/api/conversations/" + "0" * 32)
    assert r.status_code == 404


def test_chat_invalid_conversation_id_400(client):
    r = client.post("/api/chat", json={
        "messages": [{"role": "user", "content": "hi"}],
        "conversation_id": "garbage",
    })
    assert r.status_code == 400


def test_chat_streams_and_persists_turn(client):
    create = client.post("/api/conversations", json={"title": "t"}).json()
    cid = create["id"]
    with client.stream("POST", "/api/chat", json={
        "messages": [{"role": "user", "content": "hi"}],
        "conversation_id": cid,
    }) as resp:
        assert resp.status_code == 200
        body = b"".join(resp.iter_bytes()).decode()
    assert "event: text_delta" in body
    assert "event: message_stop" in body
    detail = client.get(f"/api/conversations/{cid}").json()
    roles = [m["role"] for m in detail["messages"]]
    assert roles == ["user", "assistant"]
    assert detail["messages"][1]["content"] == "ok"


def test_lesson_submit_answers_flow(client, sample_lesson, tmp_path):
    # write a lesson directly via repo (simulates Claude's write_lesson tool)
    DiskLessonRepository(tmp_path / "lessons").save(sample_lesson)
    cid = sample_lesson.concept_id.value
    # submit answers
    r = client.post(f"/api/lessons/{cid}/answers", json={"answers": {"q1": "a", "q2": "kw1"}})
    assert r.status_code == 200
    # lesson detail returns html and questions
    detail = client.get(f"/api/lessons/{cid}").json()
    assert detail["title"] == sample_lesson.title
    assert len(detail["questions"]) == 2
