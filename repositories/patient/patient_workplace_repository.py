# repositories/db_initializer.py
import sqlite3
from typing import Optional

from repositories.db_connector import create_connection

from repositories.patient_repository import (
    create_patient_table,
    create_patient_indexes,
)

from repositories.json.patient_json_repository import (
    create_patient_json_table,
    create_patient_json_indexes,
)

from repositories.patient_phone_repository import (
    create_patient_phone_table,
    create_patient_phone_indexes,
)

from repositories.patient_address_repository import (
    create_patient_address_table,
    create_patient_address_indexes,
)

from repositories.patient_document_repository import (
    create_patient_document_table,
    create_patient_document_indexes,
)

from repositories.patient_workplace_repository import (
    create_patient_workplace_table,
    create_patient_workplace_indexes,
)


def initialize_db() -> Optional[sqlite3.Connection]:
    conn = create_connection()
    if conn is None:
        return None

    try:
        create_patient_table(conn)
        create_patient_indexes(conn)

        create_patient_json_table(conn)
        create_patient_json_indexes(conn)

        create_patient_phone_table(conn)
        create_patient_phone_indexes(conn)

        create_patient_address_table(conn)
        create_patient_address_indexes(conn)

        create_patient_document_table(conn)
        create_patient_document_indexes(conn)

        create_patient_workplace_table(conn)
        create_patient_workplace_indexes(conn)

        conn.commit()
        return conn

    except Exception:
        conn.rollback()
        conn.close()
        return None
