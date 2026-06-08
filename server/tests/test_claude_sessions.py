"""Tests for the Claude Code session reader (the distill source)."""
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from app.adapters.claude_sessions import (
    DiskClaudeSessionReader, _extract_turn, _is_on_date, _normalize_content,
)
from app.adapters.tools.list_claude_sessions import ListClaudeSessionsTool, _resolve_on_date
from app.adapters.tools.read_claude_session import ReadClaudeSessionTool
from app.domain.exceptions import InvalidSessionId
from app.domain.models import SessionId
from app.domain.ports import ClaudeSessionReader

KST = ZoneInfo("Asia/Seoul")
UID = "11111111-1111-4111-8111-111111111111"
UID2 = "22222222-2222-4222-8222-222222222222"


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_session(projects: Path, project: str, sid: str, lines: list[dict],
                   mtime: datetime | None = None) -> Path:
    d = projects / project
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{sid}.jsonl"
    p.write_text("\n".join(json.dumps(o) for o in lines) + "\n", encoding="utf-8")
    if mtime is not None:
        ts = mtime.timestamp()
        os.utime(p, (ts, ts))
    return p


def _user(ts: datetime, text: str, cwd: str = "/Users/x/proj") -> dict:
    return {"type": "user", "timestamp": _iso(ts), "cwd": cwd,
            "message": {"role": "user", "content": text}}


def _assistant(ts: datetime, blocks: list, cwd: str = "/Users/x/proj") -> dict:
    return {"type": "assistant", "timestamp": _iso(ts), "cwd": cwd,
            "message": {"role": "assistant", "content": blocks}}


@pytest.fixture
def reader(tmp_path: Path) -> DiskClaudeSessionReader:
    return DiskClaudeSessionReader(base=tmp_path / "projects", tz=KST)


# ── pure functions ────────────────────────────────────────────────────────

class TestIsOnDate:
    target = date(2026, 6, 8)

    def test_just_before_kst_midnight_is_previous_day(self):
        # KST 2026-06-07 23:59 == UTC 2026-06-07 14:59
        ts = datetime(2026, 6, 7, 14, 59, tzinfo=timezone.utc)
        assert _is_on_date(ts, self.target, KST) is False

    def test_just_after_kst_midnight_is_target(self):
        # KST 2026-06-08 00:01 == UTC 2026-06-07 15:01
        ts = datetime(2026, 6, 7, 15, 1, tzinfo=timezone.utc)
        assert _is_on_date(ts, self.target, KST) is True

    def test_kst_noon_is_target(self):
        ts = datetime(2026, 6, 8, 3, 0, tzinfo=timezone.utc)  # KST 12:00
        assert _is_on_date(ts, self.target, KST) is True


class TestNormalizeContent:
    def test_string_passthrough(self):
        assert _normalize_content("hello") == "hello"

    def test_keeps_only_text_blocks(self):
        content = [
            {"type": "thinking", "thinking": "secret reasoning"},
            {"type": "text", "text": "visible one"},
            {"type": "tool_use", "name": "x", "input": {}},
            {"type": "tool_result", "content": "noise"},
            {"type": "text", "text": " and two"},
        ]
        assert _normalize_content(content) == "visible one and two"

    def test_unknown_shape_is_empty(self):
        assert _normalize_content(None) == ""


class TestExtractTurn:
    def test_assistant_strips_non_text_blocks(self):
        ts = datetime(2026, 6, 8, 3, tzinfo=timezone.utc)
        obj = _assistant(ts, [
            {"type": "thinking", "thinking": "..."},
            {"type": "text", "text": "answer"},
        ])
        assert _extract_turn(obj) == ("assistant", "answer")

    def test_tool_only_assistant_is_dropped(self):
        ts = datetime(2026, 6, 8, 3, tzinfo=timezone.utc)
        obj = _assistant(ts, [{"type": "tool_use", "name": "x", "input": {}}])
        assert _extract_turn(obj) is None

    def test_non_chat_line_is_none(self):
        assert _extract_turn({"type": "ai-title", "title": "t"}) is None


# ── list_sessions_on ──────────────────────────────────────────────────────

class TestListSessionsOn:
    def test_lists_only_target_date_sessions(self, reader, tmp_path):
        projects = tmp_path / "projects"
        noon = datetime(2026, 6, 8, 3, tzinfo=timezone.utc)  # KST 12:00 on 6/8
        _write_session(projects, "proj-a", UID, [
            {"type": "ai-title", "aiTitle": "GraphQL 페이지네이션"},
            _user(noon, "cursor 페이지네이션 어떻게 설계해?"),
            _assistant(noon, [{"type": "text", "text": "커서는..."}]),
        ], mtime=noon)
        sessions = reader.list_sessions_on(date(2026, 6, 8))
        assert len(sessions) == 1
        s = sessions[0]
        assert s.session_id.value == UID
        assert s.title == "GraphQL 페이지네이션"
        assert s.user_turns == 1 and s.assistant_turns == 1
        assert "cursor" in s.preview
        assert s.project == "proj"  # basename of cwd

    def test_empty_when_no_session_on_date(self, reader, tmp_path):
        projects = tmp_path / "projects"
        two_days_ago = datetime(2026, 6, 6, 3, tzinfo=timezone.utc)
        _write_session(projects, "proj-a", UID, [
            _user(two_days_ago, "예전 대화"),
        ], mtime=two_days_ago)
        assert reader.list_sessions_on(date(2026, 6, 8)) == []

    def test_merges_multiple_projects(self, reader, tmp_path):
        projects = tmp_path / "projects"
        noon = datetime(2026, 6, 8, 3, tzinfo=timezone.utc)
        _write_session(projects, "proj-a", UID, [_user(noon, "a")], mtime=noon)
        _write_session(projects, "proj-b", UID2, [_user(noon, "b")], mtime=noon)
        sessions = reader.list_sessions_on(date(2026, 6, 8))
        assert {s.session_id.value for s in sessions} == {UID, UID2}

    def test_missing_base_returns_empty(self, tmp_path):
        r = DiskClaudeSessionReader(base=tmp_path / "nope", tz=KST)
        assert r.list_sessions_on(date(2026, 6, 8)) == []

    def test_ignores_lines_without_timestamp(self, reader, tmp_path):
        projects = tmp_path / "projects"
        noon = datetime(2026, 6, 8, 3, tzinfo=timezone.utc)
        _write_session(projects, "proj-a", UID, [
            {"type": "user", "message": {"role": "user", "content": "no ts"}},
            _user(noon, "with ts"),
        ], mtime=noon)
        sessions = reader.list_sessions_on(date(2026, 6, 8))
        assert sessions[0].user_turns == 1


