"""Agent implementation backed by claude-agent-sdk (Claude Code OAuth via Claude Max).
SDK details are confined to this module — domain/application never see SDK types.

Tools are registered as an in-process MCP server, so existing Tool implementations
work unchanged. The SDK manages the tool-use loop internally; we just map stream
events into our domain event vocabulary.
"""
from typing import Any, AsyncIterator

from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, RateLimitEvent, ResultMessage,
    SdkMcpTool, StreamEvent, ToolUseBlock, UserMessage, create_sdk_mcp_server,
    query,
)

from ..domain.ports import Agent, Tool


_MCP_SERVER_NAME = "learning"
_MCP_TOOL_PREFIX = f"mcp__{_MCP_SERVER_NAME}__"
# write_lesson signals success with this prefix; see WriteLessonTool.execute.
_WRITE_LESSON = "write_lesson"
_WRITE_SUCCESS_PREFIX = "Created"


def _strip_prefix(name: str) -> str:
    return name[len(_MCP_TOOL_PREFIX):] if name.startswith(_MCP_TOOL_PREFIX) else name


class ClaudeSDKAgent(Agent):
    def __init__(
        self,
        tools: list[Tool],
        system_prompt: str | None = None,
        default_model: str | None = None,
        default_thinking_budget: int = 0,
        max_turns: int | None = None,
    ):
        self.system_prompt = system_prompt
        self.default_model = default_model
        self.default_thinking_budget = default_thinking_budget
        self.max_turns = max_turns

        sdk_tools = [_wrap_tool(t) for t in tools]
        self.mcp_config = create_sdk_mcp_server(name=_MCP_SERVER_NAME, tools=sdk_tools)
        self.allowed_tools = [f"mcp__{_MCP_SERVER_NAME}__{t.name}" for t in tools]

    async def stream(
        self,
        messages: list[dict],
        model: str | None = None,
        thinking_budget: int | None = None,
    ) -> AsyncIterator[dict]:
        chosen_model = model or self.default_model

        options = ClaudeAgentOptions(
            # tools=[] disables Claude Code's built-in Read/Write/Bash/etc — we only
            # want our own MCP tools exposed (no filesystem access from the LLM).
            tools=[],
            mcp_servers={_MCP_SERVER_NAME: self.mcp_config},
            allowed_tools=self.allowed_tools,
            # Isolation (CRITICAL): this agent must obey ONLY our system_prompt + MCP tools.
            # With the defaults (setting_sources=None, skills=None) the SDK loads the user's
            # global ~/.claude config — their CLAUDE.md and, fatally, auto-firing skills like
            # `study`, which hijacks "X가 뭐야" into a markdown chat answer and never calls
            # write_lesson. [] = SDK isolation mode.
            setting_sources=[],       # no user/project/local settings.json or CLAUDE.md
            skills=[],                # suppress every skill (kills the `study` skill hijack)
            strict_mcp_config=True,   # use only our MCP server; ignore user MCP config
            include_partial_messages=True,
            permission_mode="bypassPermissions",
            model=chosen_model,
            system_prompt=self.system_prompt,
            max_turns=self.max_turns,
            # Always reason at maximum effort (SDK 'max' tier). Supersedes the old
            # per-request thinking-budget knob; thinking_budget is now ignored.
            effort="max",
        )

        prompt_text = _format_history_as_prompt(messages)
        # tool_use_id → tool name. SDK doesn't repeat the name on result arrival,
        # so we remember it from ToolUseBlock and emit `tool_use_complete` when
        # the matching ToolResultBlock comes back inside a UserMessage.
        tool_names: dict[str, str] = {}
        # tool_use_id → concept_id requested with focus=true. SR-3: emit focus_lesson
        # only when the matching result is a success, never from the input alone.
        pending_focus: dict[str, str] = {}
        thinking_open = False

        async for msg in query(prompt=prompt_text, options=options):
            if isinstance(msg, StreamEvent):
                ev = msg.event
                etype = ev.get("type")
                if etype == "content_block_start":
                    block = ev.get("content_block") or {}
                    btype = block.get("type")
                    if btype == "thinking":
                        thinking_open = True
                        yield {"type": "thinking_start"}
                    elif btype == "tool_use":
                        name = _strip_prefix(block.get("name", ""))
                        block_id = block.get("id")
                        if block_id:
                            tool_names[block_id] = name
                        yield {"type": "tool_use_start", "name": name}
                elif etype == "content_block_delta":
                    delta = ev.get("delta") or {}
                    dtype = delta.get("type")
                    if dtype == "text_delta":
                        yield {"type": "text_delta", "text": delta.get("text", "")}
                    elif dtype == "thinking_delta":
                        yield {"type": "thinking_delta", "text": delta.get("thinking", "")}
                elif etype == "content_block_stop":
                    if thinking_open:
                        thinking_open = False
                        yield {"type": "thinking_stop"}
            elif isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        name = _strip_prefix(block.name)
                        tool_names[block.id] = name
                        if name == _WRITE_LESSON:
                            cid = _focus_concept_id(block.input)
                            if cid is not None:
                                pending_focus[block.id] = cid
                if msg.error:
                    yield {"type": "error", "message": f"Assistant error: {msg.error}"}
            elif isinstance(msg, UserMessage):
                if isinstance(msg.content, list):
                    for block in msg.content:
                        tu_id = getattr(block, "tool_use_id", None)
                        if tu_id is not None:
                            name = tool_names.pop(tu_id, "tool")
                            yield {"type": "tool_use_complete", "name": name}
                            cid = pending_focus.pop(tu_id, None)
                            if cid is not None and _result_succeeded(block):
                                yield {"type": "focus_lesson", "concept_id": cid}
            elif isinstance(msg, ResultMessage):
                if msg.is_error:
                    detail = ", ".join(msg.errors or []) or (msg.stop_reason or "unknown error")
                    yield {"type": "error", "message": f"Result error: {detail}"}
                else:
                    yield {
                        "type": "message_stop",
                        "stop_reason": msg.stop_reason,
                        "usage": msg.usage or {},
                    }
                return
            elif isinstance(msg, RateLimitEvent):
                # status: 'allowed' | 'allowed_warning' | 'rejected'. Only the last is fatal.
                status = getattr(msg.rate_limit_info, "status", None)
                if status == "rejected":
                    yield {"type": "error", "message": "Claude Max rate limit exceeded"}
                    return
                # otherwise informational — keep iterating until ResultMessage


