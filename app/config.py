"""Typed configuration that gets read once from the environment."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ProviderName = Literal["mock", "gemini"]


class Settings(BaseSettings):
    """Runtime configuration. Defaults select the mock adapters.

    A clean clone with no .env must boot and serve, so every field has a
    default and none of them require a credential.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    transcribe_provider: ProviderName = "mock"
    ocr_provider: ProviderName = "mock"

    # Optional on purpose for mock. The Gemini adapters validate the key themselves when they are constructed anyway.
    gemini_api_key: str | None = None

    max_upload_bytes: int = 25 * 1024 * 1024


settings = Settings()
