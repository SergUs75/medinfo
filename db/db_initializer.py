# db/db_initializer.py
import sqlite3
from typing import Optional
from db.db_connector import create_connection

def initialize_db() -> Optional[sqlite3.Connection]:
    conn = create_connection()
    if conn is None:
        return None

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        health24_id INTEGER PRIMARY KEY,
        api_id TEXT NOT NULL,
        personality_id INTEGER,
        employee_id INTEGER,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        second_name TEXT,
        birth_date TEXT,
        gender TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_json (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        health24_id INTEGER NOT NULL,
        api_id TEXT NOT NULL,
        json_data TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_phones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        health24_id INTEGER NOT NULL,
        phone TEXT NOT NULL,
        type TEXT,
        is_primary INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        valid_from TEXT DEFAULT CURRENT_TIMESTAMP,
        valid_to TEXT,
        source TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        health24_id INTEGER NOT NULL,
        document_type TEXT,
        number TEXT,
        issued_at TEXT,
        expiration_date TEXT,
        issued_by TEXT,
        is_active INTEGER DEFAULT 1,
        valid_from TEXT DEFAULT CURRENT_TIMESTAMP,
        valid_to TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document_types (
        id INTEGER PRIMARY KEY,
        code TEXT NOT NULL,
        title TEXT NOT NULL
    )
    """)
     
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_medical_attributes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        health24_id INTEGER NOT NULL,
        attribute_code TEXT NOT NULL,
        value_text TEXT,
        value_number REAL,
        value_bool INTEGER,
        is_active INTEGER DEFAULT 1,
        valid_from TEXT DEFAULT CURRENT_TIMESTAMP,
        valid_to TEXT,
        source TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_declarations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        health24_id INTEGER NOT NULL,
        declaration_id INTEGER NOT NULL,
        employee_id INTEGER,
        employee_name TEXT,
        division_id INTEGER,
        division_name TEXT,
        start_date TEXT,
        end_date TEXT,
        number TEXT,
        is_active INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS address_types (
        id INTEGER PRIMARY KEY,
        code TEXT,
        title TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY,
        code TEXT,
        title TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regions (
        id INTEGER PRIMARY KEY,
        api_id TEXT,
        koatuu TEXT,
        title TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS districts (
        id INTEGER PRIMARY KEY,
        api_id TEXT,
        koatuu TEXT,
        title TEXT,
        region_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settlement_types (
        id INTEGER PRIMARY KEY,
        code TEXT,
        title TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settlements (
        id INTEGER PRIMARY KEY,
        api_id TEXT,
        koatuu TEXT,
        title TEXT,
        region_id INTEGER,
        district_id INTEGER,
        settlement_type_id INTEGER,
        parent_settlement_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS city_districts (
        id INTEGER PRIMARY KEY,
        koatuu TEXT,
        title TEXT,
        settlement_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS street_types (
        id INTEGER PRIMARY KEY,
        code TEXT,
        title TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        health24_id INTEGER,
        address_type_id INTEGER,
        country_id INTEGER,
        region_id INTEGER,
        district_id INTEGER,
        settlement_id INTEGER,
        city_district_id INTEGER,
        street_type_id INTEGER,
        street TEXT,
        building TEXT,
        apartment TEXT,
        zip TEXT,
        is_active BOOLEAN,
        valid_from DATETIME,
        valid_to DATETIME
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_last_name ON patients(last_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_employee_id ON patients(employee_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_json_health24 ON patient_json(health24_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_phones_health24 ON patient_phones(health24_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_documents_health24 ON patient_documents(health24_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_med_attr_health24 ON patient_medical_attributes(health24_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_declarations_health24 ON patient_declarations(health24_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_addresses_health24_id ON patient_addresses (health24_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_settlements_region_id ON settlements (region_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_city_districts_settlement_id ON city_districts (settlement_id)")

    conn.commit()
    return conn
