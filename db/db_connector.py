# repositories/db_connector.py
import sqlite3
from sqlite3 import Connection
from pathlib import Path

from lib.logger import setup_logger

logger = setup_logger("db_connector")

DB_PATH = Path(__file__).resolve().parent.parent / "med_assist.db"


def create_connection() -> Connection | None:
    try:
        conn = sqlite3.connect(
            DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        logger.error("DB connection error: %s", e)
        return None
