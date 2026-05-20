"""Conversation REST endpoints."""
from fastapi import APIRouter, HTTPException

from ...application.conversation_service import ConversationService
from ...domain.exceptions import ConversationNotFound, InvalidConversationId
from ...domain.models import ConversationId, new_conversation_id
from ..schemas import (
    ConversationCreateRequest, ConversationDetailDTO, ConversationSummaryDTO,
)


def make_router(service: ConversationService) -> APIRouter:
    router = APIRouter(prefix="/conversations")

    @router.get("")
    async def list_conversations() -> list[ConversationSummaryDTO]:
        return [
            ConversationSummaryDTO(
                id=s.id.value,
                title=s.title,
                created=s.created.isoformat(),
                message_count=s.message_count,
            )
            for s in service.list_summaries()
        ]

    @router.post("")
    async def create_conversation(payload: ConversationCreateRequest) -> ConversationSummaryDTO:
        cid = new_conversation_id()
        service.create(cid, payload.title)
        conv = service.get(cid)
        return ConversationSummaryDTO(
            id=conv.id.value,
            title=conv.title,
            created=conv.created.isoformat(),
            message_count=len(conv.messages),
        )

    @router.get("/{conversation_id}")
    async def get_conversation(conversation_id: str) -> ConversationDetailDTO:
        cid = _parse(conversation_id)
        try:
            conv = service.get(cid)
        except ConversationNotFound:
            raise HTTPException(status_code=404, detail=f"Conversation not found: {conversation_id}")
        return ConversationDetailDTO(
            id=conv.id.value,
            title=conv.title,
            created=conv.created.isoformat(),
            messages=list(conv.messages),
        )

    return router


def _parse(value: str) -> ConversationId:
    try:
        return ConversationId(value)
    except InvalidConversationId:
        raise HTTPException(status_code=400, detail=f"Invalid conversation_id: {value!r}")
