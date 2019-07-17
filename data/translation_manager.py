import logging
import sqlalchemy

from data import db_manager

logger = logging.getLogger()

source_lang = 'en'
translation_lang = 'ru'

account_db = db_manager.get_db('translation')

SAVE_QUERY = sqlalchemy.text(
    "INSERT INTO translation (user_id, word, translation, source_lang, translation_lang) "
    "VALUES (:user_id, :word, :translation, :source_lang, :translation_lang)"
)

GET_QUERY = sqlalchemy.text(
    "SELECT word, translation from account "
    "WHERE user_id = :user_id"
)


def get_user_translations(user_id):
    translation_lists = {}

    with account_db.connect() as conn:
        recent_translations = conn.execute(
            GET_QUERY,
            user_id=user_id
        ).fetchall()

        for row in recent_translations:
            word = row[0]
            translation = row[1]
            if word not in translation_lists:
                translation_lists[word] = []
            translation_lists[word].append(translation)

    return translation_lists


def save_translation(user_id, word, translation):
    try:
        with account_db.connect() as conn:
            conn.execute(
                SAVE_QUERY,
                user_id=user_id,
                word=word,
                translation=translation,
                source_lang=source_lang,
                translation_lang=translation_lang
            )

    except Exception as e:
        logger.exception(e)
        return False

    return True
