import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Smart Voice Notes Assistant"
    DEBUG: bool = True
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/voicenotes")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Cloudflare R2 / S3 Settings
    S3_ENDPOINT_URL: Optional[str] = os.getenv("S3_ENDPOINT_URL")
    S3_ACCESS_KEY_ID: Optional[str] = os.getenv("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: Optional[str] = os.getenv("S3_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "voice-notes")
    S3_PUBLIC_URL: Optional[str] = os.getenv("S3_PUBLIC_URL") # For serving files

    # ML Settings
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    SPACY_MODEL: str = "en_core_web_sm"
    CNN_MODEL_PATH: str = "app/ml/models/cnn_model.keras"
    TOKENIZER_PATH: str = "app/ml/models/tokenizer.pkl"
    MAX_AUDIO_SIZE_MB: int = 25
    ALLOWED_AUDIO_EXTENSIONS: list[str] = [".wav", ".mp3", ".ogg", ".webm", ".m4a", ".mp4"]
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp")
    
    # Caching & Rate Limiting
    CACHE_TTL_SECONDS: int = 300
    RATE_LIMIT_TRANSCRIBE: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
