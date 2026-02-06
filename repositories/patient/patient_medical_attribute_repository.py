# repositories/patient_medical_attribute_repository.py
import sqlite3
from typing import Dict, Any, Set, Tuple
from lib.logger import setup_logger

logger = setup_logger("patient_medical_attribute_repository")


def sync_patient_medical_attributes(
    conn: sqlite3.Connection,
    data: Dict[str, Any],
) -> None:
    health24_id = data["id"]
    current_attrs: Set[Tuple] = set()

    attributes = data.get("medical_attributes") or []

    for attr in attributes:
        key = (
            attr.get("code"),
            attr.get("value"),
        )
        current_attrs.add(key)

        conn.execute(
            """
            INSERT INTO patient_medical_attributes (
                health24_id,
                code,
                value,
                is_active
            )
            SELECT ?, ?, ?, 1
            WHERE NOT EXISTS (
                SELECT 1 FROM patient_medical_attributes
                WHERE health24_id = ?
                  AND code IS ?
                  AND value IS ?
                  AND is_active = 1
            )
            """,
            (
                health24_id,
                *key,
                health24_id,
                *key,
            ),
        )

    if current_attrs:
        placeholders = ",".join(["(?,?)"] * len(current_attrs))
        conn.execute(
            f"""
            UPDATE patient_medical_attributes
            SET is_active = 0
            WHERE health24_id = ?
              AND is_active = 1
              AND (code, value) NOT IN ({placeholders})
            """,
            (health24_id, *[v for a in current_attrs for v in a]),
        )
    else:
        conn.execute(
            """
            UPDATE patient_medical_attributes
            SET is_active = 0
            WHERE health24_id = ?
              AND is_active = 1
            """,
            (health24_id,),
        )

    logger.debug(
        "Синхронізовано медичні атрибути пацієнта health24_id=%s, активних=%s",
        health24_id,
        len(current_attrs),
    )

