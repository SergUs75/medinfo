# repositories/patient_confidant_repository.py
import sqlite3
from typing import Dict, Any, List
from lib.logger import setup_logger

logger = setup_logger("patient_confidant_repository")


def deactivate_existing_confidants(
    conn: sqlite3.Connection,
    health24_id: int,
) -> None:
    conn.execute(
        """
        UPDATE patient_confidants
        SET is_active = 0,
            deactivated_at = CURRENT_TIMESTAMP
        WHERE health24_id = ?
          AND is_active = 1
        """,
        (health24_id,),
    )


def insert_confidant(
    conn: sqlite3.Connection,
    health24_id: int,
    confidant: Dict[str, Any],
) -> None:
    conn.execute(
        """
        INSERT INTO patient_confidants (
            health24_id,
            confidant_id,
            first_name,
            last_name,
            second_name,
            gender,
            birth_date,
            relation_type,
            preferred_way_communication,
            phone,
            is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            health24_id,
            confidant.get("id"),
            confidant.get("first_name"),
            confidant.get("last_name"),
            confidant.get("second_name"),
            confidant.get("gender"),
            confidant.get("birth_date"),
            confidant.get("relation_type"),
            confidant.get("preferred_way_communication"),
            _extract_primary_phone(confidant),
        ),
    )


def sync_patient_confidants(
    conn: sqlite3.Connection,
    data: Dict[str, Any],
) -> None:
    health24_id = data["id"]

    person = data.get("person") or {}
    confidants: List[Dict[str, Any]] = person.get("confidant_persons") or []

    deactivate_existing_confidants(conn, health24_id)

    if not confidants:
        logger.info(
            "sync_patient_confidants: відсутні довірені особи health24_id=%s",
            health24_id,
        )
        return

    for confidant in confidants:
        insert_confidant(conn, health24_id, confidant)

    logger.info(
        "sync_patient_confidants: health24_id=%s count=%s",
        health24_id,
        len(confidants),
    )


def _extract_primary_phone(confidant: Dict[str, Any]) -> str | None:
    phones = confidant.get("phones") or []
    if not phones:
        return None
    return phones[0].get("number")
