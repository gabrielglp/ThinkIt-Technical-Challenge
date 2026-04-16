from typing import Any, Optional

from pydantic import field_validator
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

    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    app_url: str = "http://localhost:3000"

    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_bucket_name: str = "ebook"
    aws_region: str = "US1"
    aws_s3_endpoint: str = "https://gateway.storjshare.io"

    @field_validator("smtp_port", mode="before")
    @classmethod
    def empty_str_to_none_int(cls, v: Any) -> Any:
        if v == "":
            return None
        return v

    @field_validator("smtp_host", "smtp_user", "smtp_password", "smtp_from_email",
                     "aws_access_key_id", "aws_secret_access_key", mode="before")
    @classmethod
    def empty_str_to_none_str(cls, v: Any) -> Any:
        if v == "":
            return None
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
