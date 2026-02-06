# repositories/patient_document_repository.py
import sqlite3
from typing import Dict, Any, Set, Tuple, List
from lib.logger import setup_logger

logger = setup_logger("patient_document_repository")


def resolve_document_type_id(conn: sqlite3.Connection, doc_type) -> int | None:
    if not doc_type:
        return None

    if isinstance(doc_type, dict):
        return doc_type.get("id")

    if isinstance(doc_type, str):
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM document_types WHERE code = ?",
            (doc_type,),
        )
        row = cur.fetchone()
        return row[0] if row else None

    return None




def sync_patient_documents(conn: sqlite3.Connection, data: Dict[str, Any]) -> None:
    health24_id = data["id"]
    current_docs: Set[Tuple] = set()

    person = data.get("person") or {}
    documents = person.get("documents") or []



    for doc in documents:
        doc_type_id = resolve_document_type_id(conn, doc.get("type"))
        key = (
            doc_type_id,
            doc.get("number"),
            doc.get("issued_at"),
            doc.get("expiration_date"),
            doc.get("issued_by"),
        )
        current_docs.add(key)

        conn.execute(
            """
            INSERT INTO patient_documents (
                health24_id,
                document_type,
                number,
                issued_at,
                expiration_date,
                issued_by,
                is_active
            )
            SELECT ?, ?, ?, ?, ?, ?, 1
            WHERE NOT EXISTS (
                SELECT 1 FROM patient_documents
                WHERE health24_id = ?
                  AND document_type IS ?
                  AND number IS ?
                  AND issued_at IS ?
                  AND expiration_date IS ?
                  AND issued_by IS ?
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

    if current_docs:
        placeholders = ",".join(["(?,?,?,?,?)"] * len(current_docs))
        conn.execute(
            f"""
            UPDATE patient_documents
            SET is_active = 0
            WHERE health24_id = ?
              AND is_active = 1
              AND (document_type, number,
                   issued_at, expiration_date, issued_by)
              NOT IN ({placeholders})
            """,
            (health24_id, *[v for d in current_docs for v in d]),
        )
    else:
        conn.execute(
            """
            UPDATE patient_documents
            SET is_active = 0
            WHERE health24_id = ?
              AND is_active = 1
            """,
            (health24_id,),
        )

    logger.debug(
        "Синхронізовано документи пацієнта health24_id=%s, активних=%s",
        health24_id,
        len(current_docs),
    )

def get_active_documents(conn: sqlite3.Connection, health24_id: int) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            COALESCE(dt.title, 'Невідомий тип документа'),
            d.number,
            d.issued_at,
            d.expiration_date,
            d.issued_by
        FROM patient_documents d
        LEFT JOIN document_types dt
            ON dt.id = d.document_type
        WHERE d.health24_id = ?
        AND d.is_active = 1
        ORDER BY d.issued_at DESC, d.id DESC
        """,
        (health24_id,),
    )

    rows = cur.fetchall()
    return [
        {
            "type": r[0],
            "number": r[1],
            "issued_at": r[2],
            "expiration_date": r[3],
            "issued_by": r[4],
        }
        for r in rows
    ]