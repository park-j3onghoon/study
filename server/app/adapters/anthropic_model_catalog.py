"""ModelCatalog backed by Anthropic's GET /v1/models.
SDK isolation: domain/application never see Anthropic types.
"""
from datetime import datetime
from typing import Any

from anthropic import AsyncAnthropic

from ..domain.models import ModelInfo
from ..domain.ports import ModelCatalog


_FAMILY_KEYWORDS = ("opus", "sonnet", "haiku")


class AnthropicModelCatalog(ModelCatalog):
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self._cache: list[ModelInfo] | None = None

    async def list_available(self) -> list[ModelInfo]:
        if self._cache is not None:
            return self._cache
        page = await self.client.models.list(limit=100)
        models = [_convert(m) for m in page.data if _is_claude(m)]
        self._cache = models
        return models


def _is_claude(raw: Any) -> bool:
    return getattr(raw, "id", "").startswith("claude-")


def _convert(raw: Any) -> ModelInfo:
    return ModelInfo(
        id=raw.id,
        display_name=getattr(raw, "display_name", raw.id),
        family=_classify_family(raw.id),
        created_at=_parse_created(getattr(raw, "created_at", None)),
    )


def _classify_family(model_id: str) -> str:
    for keyword in _FAMILY_KEYWORDS:
        if keyword in model_id:
            return keyword
    return "other"


def _parse_created(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return datetime.min
