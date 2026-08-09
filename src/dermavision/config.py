from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DERMA_", extra="ignore")

    app_name: str = "Dermavision"
    debug: bool = False
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/dermavision"
    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    open_meteo_geocoding_url: str = "https://geocoding-api.open-meteo.com/v1"
    weather_cache_ttl_seconds: int = 1800
    vision_models_dir: str = "models"
    llm_api_key: str = ""
    llm_enabled: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