def _wrap_tool(t: Tool) -> SdkMcpTool:
    async def handler(args: dict[str, Any]) -> dict[str, Any]:
        text = await t.execute(args)
        return {"content": [{"type": "text", "text": text}]}
    return SdkMcpTool(
        name=t.name,
        description=t.description,
        input_schema=t.input_schema,
        handler=handler,
    )


def _focus_concept_id(tool_input: Any) -> str | None:
    """concept_id of a write_lesson call iff it set focus=true — the lesson the user asked
    for, which the UI auto-opens. The system prompt requires focus=true on the target and
    omits it on parent/sibling rewrites, so those don't steal the viewport."""
    if not isinstance(tool_input, dict) or tool_input.get("focus") is not True:
        return None
    cid = tool_input.get("concept_id")
    return cid if isinstance(cid, str) and cid else None


def _result_succeeded(block: Any) -> bool:
    """A write_lesson tool result is a success when its text starts with 'Created'."""
    if getattr(block, "is_error", False):
        return False
    content = getattr(block, "content", None)
    text = content if isinstance(content, str) else _text_of(content)
    return text.startswith(_WRITE_SUCCESS_PREFIX)


def _text_of(content: Any) -> str:
    if not isinstance(content, list):
        return ""
    parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    return "".join(parts)


def _format_history_as_prompt(messages: list[dict]) -> str:
    """Each HTTP request gets a fresh SDK session — we don't reuse session_id across
    requests. To preserve context, prior turns are embedded as text. Loses native
    role-aware streaming on history but keeps the request layer stateless."""
    if not messages:
        return ""
    if len(messages) == 1 and messages[0].get("role") == "user":
        return messages[0].get("content", "")
    parts: list[str] = ["[Previous conversation — for context]\n"]
    for m in messages[:-1]:
        role = "User" if m.get("role") == "user" else "Assistant"
        parts.append(f"{role}: {m.get('content', '')}\n")
    parts.append("\n[New user message — respond to this]\n")
    parts.append(messages[-1].get("content", ""))
    return "".join(parts)
