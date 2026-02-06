# file_utils.py
import json
import os
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def save_data_to_json(filename: str, data: Any):
    """Зберігає дані у JSON-файл."""
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Дані успішно збережено у {filename}")
    except Exception as e:
        logger.error(f"Помилка збереження у {filename}: {e}")

def load_data_from_json(filename: str) -> Optional[Dict]:
    """Завантажує дані з JSON-файлу."""
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Файл {filename} не знайдено.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Помилка декодування JSON у {filename}: {e}")
        return None