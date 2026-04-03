from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configurações do aplicativo, lidas automaticamente do arquivo .env.
    """
    APP_NAME: str = "Gôndola.ai API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # ── Database ──
    DATABASE_URL: str = "sqlite+aiosqlite:///./gondola.db"

    # ── Google Gemini (Sprint 4) ──
    GEMINI_API_KEY: str = ""

    # ── WhatsApp Z-API (Sprint 5) ──
    ZAPI_INSTANCE_ID: str = ""
    ZAPI_TOKEN: str = ""

    # ── Localização da loja (padrão: Rio de Janeiro) ──
    STORE_LATITUDE: float = -22.9068
    STORE_LONGITUDE: float = -43.1729

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    """Singleton das configurações (cacheia na primeira chamada)."""
    return Settings()
