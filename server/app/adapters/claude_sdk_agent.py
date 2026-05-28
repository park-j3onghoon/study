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


def _strip_prefix(name: str) -> str:
    return name[len(_MCP_TOOL_PREFIX):] if name.startswith(_MCP_TOOL_PREFIX) else name


class ClaudeSDKAgent(Agent):
    def __init__(
        self,
        tools: list[Tool],
        system_prompt: str | None = None,
        default_model: str | None = None,
        default_thinking_budget: int = 0,
    ):
        self.system_prompt = system_prompt
        self.default_model = default_model
        self.default_thinking_budget = default_thinking_budget

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
        chosen_budget = thinking_budget if thinking_budget is not None else self.default_thinking_budget

        options = ClaudeAgentOptions(
            # tools=[] disables Claude Code's built-in Read/Write/Bash/etc — we only
            # want our 5 MCP tools exposed (no filesystem access from the LLM).
            tools=[],
            mcp_servers={_MCP_SERVER_NAME: self.mcp_config},
            allowed_tools=self.allowed_tools,
            include_partial_messages=True,
            permission_mode="bypassPermissions",
            model=chosen_model,
            system_prompt=self.system_prompt,
        )
        if chosen_budget > 0:
            options.thinking = {"type": "enabled", "budget_tokens": chosen_budget}

        prompt_text = _format_history_as_prompt(messages)
        # tool_use_id → tool name. SDK doesn't repeat the name on result arrival,
        # so we remember it from ToolUseBlock and emit `tool_use_complete` when
        # the matching ToolResultBlock comes back inside a UserMessage.
        tool_names: dict[str, str] = {}
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
                        tool_names[block.id] = _strip_prefix(block.name)
                if msg.error:
                    yield {"type": "error", "message": f"Assistant error: {msg.error}"}
            elif isinstance(msg, UserMessage):
                if isinstance(msg.content, list):
                    for block in msg.content:
                        tu_id = getattr(block, "tool_use_id", None)
                        if tu_id is not None:
                            name = tool_names.pop(tu_id, "tool")
                            yield {"type": "tool_use_complete", "name": name}
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
