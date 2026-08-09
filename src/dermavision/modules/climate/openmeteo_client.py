import httpx

from dermavision.config import get_settings


class OpenMeteoClient:
    def __init__(self, base_url: str | None = None) -> None:
        settings = get_settings()
        self._base_url = base_url or settings.open_meteo_base_url

    def current(self, latitude: float, longitude: float) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,uv_index",
            "daily": "uv_index_max",
            "timezone": "auto",
        }
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{self._base_url}/forecast", params=params)
            response.raise_for_status()
            return response.json()
