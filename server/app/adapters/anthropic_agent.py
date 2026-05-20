"""Concrete Agent backed by the Anthropic Messages API (streaming).
SDK details are confined to this module — domain/application layers never see Anthropic types.
"""
from typing import Any, AsyncIterator

from anthropic import AsyncAnthropic

from ..domain.ports import Agent, Tool


class AnthropicAgent(Agent):
    def __init__(
        self,
        api_key: str,
        default_model: str,
        default_thinking_budget: int,
        tools: list[Tool],
        max_iterations: int = 10,
        max_response_tokens: int = 8000,
    ):
        self.client = AsyncAnthropic(api_key=api_key)
        self.default_model = default_model
        self.default_thinking_budget = default_thinking_budget
        self.tools = tools
        self.max_iterations = max_iterations
        self.max_response_tokens = max_response_tokens
        self._tool_map = {t.name: t for t in tools}

    async def stream(
        self,
        messages: list[dict],
        model: str | None = None,
        thinking_budget: int | None = None,
    ) -> AsyncIterator[dict]:
        chosen_model = model or self.default_model
        chosen_budget = thinking_budget if thinking_budget is not None else self.default_thinking_budget
        history = list(messages)
        for _ in range(self.max_iterations):
            async with self._open(history, chosen_model, chosen_budget) as stream:
                async for event in self._consume(stream):
                    yield event
                final = await stream.get_final_message()

            tool_uses = [b for b in final.content if getattr(b, "type", None) == "tool_use"]
            if not tool_uses:
                yield {
                    "type": "message_stop",
                    "stop_reason": final.stop_reason,
                    "usage": final.usage.model_dump(),
                }
                return

            history.append({"role": "assistant", "content": [b.model_dump() for b in final.content]})
            results: list[dict] = []
            for tu in tool_uses:
                t = self._tool_map.get(tu.name)
                text = await t.execute(tu.input) if t else f"error: tool {tu.name!r} not found"
                yield {"type": "tool_use_complete", "name": tu.name, "result": text}
                results.append({"type": "tool_result", "tool_use_id": tu.id, "content": text})
            history.append({"role": "user", "content": results})

        raise RuntimeError(f"Agent exceeded max_iterations={self.max_iterations}")

    def _open(self, history: list[dict], model: str, budget: int):
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max(self.max_response_tokens, budget + 4000),
            "messages": history,
        }
        schemas = [
            {"name": t.name, "description": t.description, "input_schema": t.input_schema}
            for t in self.tools
        ]
        if schemas:
            kwargs["tools"] = schemas
        if budget > 0:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}
        return self.client.messages.stream(**kwargs)

    async def _consume(self, stream) -> AsyncIterator[dict]:
        current_block_type: str | None = None
        async for event in stream:
            etype = getattr(event, "type", None)
            if etype == "content_block_start":
                block = getattr(event, "content_block", None)
                current_block_type = getattr(block, "type", None)
                if current_block_type == "thinking":
                    yield {"type": "thinking_start"}
                elif current_block_type == "tool_use":
                    yield {"type": "tool_use_start", "name": getattr(block, "name", "")}
            elif etype == "content_block_delta":
                delta = getattr(event, "delta", None)
                delta_type = getattr(delta, "type", None)
                if delta_type == "thinking_delta":
                    yield {"type": "thinking_delta", "text": getattr(delta, "thinking", "")}
                elif delta_type == "text_delta":
                    yield {"type": "text_delta", "text": getattr(delta, "text", "")}
            elif etype == "content_block_stop":
                if current_block_type == "thinking":
                    yield {"type": "thinking_stop"}
                current_block_type = None
