"""Claude API + tool_use loop, streaming. yields domain-level events as plain dicts.

이벤트 형식 (모두 dict, 키 'type'):
- {"type": "thinking_start"}
- {"type": "thinking_delta", "text": "..."}
- {"type": "thinking_stop"}
- {"type": "text_delta", "text": "..."}
- {"type": "tool_use_start", "name": "..."}
- {"type": "tool_use_complete", "name": "...", "result": "..."}
- {"type": "message_stop", "stop_reason": "...", "usage": {...}}

라우터(routes/chat.py)가 이 dict들을 SSE event로 직렬화한다.
"""
from typing import Any, AsyncIterator

from anthropic import AsyncAnthropic

from .config import settings
from .tools import find_tool, get_tool_schemas


class Agent:
    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def stream_run(
        self,
        messages: list[dict],
        model: str | None = None,
        thinking_budget: int | None = None,
    ) -> AsyncIterator[dict]:
        chosen_model = model or settings.default_model
        chosen_budget = thinking_budget if thinking_budget is not None else settings.default_thinking_budget
        history: list[dict] = list(messages)
        for _ in range(settings.max_tool_iterations):
            async with self._open_stream(history, chosen_model, chosen_budget) as stream:
                async for event in self._consume_stream(stream):
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
                tool = find_tool(tu.name)
                text = await tool.execute(tu.input) if tool else f"error: tool {tu.name!r} not found"
                yield {"type": "tool_use_complete", "name": tu.name, "result": text}
                results.append({"type": "tool_result", "tool_use_id": tu.id, "content": text})
            history.append({"role": "user", "content": results})

        raise RuntimeError(f"Agent exceeded max_iterations={settings.max_tool_iterations}")

    def _open_stream(self, history: list[dict], model: str, thinking_budget: int):
        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": self._max_tokens_for(thinking_budget),
            "messages": history,
        }
        schemas = get_tool_schemas()
        if schemas:
            kwargs["tools"] = schemas
        if thinking_budget > 0:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
        return self.client.messages.stream(**kwargs)

    async def _consume_stream(self, stream) -> AsyncIterator[dict]:
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
                # input_json_delta(도구 input streaming)는 무시 — tool_use_complete에서 한 번에 전달
            elif etype == "content_block_stop":
                if current_block_type == "thinking":
                    yield {"type": "thinking_stop"}
                current_block_type = None

    @staticmethod
    def _max_tokens_for(thinking_budget: int) -> int:
        # max_tokens must be larger than thinking_budget (Anthropic API constraint).
        return max(settings.max_response_tokens, thinking_budget + 4000)


agent = Agent()
