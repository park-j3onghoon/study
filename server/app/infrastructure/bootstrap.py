"""Composition root. All dependency wiring lives here.

Adding a new tool: import it and append to the `tools` list inside build().
Adding a new repository: instantiate it instead of DiskLessonRepository.
"""
from pathlib import Path

from ..adapters.anthropic_agent import AnthropicAgent
from ..adapters.anthropic_model_catalog import AnthropicModelCatalog
from ..adapters.disk_conversation_repository import DiskConversationRepository
from ..adapters.disk_repository import DiskLessonRepository
from ..adapters.file_event_stream import FileEventStream
from ..adapters.tools.echo import EchoTool
from ..adapters.tools.grade_lesson import GradeLessonTool
from ..adapters.tools.list_lessons import ListLessonsTool
from ..adapters.tools.read_answers import ReadAnswersTool
from ..adapters.tools.write_lesson import WriteLessonTool
from ..application.chat_service import ChatService
from ..application.conversation_service import ConversationService
from ..application.lesson_service import LessonService
from ..application.model_service import ModelService
from ..domain.ports import EventStream
from .config import settings


class AppState:
    def __init__(
        self,
        lesson_service: LessonService,
        chat_service: ChatService,
        conversation_service: ConversationService,
        event_stream: EventStream,
        model_service: ModelService,
    ):
        self.lesson_service = lesson_service
        self.chat_service = chat_service
        self.conversation_service = conversation_service
        self.event_stream = event_stream
        self.model_service = model_service


def build() -> AppState:
    lessons_path = Path(settings.lessons_dir)
    conversations_path = Path(settings.conversations_dir)
    lesson_repo = DiskLessonRepository(lessons_path)
    conversation_repo = DiskConversationRepository(conversations_path)
    lesson_service = LessonService(lesson_repo)
    conversation_service = ConversationService(conversation_repo)
    tools = [
        EchoTool(),
        WriteLessonTool(lesson_service),
        ReadAnswersTool(lesson_service),
        GradeLessonTool(lesson_service),
        ListLessonsTool(lesson_service),
    ]
    agent = AnthropicAgent(
        api_key=settings.anthropic_api_key,
        default_model=settings.default_model,
        default_thinking_budget=settings.default_thinking_budget,
        tools=tools,
        max_iterations=settings.max_tool_iterations,
        max_response_tokens=settings.max_response_tokens,
    )
    chat_service = ChatService(agent)
    event_stream = FileEventStream(lessons_path)
    model_catalog = AnthropicModelCatalog(api_key=settings.anthropic_api_key)
    model_service = ModelService(model_catalog)
    return AppState(
        lesson_service=lesson_service,
        chat_service=chat_service,
        conversation_service=conversation_service,
        event_stream=event_stream,
        model_service=model_service,
    )
