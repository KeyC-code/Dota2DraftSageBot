import sqlite3
from datetime import datetime

DB_NAME = "app/database/dota_copilot.db"


def initialise() -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            free_requests INTEGER DEFAULT 3,
            subscribed BOOLEAN DEFAULT FALSE,
            subscription_end DATETIME,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            name TEXT DEFAULT 'unknown_user'
        )
    """
    )
    conn.commit()


def get_stats() -> tuple:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_users,
                SUM(subscribed) as premium_users,
                AVG(free_requests) as avg_requests
            FROM users
        """
        )
    return cursor.fetchone()


def get_user(user_id: int) -> tuple:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.commit()
    return user


def create_user(user_id: int, user_name: str) -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, name) VALUES (?, ?)", (user_id, user_name)
        )
        conn.commit()


def use_free_request(user_id: int) -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET free_requests = free_requests - 1 WHERE user_id = ?",
            (user_id,),
        )
        conn.commit()


def activate_subscription(user_id: int, end_date: datetime):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users SET 
                subscribed = TRUE,
                subscription_end = ?
            WHERE user_id = ?
        """,
            (end_date, user_id),
        )
        conn.commit()
