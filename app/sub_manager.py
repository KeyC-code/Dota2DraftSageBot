from datetime import datetime

from dateutil.relativedelta import relativedelta

import app.database.user as DB_user


class User:
    def __init__(self, user_from_db: tuple):
        self.id = user_from_db[0]
        self.name = user_from_db[5]
        self.free_requests = user_from_db[1]
        self.subscribed = bool(user_from_db[2])

        sub_end_str = user_from_db[3]
        if sub_end_str and sub_end_str != "1970-01-01 00:00:00":
            try:
                self.subscription = datetime.strptime(sub_end_str, "%Y-%m-%d %H:%M:%S")
            except:
                self.subscription = datetime(1970, 1, 1)
        else:
            self.subscription = datetime(1970, 1, 1)

        self.registeration_date = user_from_db[4]


class SubscriptionManager:
    @staticmethod
    def get_user(user_id: int, user_name: str) -> User:
        db_user = DB_user.get_user(user_id)
        if not db_user:
            DB_user.create_user(user_id, user_name)
            return User(
                (
                    user_id,
                    3,
                    False,
                    datetime(1970, 1, 1),
                    datetime.now(),
                    user_name,
                ),
            )
        result_user = User(db_user)
        return result_user

    @staticmethod
    def check_access(user_id: int, user_name: str) -> bool:
        user = SubscriptionManager.get_user(user_id, user_name)
        if user.subscribed and user.subscription > datetime.now():
            return True
        return user.free_requests > 0

    @staticmethod
    def use_free_request(user_id: int) -> None:
        DB_user.use_free_request(user_id)
        user = DB_user.get_user(user_id)
        print(
            f" ==> \033[38;2;2;43;58m[user]\033[0m({type(user).__name__}) = \033[38;2;0;53;120m{user}\033[0m"
        )

    @staticmethod
    def activate_subscription(user_id: int, duration: int) -> None:
        end_date = datetime.now() + relativedelta(months=duration)
        DB_user.activate_subscription(user_id, end_date)
