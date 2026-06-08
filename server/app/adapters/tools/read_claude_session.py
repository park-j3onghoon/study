"""read_claude_session tool. Returns one session's user/assistant text for distilling."""
from typing import Any

from ...domain.exceptions import InvalidSessionId
from ...domain.models import SessionId
from ...domain.ports import ClaudeSessionReader, Tool


class ReadClaudeSessionTool(Tool):
    name = "read_claude_session"
    description = (
        "Read one Claude Code session's conversation — user + assistant text only (thinking, "
        "tool calls and tool results are stripped out). Use after list_claude_sessions to pull "
        "the 1-3 sessions worth distilling. Output is truncated to max_chars (a default is applied "
        "when omitted). 'session_id' is the id from list_claude_sessions. "
        "Returns 'Error: ...' for a malformed or missing session_id."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "session_id from list_claude_sessions."},
            "max_chars": {"type": "integer", "description": "Truncate the transcript to this many chars."},
        },
        "required": ["session_id"],
    }

    def __init__(self, reader: ClaudeSessionReader, default_max_chars: int):
        self.reader = reader
        self.default_max_chars = default_max_chars

    async def execute(self, args: dict[str, Any]) -> str:
        try:
            session_id = SessionId(args["session_id"])
        except InvalidSessionId as exc:
            return f"Error: {exc}"
        max_chars = args.get("max_chars") or self.default_max_chars
        return self.reader.read_session(session_id, max_chars)
