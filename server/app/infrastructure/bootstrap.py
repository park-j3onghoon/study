"""Composition root. All dependency wiring lives here.

Adding a new tool: import it and append to the `tools` list inside build().
Adding a new repository: instantiate it instead of DiskLessonRepository.
"""
from pathlib import Path

from ..adapters.anthropic_agent import AnthropicAgent
from ..adapters.disk_repository import DiskLessonRepository
from ..adapters.tools.echo import EchoTool
from ..adapters.tools.grade_lesson import GradeLessonTool
from ..adapters.tools.list_lessons import ListLessonsTool
from ..adapters.tools.read_answers import ReadAnswersTool
from ..adapters.tools.write_lesson import WriteLessonTool
from ..application.chat_service import ChatService
from ..application.lesson_service import LessonService
from .config import settings


class AppState:
    def __init__(self, lesson_service: LessonService, chat_service: ChatService):
        self.lesson_service = lesson_service
        self.chat_service = chat_service


def build() -> AppState:
    repo = DiskLessonRepository(Path(settings.lessons_dir))
    lesson_service = LessonService(repo)
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
    return AppState(lesson_service=lesson_service, chat_service=chat_service)
