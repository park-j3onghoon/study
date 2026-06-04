"""HTTP route smoke tests. Uses a hand-built FastAPI app with stub agent so we
don't need an Anthropic API key.
"""
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.adapters.disk_conversation_repository import DiskConversationRepository
from app.adapters.disk_repository import DiskLessonRepository
from app.application.chat_service import ChatService
from app.application.conversation_service import ConversationService
from app.application.lesson_service import LessonService
from app.application.model_service import ModelService
from app.domain.models import ConceptId, ModelInfo
from app.domain.ports import EventStream, ModelCatalog
from app.interface.routes import chat, conversations, events, lessons, models

from .conftest import StubAgent


class _NoopEventStream(EventStream):
    async def watch(self):
        if False:
            yield {}


class _StubCatalog(ModelCatalog):
    def __init__(self, models):
        self.models = models

    async def list_available(self):
        return list(self.models)


def _now_utc():
    from datetime import datetime, timezone
    return datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def client(tmp_path: Path):
    lesson_svc = LessonService(DiskLessonRepository(tmp_path / "lessons"))
    conv_svc = ConversationService(DiskConversationRepository(tmp_path / "conv"))
    chat_svc = ChatService(StubAgent([
        {"type": "text_delta", "text": "ok"},
        {"type": "message_stop", "stop_reason": "end_turn"},
    ]))
    model_svc = ModelService(_StubCatalog([
        ModelInfo(id="claude-opus-test", display_name="Opus Test",
                  family="opus", created_at=_now_utc()),
        ModelInfo(id="claude-haiku-test", display_name="Haiku Test",
                  family="haiku", created_at=_now_utc()),
    ]))
    app = FastAPI()
    app.include_router(chat.make_router(chat_svc, conv_svc), prefix="/api")
    app.include_router(lessons.make_router(lesson_svc), prefix="/api")
    app.include_router(conversations.make_router(conv_svc), prefix="/api")
    app.include_router(events.make_router(_NoopEventStream()), prefix="/api")
    app.include_router(models.make_router(model_svc), prefix="/api")
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


def test_lessons_list_propagates_parent_id(client, sample_lesson, tmp_path):
    repo = DiskLessonRepository(tmp_path / "lessons")
    repo.save(sample_lesson)  # root: parent_id None
    child = replace(sample_lesson, concept_id=ConceptId("child-concept"),
                    parent_id=sample_lesson.concept_id)
    repo.save(child)

    payload = client.get("/api/lessons").json()
    by_id = {item["concept_id"]: item for item in payload}
    assert by_id[sample_lesson.concept_id.value]["parent_id"] is None
    assert by_id["child-concept"]["parent_id"] == sample_lesson.concept_id.value


def test_lesson_detail_propagates_parent_id(client, sample_lesson, tmp_path):
    repo = DiskLessonRepository(tmp_path / "lessons")
    repo.save(sample_lesson)
    child = replace(sample_lesson, concept_id=ConceptId("child-concept"),
                    parent_id=sample_lesson.concept_id)
    repo.save(child)

    detail = client.get("/api/lessons/child-concept").json()
    assert detail["parent_id"] == sample_lesson.concept_id.value


def test_models_returns_latest_per_family(client):
    r = client.get("/api/models")
    assert r.status_code == 200
    payload = r.json()
    families = [m["family"] for m in payload]
    assert families == ["opus", "haiku"]  # opus first (best tier)
    assert payload[0]["id"] == "claude-opus-test"
