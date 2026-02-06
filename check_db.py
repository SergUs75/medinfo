# check_db.py
import sys
import os
import sqlite3

# --- Фікс шляху для коректного імпорту ---
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
# ----------------------------------------

# Припускаємо, що db_connector.py знаходиться у repositories/
from repositories.db_connector import create_connection

# Функція підключення, зазвичай, створює med_assist.db у кореневому каталозі
conn = create_connection() 

if conn:
    try:
        # Отримуємо фактичний шлях до файлу бази даних, до якого ми підключилися
        db_path = conn.cursor().connection.execute('PRAGMA database_list').fetchall()[0][2]
        print(f"Підключено до бази даних за шляхом: {db_path}")

        cur = conn.cursor()
        
        # 1. Рахуємо записи
        cur.execute("SELECT COUNT(*) FROM patients")
        count = cur.fetchone()[0]
        print(f"\nКількість записів у таблиці 'patients': {count}")

        # 2. Виводимо перші 5 записів для перевірки
        if count > 0:
            cur.execute("SELECT * FROM patients LIMIT 5")
            first_records = cur.fetchall()
            print("\nПерші 5 записів (id, api_id, personality_id, ...):")
            for record in first_records:
                print(record)
        else:
            print("Таблиця 'patients' П О Р О Ж Н Я. Потрібно повторно запустити patient_api.py.")
            
    except sqlite3.OperationalError as e:
        print(f"\nПомилка SQL: {e}. Ймовірно, таблиця 'patients' не існує.")
    finally:
        conn.close()
else:
    print("Помилка підключення до БД.")