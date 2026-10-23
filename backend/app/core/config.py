from pydantic import Field as PydanticField
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Spec names (uppercase) — env vars DATABASE_URL / SECRET_KEY / CORS_ORIGINS
    # Lowercase aliases kept for backwards compat via populate_by_name + case-insensitive
    DATABASE_URL: str = PydanticField(
        default="sqlite:///./crop_recommend.db", validation_alias="DATABASE_URL"
    )
    SECRET_KEY: str = PydanticField(
        default="dev-secret-change-in-prod", validation_alias="SECRET_KEY"
    )
    CORS_ORIGINS: str = PydanticField(
        default="http://localhost:5173,http://localhost:3000",
        validation_alias="CORS_ORIGINS",
    )
    # Chat assistant (Gemini, OpenAI-compatible endpoint). Leave key empty to disable chat.
    LLM_API_KEY: str = PydanticField(default="", validation_alias="LLM_API_KEY")
    LLM_MODEL: str = PydanticField(default="gemini-3.8-flash", validation_alias="LLM_MODEL")
    LLM_FALLBACK_MODEL: str = PydanticField(
        default="gemini-flash-lite-latest", validation_alias="LLM_FALLBACK_MODEL"
    )
    LLM_BASE_URL: str = PydanticField(
        default="https://generativelanguage.googleapis.com/v1beta/openai",
        validation_alias="LLM_BASE_URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    # Backwards-compat lowercase accessors
    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY

    @property
    def cors_origins(self) -> str:
        return self.CORS_ORIGINS

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
