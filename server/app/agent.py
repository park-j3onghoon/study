"""Claude API + tool_use loop. P1에서는 동기 응답만. P4에서 SSE 스트리밍으로 확장 예정."""
from typing import Any

from anthropic import AsyncAnthropic

from .config import settings
from .tools import find_tool, get_tool_schemas


class Agent:
    def __init__(self) -> None:
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def run(
        self,
        messages: list[dict],
        model: str | None = None,
        thinking_budget: int | None = None,
    ) -> dict:
        chosen_model = model or settings.default_model
        chosen_budget = thinking_budget if thinking_budget is not None else settings.default_thinking_budget
        history: list[dict] = list(messages)
        for _ in range(settings.max_tool_iterations):
            response = await self._call_model(history, chosen_model, chosen_budget)
            tool_uses = [b for b in response.content if getattr(b, "type", None) == "tool_use"]
            if not tool_uses:
                return self._format_final(response)
            history.append({"role": "assistant", "content": [b.model_dump() for b in response.content]})
            history.append({"role": "user", "content": await self._run_tools(tool_uses)})
        raise RuntimeError(f"Agent exceeded max_iterations={settings.max_tool_iterations}")

    async def _call_model(self, history: list[dict], model: str, thinking_budget: int):
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
        return await self.client.messages.create(**kwargs)

    async def _run_tools(self, tool_uses: list[Any]) -> list[dict]:
        results: list[dict] = []
        for tu in tool_uses:
            tool = find_tool(tu.name)
            text = await tool.execute(tu.input) if tool else f"error: tool {tu.name!r} not found"
            results.append({"type": "tool_result", "tool_use_id": tu.id, "content": text})
        return results

    @staticmethod
    def _max_tokens_for(thinking_budget: int) -> int:
        # max_tokens must be larger than thinking budget (Anthropic API constraint).
        return max(settings.max_response_tokens, thinking_budget + 4000)

    @staticmethod
    def _format_final(response: Any) -> dict:
        return {
            "stop_reason": response.stop_reason,
            "content": [b.model_dump() for b in response.content],
            "usage": response.usage.model_dump(),
        }


agent = Agent()
