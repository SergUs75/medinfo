# repositories/patient_phone_repository.py
import sqlite3
from typing import Dict, Any, List
from lib.utils import lower_first
from lib.logger import setup_logger

logger = setup_logger("patient_phone_repository")


def phone_exists(conn: sqlite3.Connection, health24_id: int, phone: str) -> bool:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT 1
        FROM patient_phones
        WHERE health24_id = ? AND phone = ?
        LIMIT 1
        """,
        (health24_id, phone),
    )
    return cur.fetchone() is not None


def sync_patient_phones(conn: sqlite3.Connection, data: Dict[str, Any]) -> None:
    health24_id = data["id"]

    def insert_phone(phone: str | None, phone_type: str | None, source: str):
        if not phone:
            return
        phone_type = lower_first(phone_type)
        if phone_exists(conn, health24_id, phone):
            return
        conn.execute(
            """
            INSERT INTO patient_phones (
                health24_id,
                phone,
                type,
                source,
                is_active,
                valid_from
            )
            VALUES (?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
            """,
            (
                health24_id,
                phone,
                phone_type,
                source,
            ),
        )

    for phone in data.get("phones", []):
        insert_phone(phone.get("number"), phone.get("type_name"), "patient.phones")

    person = data.get("person") or {}
    for phone in person.get("phones", []):
        insert_phone(phone.get("number"), phone.get("type_name"), "person.phones")

    primary = data.get("primary_auth_method")
    if primary:
        insert_phone(primary.get("phone_number"), primary.get("type_name"), "primary_auth")

    for auth in data.get("authentication_methods", []):
        insert_phone(auth.get("phone_number"), auth.get("type_name"), "auth_method")

    conn.execute(
        """
        UPDATE patient_phones
        SET is_active = 0
        WHERE health24_id = ?
        """,
        (health24_id,),
    )

    conn.execute(
        """
        UPDATE patient_phones
        SET is_active = 1
        WHERE id = (
            SELECT id
            FROM patient_phones
            WHERE health24_id = ?
            ORDER BY valid_from DESC
            LIMIT 1
        )
        """,
        (health24_id,),
    )


def get_phones(conn: sqlite3.Connection, health24_id: int) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            phone,
            type,
            is_active
        FROM patient_phones
        WHERE health24_id = ?
        ORDER BY valid_from ASC
        """,
        (health24_id,),
    )
    rows = cur.fetchall()
    return [
        {
            "phone": r[0],
            "type": r[1],
            "is_active": bool(r[2]),
        }
        for r in rows
    ]
