# repositories/patient_repository.py

import sqlite3
from sqlite3 import Error
from typing import Optional, List, Tuple, Any

from lib.logger import setup_logger

logger = setup_logger("patient_repository")


# ===============================
# КАСТОМНА ФУНКЦІЯ ДЛЯ КИРИЛИЦІ
# ===============================

def setup_case_insensitive_like(conn: sqlite3.Connection) -> None:
    """Налаштовує регістронезалежне порівняння для кирилиці"""
    def upper_cyrillic(text):
        if text is None:
            return None
        return text.upper()
    
    conn.create_function("UPPER_CYR", 1, upper_cyrillic)
    logger.debug("Функція UPPER_CYR зареєстрована")


# ===============================
# СТВОРЕННЯ ТРАНЗАКЦІЇ
# ===============================

def create_patient_table(conn: sqlite3.Connection) -> None:
    # Реєструємо функцію для кирилиці
    setup_case_insensitive_like(conn)
    
    sql = """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            health24_id INTEGER UNIQUE NOT NULL,
            api_id TEXT UNIQUE NOT NULL,
            personality_id TEXT UNIQUE NOT NULL,
            employee_id INTEGER,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            second_name TEXT,
            birth_date TEXT,      -- YYYY-MM-DD
            gender TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    try:
        conn.execute(sql)
        conn.commit()
        logger.info("Таблиця patients перевірена / створена")
    except sqlite3.Error as e:
        logger.error("Помилка створення таблиці patients: %s", e)
        raise RuntimeError(e)


def create_patient_indexes(conn: sqlite3.Connection) -> None:
    try:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_patients_last_name "
            "ON patients (last_name COLLATE NOCASE)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_patients_first_name "
            "ON patients (first_name COLLATE NOCASE)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_patients_second_name "
            "ON patients (second_name COLLATE NOCASE)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_patients_employee_id "
            "ON patients (employee_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_patients_birth_date "
            "ON patients (birth_date)"
        )
        conn.commit()
        logger.info("Індекси patients створені / перевірені")
    except sqlite3.Error as e:
        logger.error("Помилка створення індексів patients: %s", e)
        raise RuntimeError(e)


# ===============================
# UPSERT
# ===============================

def upsert_patient_data(
    conn: sqlite3.Connection,
    patient_data: Tuple[Any, ...]
) -> None:
    sql = """
        INSERT INTO patients (
            health24_id,
            api_id,
            personality_id,
            employee_id,
            last_name,
            first_name,
            second_name,
            birth_date,
            gender
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(health24_id) DO UPDATE SET
            api_id = excluded.api_id,
            personality_id = excluded.personality_id,
            employee_id = excluded.employee_id,
            last_name = excluded.last_name,
            first_name = excluded.first_name,
            second_name = excluded.second_name,
            birth_date = excluded.birth_date,
            gender = excluded.gender,
            updated_at = CURRENT_TIMESTAMP
    """
    try:
        conn.execute(sql, patient_data)
        conn.commit()
    except Error as e:
        conn.rollback()
        logger.error(
            "Помилка upsert пацієнта health24_id=%s: %s",
            patient_data[0],
            e,
        )
        raise


# ===============================
# ОТРИМАННЯ 1 ПАЦІЄНТА
# ===============================

def get_patient_by_health24_id(
    conn: sqlite3.Connection,
    health24_id: int
) -> Optional[dict]:
    conn.row_factory = sqlite3.Row

    sql = """
        SELECT
            health24_id,
            employee_id,
            last_name,
            first_name,
            second_name,
            birth_date,
            gender
        FROM patients
        WHERE health24_id = ?
    """

    cur = conn.cursor()
    cur.execute(sql, (health24_id,))
    row = cur.fetchone()

    if not row:
        logger.warning(
            "Пацієнт з health24_id=%s не знайдений",
            health24_id,
        )
        return None

    logger.debug(
        "Отримано пацієнта health24_id=%s",
        health24_id,
    )

    return dict(row)


# ===============================
# ПОШУК + ФІЛЬТРИ + СОРТУВАННЯ
# ===============================

def search_patients(
    conn: sqlite3.Connection,
    last_name: str = "",
    first_name: str = "",
    second_name: str = "",
    employee_id: Optional[int] = None,
    order_by: str = "last_name",
    direction: str = "ASC",
) -> List[dict]:
    
    # Переконуємося що функція зареєстрована
    setup_case_insensitive_like(conn)
    
    conn.row_factory = sqlite3.Row

    allowed_order_fields = {
        "health24_id": "health24_id",
        "last_name": "last_name COLLATE NOCASE",
        "first_name": "first_name COLLATE NOCASE",
        "second_name": "second_name COLLATE NOCASE",
        "birth_date": "DATE(birth_date)",
        "gender": "gender",
    }

    order_sql = allowed_order_fields.get(
        order_by,
        "last_name COLLATE NOCASE"
    )

    direction_sql = "DESC" if direction.upper() == "DESC" else "ASC"

    sql = """
        SELECT
            health24_id,
            employee_id,
            last_name,
            first_name,
            second_name,
            birth_date,
            gender
        FROM patients
        WHERE 1 = 1
    """

    params: list[Any] = []

    # Використовуємо UPPER_CYR для регістронезалежного пошуку
    if last_name:
        sql += " AND UPPER_CYR(last_name) LIKE UPPER_CYR(?)"
        params.append(f"{last_name}%")

    if first_name:
        sql += " AND UPPER_CYR(first_name) LIKE UPPER_CYR(?)"
        params.append(f"{first_name}%")

    if second_name:
        sql += " AND UPPER_CYR(second_name) LIKE UPPER_CYR(?)"
        params.append(f"{second_name}%")

    if employee_id is not None:
        sql += " AND employee_id = ?"
        params.append(employee_id)

    sql += f" ORDER BY {order_sql} {direction_sql}"

    logger.debug(
        "search_patients SQL=%s | params=%s",
        sql.replace("\n", " "),
        params,
    )

    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()

    logger.info("search_patients: знайдено %s записів", len(rows))

    return [dict(row) for row in rows]