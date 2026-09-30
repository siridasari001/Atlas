from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    atlas_env: str = "development"
    llm_provider: str = "openai"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()