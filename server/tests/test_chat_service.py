"""ChatService — pure-read stream. Persistence is a separate concern (route's job)."""
import pytest

from app.application.chat_service import ChatService


pytestmark = pytest.mark.asyncio


async def test_stream_forwards_agent_events(chat_service):
    events = [e async for e in chat_service.stream(messages=[{"role": "user", "content": "hi"}])]
    types = [e["type"] for e in events]
    assert types == ["text_delta", "text_delta", "message_stop"]


async def test_stream_passes_messages_to_agent(make_stub_agent):
    agent = make_stub_agent([])
    svc = ChatService(agent)
    msgs = [{"role": "user", "content": "hello"}]
    _ = [e async for e in svc.stream(messages=msgs, model="m", thinking_budget=100)]
    assert agent.received_messages == msgs


async def test_stream_does_not_persist(make_stub_agent, tmp_conversations_repo):
    """Pure-read invariant: stream itself never touches the repo."""
    agent = make_stub_agent([{"type": "text_delta", "text": "hi"}])
    svc = ChatService(agent)
    _ = [e async for e in svc.stream(messages=[{"role": "user", "content": "?"}])]
    assert tmp_conversations_repo.list_summaries() == []
