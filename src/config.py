from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.enums import Environments


class Settings(BaseSettings):
    ENVIRONMENT: Environments = Environments.LOCAL

    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    TELEGRAM_PHONE: str
    TELEGRAM_USERNAME: str
    TELEGRAM_CHANNEL_ID: str
    TELEGRAM_PASSWORD: str

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file='../.env',
        env_file_encoding='utf-8'
    )


settings: Settings = Settings()
