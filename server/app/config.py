from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """학습 앱의 모든 환경 설정을 한 곳에 모은다. 새 설정은 여기 필드 추가만 하면 됨."""

    anthropic_api_key: str
    default_model: str = "claude-opus-4-7"
    default_thinking_budget: int = 0
    lessons_dir: str = "./lessons"
    conversations_dir: str = "./conversations"
    max_response_tokens: int = 8000
    max_tool_iterations: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
