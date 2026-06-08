"""list_claude_sessions tool. Lists a day's Claude Code sessions for the distill flow."""
from datetime import date, datetime, timedelta, tzinfo
from typing import Any

from ...domain.models import ClaudeSessionSummary
from ...domain.ports import ClaudeSessionReader, Tool


class ListClaudeSessionsTool(Tool):
    name = "list_claude_sessions"
    description = (
        "List a day's Claude Code coding sessions (across all projects) so you can pick which "
        "to distill into a lesson. One line per session: session_id, project, title, start time, "
        "user/assistant turn counts, and a preview of the first user prompt. Use the preview to "
        "choose only the 1-3 sessions worth reading with read_claude_session — do NOT read every "
        "session. Day selection (the server resolves the actual date — you do not need to know "
        "today's date): 'days_ago' for relative requests (0=today default, 1=yesterday, 2=two days "
        "ago), or 'date' (YYYY-MM-DD) for a specific calendar day. Returns '(no sessions ...)' when none."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "days_ago": {
                "type": "integer",
                "description": "0=today (default), 1=yesterday, 2=two days ago. Use for relative requests like '어제'.",
            },
            "date": {"type": "string", "description": "Specific day as YYYY-MM-DD (overrides days_ago)."},
        },
    }

    def __init__(self, reader: ClaudeSessionReader, tz: tzinfo):
        self.reader = reader
        self.tz = tz

    async def execute(self, args: dict[str, Any]) -> str:
        try:
            on_date = _resolve_on_date(
                datetime.now(self.tz).date(), args.get("date"), args.get("days_ago")
            )
        except ValueError as exc:
            return f"Error: {exc}"
        sessions = self.reader.list_sessions_on(on_date)
        if not sessions:
            return f"(no sessions on {on_date.isoformat()})"
        return "\n".join(_render(s) for s in sessions)


def _resolve_on_date(today: date, date_str: str | None, days_ago: Any) -> date:
    """Resolve which day to list. Absolute `date` wins; else `days_ago` back from today
    (computed here, server-side, so the agent never needs to know the calendar); else today."""
    if date_str:
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"invalid date {date_str!r} (expected YYYY-MM-DD)")
    if days_ago is not None:
        try:
            n = int(days_ago)
        except (TypeError, ValueError):
            raise ValueError(f"days_ago must be an integer, got {days_ago!r}")
        if n < 0:
            raise ValueError("days_ago must be >= 0")
        return today - timedelta(days=n)
    return today


def _render(s: ClaudeSessionSummary) -> str:
    return (
        f"- {s.session_id.value} | {s.project} | {s.title} "
        f"| {s.started_at.isoformat()} | turns={s.user_turns}u/{s.assistant_turns}a "
        f"| preview: {s.preview}"
    )
