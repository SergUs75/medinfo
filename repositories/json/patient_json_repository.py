# repositories/patient_json_repository.py
import sqlite3
from typing import Optional

from lib.logger import setup_logger

logger = setup_logger("patient_json_repository")


def create_patient_json_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS patient_json (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            health24_id INTEGER NOT NULL,
            api_id TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_patient_json_health24_id
        ON patient_json (health24_id)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_patient_json_created_at
        ON patient_json (created_at)
        """
    )
    conn.commit()


def insert_patient_json(
    conn: sqlite3.Connection,
    health24_id: int,
    api_id: str,
    json_data: str,
) -> None:
    conn.execute(
        """
        INSERT INTO patient_json (
            health24_id,
            api_id,
            json_data
        )
        VALUES (?, ?, ?)
        """,
        (health24_id, api_id, json_data),
    )
    logger.debug(
        "Збережено JSON пацієнта health24_id=%s",
        health24_id,
    )


def get_latest_patient_json(conn, health24_id: int) -> str | None:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT json_data
        FROM patient_json
        WHERE health24_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (health24_id,),
    )
    row = cur.fetchone()
    return row[0] if row else None

def patient_json_exists(conn, health24_id: int) -> bool:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT 1
        FROM patient_json
        WHERE health24_id = ?
        LIMIT 1
        """,
        (health24_id,)
    )
    return cur.fetchone() is not None

