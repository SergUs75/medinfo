# repositories/patient_address_repository.py

import sqlite3
from typing import Dict, Any
from datetime import datetime
from lib.logger import setup_logger

logger = setup_logger("patient_address_repository")


def sync_patient_addresses(conn: sqlite3.Connection, data: Dict[str, Any]) -> None:
    health24_id = data["id"]
    person = data.get("person") or {}
    addresses = person.get("addresses") or []

    now = datetime.utcnow().isoformat()

    # 1. Деактивуємо всі попередні адреси
    conn.execute(
        """
        UPDATE patient_addresses
        SET is_active = 0,
            valid_to = ?
        WHERE health24_id = ?
          AND is_active = 1
        """,
        (now, health24_id),
    )

    # 2. Вставляємо всі адреси з API як активні
    for addr in addresses:
        conn.execute(
            """
            INSERT INTO patient_addresses (
                health24_id,
                address_type_id,
                country_id,
                region_id,
                district_id,
                settlement_id,
                city_district_id,
                street_type_id,
                street,
                building,
                apartment,
                zip,
                is_active,
                valid_from,
                valid_to
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, NULL)
            """,
            (
                health24_id,
                addr.get("address_type_id"),
                addr.get("country_id"),
                addr.get("region_id"),
                addr.get("district_id"),
                addr.get("settlement_id"),
                addr.get("city_district_id"),
                addr.get("street_type_id"),
                addr.get("street"),
                addr.get("building"),
                addr.get("apartment"),
                addr.get("zip"),
                now,
            ),
        )

    logger.info(
        "Адреси пацієнта синхронізовано (health24_id=%s, кількість=%s)",
        health24_id,
        len(addresses),
    )


def get_active_address(conn: sqlite3.Connection, health24_id: int):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            at.title  AS address_type,
            c.title   AS country,
            r.title   AS region,
            s.title   AS settlement,
            st.title  AS street_type,
            pa.street,
            pa.building,
            pa.apartment,
            pa.zip,
            pa.is_active
        FROM patient_addresses pa
        LEFT JOIN address_types at ON at.id = pa.address_type_id
        LEFT JOIN countries c ON c.id = pa.country_id
        LEFT JOIN regions r ON r.id = pa.region_id
        LEFT JOIN settlements s ON s.id = pa.settlement_id
        LEFT JOIN street_types st ON st.id = pa.street_type_id
        WHERE pa.health24_id = ?
          AND pa.is_active = 1
        ORDER BY pa.valid_from DESC
        LIMIT 1
        """,
        (health24_id,),
    )
    row = cur.fetchone()
    print(row)
    return dict(row) if row else None

