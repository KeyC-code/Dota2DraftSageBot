from datetime import datetime, timedelta

from app.database import user as db_user
from app.sub_manager import SubscriptionManager, User


def test_get_user_creates_new(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()

    user_obj = SubscriptionManager.get_user(666, "NewUser")
    assert isinstance(user_obj, User)
    assert user_obj.id == 666
    assert user_obj.free_requests == 3
    assert user_obj.subscribed is False


def test_check_access_free(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()
    SubscriptionManager.get_user(777, "FreeUser")

    assert SubscriptionManager.check_access(777, "FreeUser") is True


def test_check_access_no_free_no_sub(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()
    user_id = 888
    SubscriptionManager.get_user(user_id, "NoAccess")

    for _ in range(3):
        SubscriptionManager.use_free_request(user_id)

    assert SubscriptionManager.check_access(user_id, "NoAccess") is False


def test_check_access_with_active_sub(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()
    user_id = 999
    SubscriptionManager.get_user(user_id, "SubUser")

    SubscriptionManager.activate_subscription(user_id, 1)
    assert SubscriptionManager.check_access(user_id, "SubUser") is True


def test_use_free_request_decrements(temp_db):
    db_user.DB_NAME = temp_db
    db_user.initialise()
    user_id = 1000
    SubscriptionManager.get_user(user_id, "Tester")

    initial = SubscriptionManager.get_user(user_id, "Tester").free_requests
    SubscriptionManager.use_free_request(user_id)
    after = SubscriptionManager.get_user(user_id, "Tester").free_requests

    assert after == initial - 1
