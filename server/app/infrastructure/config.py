"""Single source of truth for environment-driven settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


_DEFAULT_SYSTEM_PROMPT = (
    "You are a personal study tutor. Use the provided MCP tools "
    "(write_lesson, read_answers, grade_lesson, list_lessons) to create lessons, "
    "read submitted answers, grade them, and list past lessons. "
    "Korean is the user's primary language. Be concise and concrete."
)


class Settings(BaseSettings):
    # Claude Code OAuth (via `claude` CLI login) is the auth path — no API key needed.
    default_model: str | None = None
    default_thinking_budget: int = 0
    system_prompt: str = _DEFAULT_SYSTEM_PROMPT
    lessons_dir: str = "./lessons"
    conversations_dir: str = "./conversations"
    max_response_tokens: int = 8000
    max_tool_iterations: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
