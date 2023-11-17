from pydantic import PostgresDsn, RedisDsn, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):

    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn

    ADDRESS_URL: HttpUrl

    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )


settings = BaseConfig()
