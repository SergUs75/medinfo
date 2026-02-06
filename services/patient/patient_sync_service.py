import sqlite3
from typing import Dict, Any, List

from repositories.patient.patient_repository import upsert_patient_data
from api.health24.patient_client import PatientClient
from lib.logger import setup_logger

logger = setup_logger("patient_sync_service")


class PatientSyncService:
    def __init__(self, conn: sqlite3.Connection, api_client: PatientClient):
        self.conn = conn
        self.api_client = api_client

    def sync_patient_list(self, employee_id: str) -> int:
        try:
            logger.info("Початок синхронізації списку пацієнтів для employee_id=%s", employee_id)
            patients = self.api_client.get_patients(employee_id)

            if not patients:
                logger.info("Не отримано жодного пацієнта з API")
                return 0

            count = 0
            for p in patients:
                # Перетворення dict -> tuple, який очікує upsert_patient_data
                # Порядок: health24_id, api_id, personality_id, employee_id, last_name, first_name, second_name, birth_date, gender
                
                # Припускаємо, що API повертає ці поля. Якщо ні, треба буде робити fetch деталей.
                # Спроба витягти мінімально необхідні поля.
                
                try:
                    # Примітка: employee_id передаємо як аргумент, якщо в об'єкті нема
                    p_employee_id = self._extract_employee_id(p) or int(employee_id)
                    
                    data_tuple = (
                        p.get("id"),
                        p.get("api_id") or str(p.get("id")), # fallback якщо api_id нема
                        p.get("personality_id") or str(p.get("id")), # fallback
                        p_employee_id,
                        p.get("last_name"),
                        p.get("first_name"),
                        p.get("second_name"),
                        p.get("birth_date"),
                        p.get("gender"),
                    )
                    
                    upsert_patient_data(self.conn, data_tuple)
                    count += 1
                except Exception as e:
                    logger.warning("Не вдалося зберегти пацієнта %s: %s", p.get("id"), e)

            logger.info("Синхронізовано %s пацієнтів", count)
            return count

        except Exception as e:
            logger.error("sync_patient_list error: %s", e)
            return 0

    def _extract_employee_id(self, data: Dict[str, Any]) -> int | None:
        # Спроба дістати employee_id з вкладеної декларації, як в load_service
        declaration = data.get("declaration")
        if isinstance(declaration, dict):
            employee = declaration.get("employee")
            if isinstance(employee, dict):
                return employee.get("id")
        return None
