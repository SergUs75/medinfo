# api/base_client.py

import requests
from auth_manager import get_access_token
from config.config_loader import settings
from lib.logger import setup_logger

logger = setup_logger("base_client")


class BaseApiClient:
    """
    Базовий API-клієнт.
    ВІДПОВІДАЛЬНІСТЬ:
    - base_url
    - session
    - headers
    - timeout
    """

    def __init__(self):
        self.base_url = settings.get("api.base_url")
        self.timeout = settings.get("api_timeout", 10)

        self.session = requests.Session()

    def _headers(self) -> dict:
        token = get_access_token()
        if not token:
            raise RuntimeError("Відсутній access token")

        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
