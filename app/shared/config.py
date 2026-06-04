from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    DB_POOL_SIZ: int = 10
    DB_MAX_OVERFLOW: int = 20

    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_TTL_HOURS: int = 24

    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
