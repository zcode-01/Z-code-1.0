"""
Z-Code Backend — Application Settings
Reads from .env file via python-dotenv.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = "zcode-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Gemini AI
    GEMINI_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./zcode.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost,http://127.0.0.1,null,file://"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
