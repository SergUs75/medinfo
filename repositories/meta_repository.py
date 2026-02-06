# repositories/meta_repository.py

import sqlite3
from typing import Optional
from lib.logger import setup_logger

logger = setup_logger("meta_repository")


def get_meta_value(conn: sqlite3.Connection, key: str) -> Optional[str]:
    cur = conn.cursor()
    cur.execute(
        "SELECT value FROM meta WHERE key = ?",
        (key,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def set_meta_value(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO meta (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )
