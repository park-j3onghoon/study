"""Reads Claude Code session transcripts (~/.claude/projects/<proj>/<uuid>.jsonl).

Read-only access to an external on-disk source, confined to this adapter so the LLM
tools (and the rest of the app) never touch the filesystem directly. The base dir is
injected so tests point at a fake tree instead of the real ~/.claude.
"""
import json
import logging
from datetime import date, datetime, time, tzinfo
from pathlib import Path

from ..domain.models import ClaudeSessionSummary, SessionId
from ..domain.ports import ClaudeSessionReader

log = logging.getLogger(__name__)

_PREVIEW_CHARS = 160
_CHAT_ROLES = ("user", "assistant")


class DiskClaudeSessionReader(ClaudeSessionReader):
    def __init__(self, base: Path, tz: tzinfo):
        self.base = base
        self.tz = tz

    def list_sessions_on(self, on_date: date) -> list[ClaudeSessionSummary]:
        if not self.base.is_dir():
            return []
        # A file last written before on_date can't hold on_date events — skip the open.
        floor = datetime.combine(on_date, time.min, tzinfo=self.tz).timestamp()
        summaries: list[ClaudeSessionSummary] = []
        for path in self.base.glob("*/*.jsonl"):
            try:
                if path.stat().st_mtime < floor:
                    continue
            except OSError:
                continue
            summary = self._summarize(path, on_date)
            if summary is not None:
                summaries.append(summary)
        summaries.sort(key=lambda s: s.started_at, reverse=True)
        return summaries

    def read_session(self, session_id: SessionId, max_chars: int) -> str:
        path = self._resolve(session_id)
        if path is None:
            return f"Error: session {session_id.value!r} not found."
        parts: list[str] = []
        used = 0
        for obj in _iter_lines(path):
            turn = _extract_turn(obj)
            if turn is None:
                continue
            role, text = turn
            block = f"{role.capitalize()}: {text}"
            parts.append(block)
            used += len(block)
            if used >= max_chars:
                parts.append("…(truncated)")
                break
        return "\n\n".join(parts) if parts else "(empty session)"

    def _resolve(self, session_id: SessionId) -> Path | None:
        # session_id is regex-validated (UUID) so the glob pattern cannot traverse.
        matches = sorted(self.base.glob(f"*/{session_id.value}.jsonl"))
        if not matches:
            return None
        path = matches[0].resolve()
        # Defense in depth: never read outside base even if a symlink points away.
        if not path.is_relative_to(self.base.resolve()):
            log.warning("session path escaped base, refusing: %s", path)
            return None
        return path

    def _summarize(self, path: Path, on_date: date) -> ClaudeSessionSummary | None:
        title = ""
        project = ""
        preview = ""
        started_at: datetime | None = None
        user_turns = 0
        assistant_turns = 0
        for obj in _iter_lines(path):
            if not title and obj.get("type") == "ai-title":
                # Claude Code stores the auto-generated session title under "aiTitle".
                title = str(obj.get("aiTitle") or "")
            if not project:
                project = _project_of(obj)
            turn = _extract_turn(obj)
            ts = _parse_ts(obj.get("timestamp"))
            if turn is None or ts is None or not _is_on_date(ts, on_date, self.tz):
                continue
            role, text = turn
            if started_at is None or ts < started_at:
                started_at = ts
            if role == "user":
                user_turns += 1
                if not preview:
                    preview = text[:_PREVIEW_CHARS]
            else:
                assistant_turns += 1
        if started_at is None:  # no event on on_date
            return None
        return ClaudeSessionSummary(
            session_id=SessionId(path.stem),
            title=title or "(untitled)",
            project=project or "(unknown)",
            started_at=started_at,
            user_turns=user_turns,
            assistant_turns=assistant_turns,
            preview=preview,
        )


def _iter_lines(path: Path):
    """Yield parsed JSON objects from a .jsonl one line at a time — a single session
    file can be tens of MB, so we never load it whole. Broken lines are skipped."""
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    yield obj
    except OSError as exc:
        log.warning("could not read session %s: %s", path, exc)


def _extract_turn(obj: dict) -> tuple[str, str] | None:
    """(role, text) for a user/assistant line with non-empty text, else None."""
    if obj.get("type") not in _CHAT_ROLES:
        return None
    message = obj.get("message")
    if not isinstance(message, dict) or message.get("role") not in _CHAT_ROLES:
        return None
    text = _normalize_content(message.get("content")).strip()
    if not text:
        return None
    return message["role"], text


def _normalize_content(content) -> str:
    """Message content is a str (simple) or a list of typed blocks. Keep only text —
    the learning material — and drop thinking / tool_use / tool_result / image blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def _is_on_date(ts: datetime, on_date: date, tz: tzinfo) -> bool:
    return ts.astimezone(tz).date() == on_date


def _parse_ts(value) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    # Session timestamps are UTC ISO-8601 with a trailing Z (e.g. 2026-06-08T04:44:41.324Z);
    # 3.10's fromisoformat doesn't accept "Z".
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _project_of(obj: dict) -> str:
    cwd = obj.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        return ""
    name = Path(cwd).name
    branch = obj.get("gitBranch")
    return f"{name}@{branch}" if isinstance(branch, str) and branch else name
