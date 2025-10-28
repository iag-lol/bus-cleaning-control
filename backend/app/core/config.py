"""Application configuration."""

from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Bus Cleaning Control"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./bus_cleaning.db"

    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    # Redis
    REDIS_URL: Optional[str] = None
    USE_REDIS: bool = False

    # ML/AI
    ML_MODEL_PATH: str = "/app/ml/models/cleaning_classifier.onnx"
    ML_CONFIDENCE_THRESHOLD_CLEAN: float = 0.70
    ML_CONFIDENCE_THRESHOLD_DIRTY: float = 0.65
    ML_USE_DUMMY: bool = True
    ML_INFERENCE_TIMEOUT: int = 5

    # File Uploads
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def assemble_extensions(cls, v: str | List[str]) -> List[str]:
        """Parse allowed extensions from comma-separated string or list."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Alerts
    ALERT_DIRTY_THRESHOLD: int = 2
    ALERT_DIRTY_WINDOW_HOURS: int = 72
    ALERT_UNCERTAIN_THRESHOLD: int = 3

    # Web Push
    VAPID_PRIVATE_KEY: Optional[str] = None
    VAPID_PUBLIC_KEY: Optional[str] = None
    VAPID_ADMIN_EMAIL: str = "admin@buses.cl"

    # Timezone
    TZ: str = "America/Santiago"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development" or self.DEBUG


# Global settings instance
settings = Settings()