# ── read_session ──────────────────────────────────────────────────────────

class TestReadSession:
    def test_returns_user_and_assistant_text_only(self, reader, tmp_path):
        projects = tmp_path / "projects"
        noon = datetime(2026, 6, 8, 3, tzinfo=timezone.utc)
        _write_session(projects, "proj-a", UID, [
            _user(noon, "질문이야"),
            _assistant(noon, [
                {"type": "thinking", "thinking": "비밀 추론"},
                {"type": "text", "text": "답이야"},
                {"type": "tool_use", "name": "write_lesson", "input": {"x": 1}},
            ]),
        ])
        out = reader.read_session(SessionId(UID), max_chars=10000)
        assert "질문이야" in out and "답이야" in out
        assert "비밀 추론" not in out
        assert "write_lesson" not in out

    def test_truncates_to_max_chars(self, reader, tmp_path):
        projects = tmp_path / "projects"
        noon = datetime(2026, 6, 8, 3, tzinfo=timezone.utc)
        _write_session(projects, "proj-a", UID, [
            _user(noon, "x" * 500),
            _user(noon, "y" * 500),
        ])
        out = reader.read_session(SessionId(UID), max_chars=50)
        assert "truncated" in out
        assert "y" not in out  # block-granular truncation excluded the 2nd message

    def test_skips_broken_json_lines(self, reader, tmp_path):
        projects = tmp_path / "projects"
        noon = datetime(2026, 6, 8, 3, tzinfo=timezone.utc)
        p = _write_session(projects, "proj-a", UID, [_user(noon, "good")])
        with p.open("a", encoding="utf-8") as f:
            f.write("{not valid json\n")
        out = reader.read_session(SessionId(UID), max_chars=10000)
        assert "good" in out

    def test_missing_session_returns_error(self, reader):
        out = reader.read_session(SessionId(UID), max_chars=10000)
        assert out.startswith("Error:")


# ── SessionId guard (path traversal) ──────────────────────────────────────

class TestSessionIdGuard:
    @pytest.mark.parametrize("bad", [
        "../../etc/passwd",
        "/etc/passwd",
        "..",
        "foo/../bar",
        "11111111-1111-4111-8111-111111111111/../x",
        "not-a-uuid",
        "",
    ])
    def test_rejects_non_uuid(self, bad):
        with pytest.raises(InvalidSessionId):
            SessionId(bad)


class TestReadClaudeSessionTool:
    async def test_malformed_session_id_returns_error_not_disk_read(self, reader):
        tool = ReadClaudeSessionTool(reader, default_max_chars=100)
        out = await tool.execute({"session_id": "../../.claude/.credentials"})
        assert out.startswith("Error:")


# ── day selection (server-side, agent needs no calendar knowledge) ─────────

class TestResolveOnDate:
    today = date(2026, 6, 8)

    def test_default_is_today(self):
        assert _resolve_on_date(self.today, None, None) == self.today

    def test_days_ago_one_is_yesterday(self):
        assert _resolve_on_date(self.today, None, 1) == date(2026, 6, 7)

    def test_days_ago_two(self):
        assert _resolve_on_date(self.today, None, 2) == date(2026, 6, 6)

    def test_absolute_date_overrides_days_ago(self):
        assert _resolve_on_date(self.today, "2026-06-01", 5) == date(2026, 6, 1)

    def test_string_days_ago_is_coerced(self):
        assert _resolve_on_date(self.today, None, "1") == date(2026, 6, 7)

    def test_negative_days_ago_raises(self):
        with pytest.raises(ValueError):
            _resolve_on_date(self.today, None, -1)

    def test_bad_date_raises(self):
        with pytest.raises(ValueError):
            _resolve_on_date(self.today, "nope", None)


class TestListClaudeSessionsTool:
    async def test_days_ago_resolves_relative_to_today(self):
        captured = {}

        class _FakeReader(ClaudeSessionReader):
            def list_sessions_on(self, on_date):
                captured["on_date"] = on_date
                return []

            def read_session(self, session_id, max_chars):
                return ""

        tool = ListClaudeSessionsTool(_FakeReader(), KST)
        await tool.execute({"days_ago": 1})
        assert captured["on_date"] == datetime.now(KST).date() - timedelta(days=1)
