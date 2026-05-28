"""Model catalog REST endpoint."""
import logging

from fastapi import APIRouter, HTTPException

from ...application.model_service import ModelService
from ..schemas import ModelDTO


log = logging.getLogger(__name__)


def make_router(service: ModelService) -> APIRouter:
    router = APIRouter(prefix="/models")

    @router.get("")
    async def list_models() -> list[ModelDTO]:
        try:
            models = await service.latest_per_family()
        except Exception as exc:
            log.warning("model catalog fetch failed: %s", exc)
            raise HTTPException(status_code=503, detail=f"Model catalog unavailable: {exc}")
        return [
            ModelDTO(
                id=m.id,
                display_name=m.display_name,
                family=m.family,
                created_at=m.created_at.isoformat(),
            )
            for m in models
        ]

    return router
