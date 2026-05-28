"""Hardcoded ModelCatalog. We use this with the Claude SDK / Max subscription path
because OAuth doesn't expose a model-listing endpoint. Update this list when
Anthropic releases new models."""
from datetime import datetime, timezone

from ..domain.models import ModelInfo
from ..domain.ports import ModelCatalog


# Order doesn't matter — ModelService sorts by family + created_at.
_KNOWN_MODELS: tuple[ModelInfo, ...] = (
    ModelInfo(
        id="claude-opus-4-7",
        display_name="Claude Opus 4.7",
        family="opus",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    ),
    ModelInfo(
        id="claude-sonnet-4-6",
        display_name="Claude Sonnet 4.6",
        family="sonnet",
        created_at=datetime(2025, 12, 1, tzinfo=timezone.utc),
    ),
    ModelInfo(
        id="claude-haiku-4-5-20251001",
        display_name="Claude Haiku 4.5",
        family="haiku",
        created_at=datetime(2025, 10, 1, tzinfo=timezone.utc),
    ),
)


class StaticModelCatalog(ModelCatalog):
    async def list_available(self) -> list[ModelInfo]:
        return list(_KNOWN_MODELS)
