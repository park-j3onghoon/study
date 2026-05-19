"""시범 도구. P2에서 실제 도구로 교체될 예정."""
from typing import Any

from . import register_tool
from .base import Tool


@register_tool
class Echo(Tool):
    name = "echo"
    description = (
        "Echo the given text back verbatim, prefixed with 'echo: '. "
        "Use this only when the user explicitly asks for an echo test."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to echo back.",
            },
        },
        "required": ["text"],
    }

    async def execute(self, input: dict[str, Any]) -> str:
        return f"echo: {input['text']}"
