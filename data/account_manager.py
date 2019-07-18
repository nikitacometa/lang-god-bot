import logging
import sqlalchemy

from data.db_manager import get_db


class AccountManager:
    _logger = logging.getLogger(__name__)

    _account_db = get_db('account')

    SAVE_ACCOUNT_QUERY = sqlalchemy.text(
        "INSERT INTO account (user_id, username) "
        "VALUES (:user_id, :username)"
    )

    @classmethod
    def save_account(cls, user_id, username):
        try:
            with cls._account_db.connect() as conn:
                conn.execute(
                    cls.SAVE_ACCOUNT_QUERY,
                    user_id=user_id,
                    username=username
                )

        except Exception as e:
            cls._logger.exception(e)
            return False

        return True
