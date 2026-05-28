"""ModelService — ranking + latest-per-family."""
from datetime import datetime, timezone

import pytest

from app.application.model_service import ModelService
from app.domain.models import ModelInfo
from app.domain.ports import ModelCatalog


pytestmark = pytest.mark.asyncio


class StubCatalog(ModelCatalog):
    def __init__(self, models: list[ModelInfo]):
        self.models = models

    async def list_available(self) -> list[ModelInfo]:
        return list(self.models)


def _m(id_, family, created):
    return ModelInfo(id=id_, display_name=id_, family=family,
                     created_at=datetime(*created, tzinfo=timezone.utc))


async def test_list_available_orders_best_family_then_newest():
    svc = ModelService(StubCatalog([
        _m("haiku-old", "haiku", (2025, 1, 1)),
        _m("opus-old", "opus", (2025, 1, 1)),
        _m("opus-new", "opus", (2026, 5, 1)),
        _m("sonnet-new", "sonnet", (2026, 4, 1)),
    ]))
    ids = [m.id for m in await svc.list_available()]
    assert ids == ["opus-new", "opus-old", "sonnet-new", "haiku-old"]


async def test_latest_per_family_picks_one_each():
    svc = ModelService(StubCatalog([
        _m("opus-old", "opus", (2025, 1, 1)),
        _m("opus-new", "opus", (2026, 5, 1)),
        _m("sonnet-1", "sonnet", (2026, 4, 1)),
        _m("haiku-1", "haiku", (2026, 3, 1)),
        _m("other-1", "other", (2026, 2, 1)),
    ]))
    picked = await svc.latest_per_family()
    assert [m.id for m in picked] == ["opus-new", "sonnet-1", "haiku-1", "other-1"]


async def test_latest_per_family_handles_empty():
    svc = ModelService(StubCatalog([]))
    assert await svc.latest_per_family() == []
