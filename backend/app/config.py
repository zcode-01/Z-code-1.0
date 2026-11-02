"""
Z-Code Backend — Application Settings
Reads from .env file via python-dotenv.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = "zcode-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # NVIDIA AI (Nemotron 3 Ultra) - loaded from .env
    NVIDIA_API_KEY: str = ""
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b"

    # Gemini AI (optional fallback)
    GEMINI_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./zcode.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost,http://127.0.0.1,null,file://"

    model_config = SettingsConfigDict(
        env_file=(_ENV_FILE, ".env"),
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
