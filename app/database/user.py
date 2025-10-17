# app/database/user.py
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_NAME = "app/database/dota_copilot.db"


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()


def initialise() -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                free_requests INTEGER DEFAULT 3,
                subscribed BOOLEAN DEFAULT FALSE,
                subscription_end DATETIME,
                registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                name TEXT DEFAULT 'unknown_user'
            )
        """)
        conn.commit()


def get_user(user_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()


def create_user(user_id: int, user_name: str) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, name) VALUES (?, ?)", (user_id, user_name)
        )
        conn.commit()


def use_free_request(user_id: int) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET free_requests = free_requests - 1 WHERE user_id = ?",
            (user_id,),
        )
        conn.commit()


def activate_subscription(user_id: int, end_date: datetime):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Сохраняем БЕЗ микросекунд → избегаем проблем с типами
        end_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            UPDATE users SET 
                subscribed = TRUE,
                subscription_end = ?
            WHERE user_id = ?
        """,
            (end_str, user_id),
        )
        conn.commit()


def get_stats():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                SUM(subscribed) as premium_users,
                AVG(free_requests) as avg_requests
            FROM users
        """)
        return cursor.fetchone()
