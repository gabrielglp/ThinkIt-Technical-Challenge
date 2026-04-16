from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://orders_user:orders_pass@db:5432/orders_db"
    database_url_sync: str = "postgresql://orders_user:orders_pass@db:5432/orders_db"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    smtp_host: str = "simintermediacoes.com"
    smtp_port: int = 465
    smtp_user: str = "noreply@simintermediacoes.com"
    smtp_password: str = ""
    smtp_from_email: str = "noreply@simintermediacoes.com"
    app_url: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
