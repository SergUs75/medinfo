import json
import sqlite3
from typing import Dict, Any, Optional

from api.health24.patient_client import PatientClient
from repositories.json.patient_json_repository import (
    insert_patient_json,
    patient_json_exists,
)
from repositories.patient.patient_repository import upsert_patient_data
from repositories.patient.patient_phone_repository import sync_patient_phones
from repositories.patient.patient_address_repository import sync_patient_addresses
from repositories.patient.patient_document_repository import sync_patient_documents
from repositories.patient.patient_declaration_repository import sync_patient_declaration

from lib.logger import setup_logger

logger = setup_logger("patient_load_service")


# ======================
# Доманні помилки
# ======================

class PatientLoadError(Exception):
    """Загальна помилка завантаження пацієнта"""
    pass


class PatientApiUnavailable(PatientLoadError):
    """API недоступне, локальні дані відсутні"""
    pass


class PatientNotFound(PatientLoadError):
    """Пацієнт не знайдений в API"""
    pass


# ======================
# Сервіс завантаження
# ======================

class PatientLoadService:
    """
    Сервіс завантаження та синхронізації повних даних пацієнта.

    Принципи:
    - API викликається ЗАВЖДИ
    - API — джерело істини
    - SQLite — кеш + історія
    - Уся синхронізація — транзакційна
    - GUI після виконання може безпечно читати дані з БД
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        api_client: PatientClient,
    ):
        self.conn = conn
        self.api_client = api_client

    # ======================
    # Публічний API
    # ======================

    def load_patient(self, health24_id: int) -> None:
        """
        Основний сценарій:
        1. Завжди намагаємось отримати дані з API
        2. Якщо API недоступне:
           - якщо локальні дані є → offline fallback
           - якщо локальних даних нема → помилка
        3. Якщо API доступне → синхронізуємо дані
        """

        logger.info(
            "Початок завантаження даних пацієнта (health24_id=%s)",
            health24_id,
        )

        # ─────────────────────────────
        # Спроба отримати дані з API
        # ─────────────────────────────
        try:
            patient_data = self.api_client.get_patient(health24_id)
            api_available = True
            logger.debug(
                "Дані пацієнта успішно отримані з API (health24_id=%s)",
                health24_id,
            )
        except Exception as e:
            api_available = False
            logger.warning(
                "API недоступне для пацієнта health24_id=%s. Причина: %s",
                health24_id,
                e,
            )

        # ─────────────────────────────
        # OFFLINE FALLBACK
        # ─────────────────────────────
        if not api_available:
            if patient_json_exists(self.conn, health24_id):
                logger.info(
                    "Використано локальні дані пацієнта "
                    "(offline режим, health24_id=%s)",
                    health24_id,
                )
                return

            logger.error(
                "API недоступне і локальні дані пацієнта відсутні "
                "(health24_id=%s)",
                health24_id,
            )
            raise PatientApiUnavailable(
                "API недоступне, локальні дані пацієнта відсутні"
            )

        # ─────────────────────────────
        # ONLINE SYNC
        # ─────────────────────────────
        try:
            self._sync_patient(patient_data)
        except Exception as e:
            logger.exception(
                "Помилка синхронізації даних пацієнта (health24_id=%s)",
                health24_id,
            )
            raise PatientLoadError(str(e))

        logger.info(
            "Завантаження та синхронізація пацієнта завершені успішно "
            "(health24_id=%s)",
            health24_id,
        )

    # ======================
    # Внутрішня логіка
    # ======================

    def _sync_patient(self, data: Dict[str, Any]) -> None:
        """
        Транзакційна синхронізація даних пацієнта.
        """

        health24_id = data.get("id")

        logger.debug(
            "Початок синхронізації даних пацієнта з БД "
            "(health24_id=%s)",
            health24_id,
        )

        self.conn.execute("BEGIN")

        try:
            # 1. Збереження повного JSON (snapshot / історія)
            insert_patient_json(
                conn=self.conn,
                health24_id=data["id"],
                api_id=data["api_id"],
                json_data=json.dumps(data, ensure_ascii=False),
            )

            # 2. Базовий профіль пацієнта
            upsert_patient_data(
                self.conn,
                (
                    data["id"],
                    data["api_id"],
                    data["personality_id"],
                    self._extract_employee_id(data),
                    data["last_name"],
                    data["first_name"],
                    data.get("second_name"),
                    data.get("birth_date"),
                    data.get("gender"),
                ),
            )

            # 3. Проєкційні таблиці
            sync_patient_phones(self.conn, data)
            sync_patient_addresses(self.conn, data)
            sync_patient_documents(self.conn, data)
            sync_patient_declaration(self.conn, data)

            self.conn.commit()

            logger.debug(
                "Синхронізація даних пацієнта з БД виконана успішно "
                "(health24_id=%s)",
                health24_id,
            )

        except Exception:
            self.conn.rollback()
            logger.error(
                "Транзакцію синхронізації даних пацієнта відхилено "
                "(health24_id=%s)",
                health24_id,
            )
            raise

    # ======================
    # Допоміжні методи
    # ======================

    @staticmethod
    def _extract_employee_id(data: Dict[str, Any]) -> Optional[int]:
        declaration = data.get("declaration") or {}
        employee = declaration.get("employee") or {}
        return employee.get("id")
