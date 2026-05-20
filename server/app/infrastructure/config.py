"""Single source of truth for environment-driven settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str
    default_model: str = "claude-opus-4-7"
    default_thinking_budget: int = 0
    lessons_dir: str = "./lessons"
    max_response_tokens: int = 8000
    max_tool_iterations: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
