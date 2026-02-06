# repositories/patient_profile_repository.py
import sqlite3
from typing import Optional
from lib.logger import setup_logger

logger = setup_logger("patient_profile_repository")


def create_patient_profile_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patient_profile (
            health24_id        INTEGER PRIMARY KEY,
            personality_id     INTEGER NOT NULL,
            api_id             TEXT NOT NULL,

            last_name          TEXT NOT NULL,
            first_name         TEXT NOT NULL,
            second_name        TEXT,

            full_name          TEXT NOT NULL,
            initials_name      TEXT,

            gender             TEXT,
            birth_date         TEXT,
            age                INTEGER,

            phone              TEXT,
            email              TEXT,

            declaration_number TEXT,
            doctor_employee_id INTEGER,
            doctor_name        TEXT,

            verification_code  TEXT,
            confirmed          INTEGER,
            has_full_profile   INTEGER,

            updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def create_patient_profile_indexes(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_profile_last_name
        ON patient_profile (last_name COLLATE NOCASE)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_profile_doctor
        ON patient_profile (doctor_employee_id)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_profile_birth_date
        ON patient_profile (birth_date)
    """)
    conn.commit()


def upsert_patient_profile(conn: sqlite3.Connection, data: dict) -> None:
    sql = """
        INSERT INTO patient_profile (
            health24_id,
            personality_id,
            api_id,
            last_name,
            first_name,
            second_name,
            full_name,
            initials_name,
            gender,
            birth_date,
            age,
            phone,
            email,
            declaration_number,
            doctor_employee_id,
            doctor_name,
            verification_code,
            confirmed,
            has_full_profile
        )
        VALUES (
            :health24_id,
            :personality_id,
            :api_id,
            :last_name,
            :first_name,
            :second_name,
            :full_name,
            :initials_name,
            :gender,
            :birth_date,
            :age,
            :phone,
            :email,
            :declaration_number,
            :doctor_employee_id,
            :doctor_name,
            :verification_code,
            :confirmed,
            :has_full_profile
        )
        ON CONFLICT(health24_id) DO UPDATE SET
            personality_id     = excluded.personality_id,
            api_id             = excluded.api_id,
            last_name          = excluded.last_name,
            first_name         = excluded.first_name,
            second_name        = excluded.second_name,
            full_name          = excluded.full_name,
            initials_name      = excluded.initials_name,
            gender             = excluded.gender,
            birth_date         = excluded.birth_date,
            age                = excluded.age,
            phone              = excluded.phone,
            email              = excluded.email,
            declaration_number = excluded.declaration_number,
            doctor_employee_id = excluded.doctor_employee_id,
            doctor_name        = excluded.doctor_name,
            verification_code  = excluded.verification_code,
            confirmed          = excluded.confirmed,
            has_full_profile   = excluded.has_full_profile,
            updated_at         = CURRENT_TIMESTAMP
    """
    conn.execute(sql, data)
    conn.commit()
