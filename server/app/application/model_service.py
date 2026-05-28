"""ModelService — query-only. Ranks available models so the UI can pick the
"latest best" without knowing provider naming."""
from ..domain.models import ModelInfo
from ..domain.ports import ModelCatalog


# Higher index = better tier. "other" 는 가장 마지막에 놓는다.
_FAMILY_RANK = {"opus": 3, "sonnet": 2, "haiku": 1, "other": 0}


class ModelService:
    def __init__(self, catalog: ModelCatalog):
        self.catalog = catalog

    async def list_available(self) -> list[ModelInfo]:
        """Sorted: best family first, newest first within family."""
        models = await self.catalog.list_available()
        return sorted(
            models,
            key=lambda m: (_FAMILY_RANK.get(m.family, 0), m.created_at),
            reverse=True,
        )

    async def latest_per_family(self) -> list[ModelInfo]:
        """One model per family (the newest). Best family first."""
        seen: set[str] = set()
        picked: list[ModelInfo] = []
        for m in await self.list_available():
            if m.family in seen:
                continue
            seen.add(m.family)
            picked.append(m)
        return picked
