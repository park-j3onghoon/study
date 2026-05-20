from typing import Any

from ...domain.ports import Tool


class EchoTool(Tool):
    name = "echo"
    description = (
        "Echo back the given text prefixed with 'echo: '. "
        "Use only when the user explicitly asks for an echo test."
    )
    input_schema = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    }

    async def execute(self, input: dict[str, Any]) -> str:
        return f"echo: {input['text']}"
