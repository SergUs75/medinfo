# auth_manager.py
import base64
import json
import time
from datetime import datetime
from typing import Optional

from config.config_loader import settings
from lib.logger import setup_logger

logger = setup_logger("auth_manager")


def extract_exp_from_jwt(access_token: str) -> Optional[int]:
    try:
        _, payload_b64, _ = access_token.split(".")
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64).decode("utf-8")
        payload = json.loads(payload_json)
        return payload.get("exp")
    except Exception as e:
        logger.error("Не вдалося витягти exp з access token: %s", e)
        return None


def exp_to_human(exp_unix: int) -> tuple[str, str]:
    exp_dt = datetime.fromtimestamp(exp_unix)
    now = int(time.time())
    delta = max(0, exp_unix - now)

    hours = delta // 3600
    minutes = (delta % 3600) // 60

    exp_str = exp_dt.strftime("%d.%m.%Y %H:%M")
    left_str = f"{hours} год {minutes} хв"

    return exp_str, left_str


def is_token_valid(access_token: str, buffer_seconds: int = 60) -> bool:
    exp = extract_exp_from_jwt(access_token)
    if not exp:
        return False
    return exp > (int(time.time()) + buffer_seconds)


def get_access_token() -> Optional[str]:
    access_token = settings.get("api.access_token")

    if not access_token:
        logger.warning("Access token відсутній у налаштуваннях")
        return None

    exp = extract_exp_from_jwt(access_token)
    if not exp:
        logger.error("Access token некоректний або без exp")
        return None

    if is_token_valid(access_token):
        exp_str, left_str = exp_to_human(exp)
        logger.info(
            "Access token дійсний до %s (залишилось: %s)",
            exp_str,
            left_str,
        )
        return access_token

    exp_str, _ = exp_to_human(exp)
    logger.warning(
        "Access token прострочений (діяв до %s)",
        exp_str,
    )
    return None


def save_access_token(access_token: str) -> bool:
    exp = extract_exp_from_jwt(access_token)
    if not exp:
        logger.error("Спроба зберегти некоректний access token")
        return False

    settings.set("api.access_token", access_token)
    settings.save_settings()

    exp_str, left_str = exp_to_human(exp)
    logger.info(
        "Access token збережено. Чинний до %s (залишилось: %s)",
        exp_str,
        left_str,
    )
    return True


if __name__ == "__main__":
    token = get_access_token()
    if token:
        logger.info("Токен готовий до використання")
    else:
        logger.error("Токен недійсний або відсутній")
