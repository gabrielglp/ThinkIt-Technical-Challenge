from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://orders_user:orders_pass@db:5432/orders_db"
    database_url_sync: str = "postgresql://orders_user:orders_pass@db:5432/orders_db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS — string separada por vírgula vinda do .env
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
