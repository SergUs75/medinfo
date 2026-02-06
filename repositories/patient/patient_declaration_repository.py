# repositories/patient_declaration_repository.py
import sqlite3
from typing import Optional, Dict, Any
from lib.logger import setup_logger

logger = setup_logger("patient_declaration_repository")


def deactivate_existing_declarations(conn: sqlite3.Connection, health24_id: int) -> None:
    conn.execute(
        """
        UPDATE patient_declarations
        SET is_active = 0,
            end_date = CURRENT_TIMESTAMP
        WHERE health24_id = ?
          AND is_active = 1
        """,
        (health24_id,),
    )


def insert_declaration(
    conn: sqlite3.Connection,
    health24_id: int,
    declaration: Dict[str, Any],
) -> None:
    employee = declaration.get("employee") or {}
    division = employee.get("division") or {}

    employee_name = employee.get("name")
    division_name = division.get("name")

    conn.execute(
        """
        INSERT INTO patient_declarations (
            health24_id,
            declaration_id,
            employee_id,
            employee_name,
            division_id,
            division_name,
            start_date,
            end_date,
            number,
            is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            health24_id,
            declaration.get("id"),
            employee.get("id"),
            employee_name,
            division.get("id"),
            division_name,
            declaration.get("start_date"),
            declaration.get("end_date"),
            declaration.get("number"),
        ),
    )


def sync_patient_declaration(conn: sqlite3.Connection, data: Dict[str, Any]) -> None:
    health24_id = data["id"]
    declaration = data.get("declaration")

    if not declaration:
        logger.info(
            "sync_patient_declaration: декларація відсутня health24_id=%s",
            health24_id,
        )
        return

    decl_id = declaration.get("id")

    if declaration_exists(conn, decl_id):
        update_declaration(conn, declaration)
    else:
        deactivate_existing_declarations(conn, health24_id)
        insert_declaration(conn, health24_id, declaration)


    logger.info(
        "sync_patient_declaration: синхронізовано health24_id=%s",
        health24_id,
    )

def declaration_exists(conn: sqlite3.Connection, declaration_id: int) -> bool:
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM patient_declarations WHERE declaration_id = ? LIMIT 1",
        (declaration_id,),
    )
    return cur.fetchone() is not None

def update_declaration(
    conn: sqlite3.Connection,
    declaration: Dict[str, Any],
) -> None:
    employee = declaration.get("employee") or {}
    division = employee.get("division") or {}

    conn.execute(
        """
        UPDATE patient_declarations
        SET
            employee_id = ?,
            employee_name = ?,
            division_id = ?,
            division_name = ?,
            start_date = ?,
            end_date = ?,
            number = ?
        WHERE declaration_id = ?
        """,
        (
            employee.get("id"),
            employee.get("name"),
            division.get("id"),
            division.get("name"),
            declaration.get("start_date"),
            declaration.get("end_date"),
            declaration.get("number"),
            declaration.get("id"),
        ),
    )

def get_latest_declaration(
    conn: sqlite3.Connection,
    health24_id: int,
) -> Optional[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            employee_id,
            declaration_id,
            employee_name,
            division_id,
            division_name,
            start_date,
            end_date,
            number,
            is_active
        FROM patient_declarations
        WHERE health24_id = ?
        ORDER BY is_active DESC, start_date DESC
        LIMIT 1
        """,
        (health24_id,),
    )
    row = cur.fetchone()
    if not row:
        return None

    return {
        "employee_id": row[0],
        "declaration_id": row[1],
        "employee_name": row[2],
        "division_id": row[3],
        "division_name": row[4],
        "start_date": row[5],
        "end_date": row[6],
        "number": row[7],
        "is_active": bool(row[8]),
    }
