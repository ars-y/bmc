from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):

    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_JWT_EXPIRE_MINUTES: int = 60*24*7
    REFRESH_JWT_EXPIRE_MINUTES: int = 60*24*30
    RESET_JWT_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )


auth_settings = AuthConfig()
