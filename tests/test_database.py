import sqlite3
from datetime import datetime, timedelta

from app.database import user as db_user


def test_initialise_creates_table(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
        )
        assert cursor.fetchone() is not None


def test_create_and_get_user(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()

    user_id, name = 111, "Alice"
    db_user.create_user(user_id, name)
    user = db_user.get_user(user_id)

    assert user is not None
    assert user[0] == user_id
    assert user[5] == name
    assert user[1] == 3
    assert user[2] == 0


def test_use_free_request(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()
    db_user.create_user(222, "Bob")

    db_user.use_free_request(222)
    user = db_user.get_user(222)
    assert user[1] == 2


def test_activate_subscription(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()
    db_user.create_user(333, "Charlie")

    end_date = datetime.now() + timedelta(days=30)
    db_user.activate_subscription(333, end_date)

    user = db_user.get_user(333)
    stored_date = datetime.strptime(user[3], "%Y-%m-%d %H:%M:%S")

    assert abs((stored_date - end_date).total_seconds()) < 1


def test_get_stats(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()
    db_user.create_user(444, "User1")
    db_user.create_user(555, "User2")
    db_user.use_free_request(444)
    db_user.use_free_request(444)

    stats = db_user.get_stats()
    assert stats[0] == 2
    assert stats[1] == 0
    assert 1.5 <= stats[2] <= 2.0
