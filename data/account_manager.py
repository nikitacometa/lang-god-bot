import logging
import sqlalchemy

from data import db_manager

logger = logging.getLogger()

account_db = db_manager.get_db('account')

SAVE_QUERY = sqlalchemy.text(
                "INSERT INTO account (user_id, username) "
                "VALUES (:user_id, :username)"
             )


def save_account(user_id, username):
    try:
        with account_db.connect() as conn:
            conn.execute(
                SAVE_QUERY,
                user_id=user_id,
                username=username
            )

    except Exception as e:
        logger.exception(e)
        return False

    return True
