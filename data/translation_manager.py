import logging
import sqlalchemy

from data.db_manager import get_db


class TranslationManager:
    SAVE_TRANSLATION_QUERY = sqlalchemy.text(
        "INSERT INTO translation (user_id, word, translation, source_lang, translation_lang) "
        "VALUES (:user_id, :word, :translation, :source_lang, :translation_lang)"
    )

    GET_USER_TRANSLATIONS_QUERY = sqlalchemy.text(
        "SELECT word, translation from account "
        "WHERE user_id = :user_id"
    )

    _logger = logging.getLogger(__name__)

    _source_lang = 'en'
    _translation_lang = 'ru'

    _translation_db = get_db('translation')

    @classmethod
    def get_user_translations(cls, user_id):
        cls._logger.debug("get: user_id = %s", user_id)

        translation_lists = {}

        with cls._translation_db.connect() as conn:
            recent_translations = conn.execute(
                cls.GET_USER_TRANSLATIONS_QUERY,
                user_id=user_id
            ).fetchall()

            for row in recent_translations:
                word = row[0]
                translation = row[1]
                if word not in translation_lists:
                    translation_lists[word] = []
                translation_lists[word].append(translation)

        return translation_lists

    @classmethod
    def save_translation(cls, user_id, word, translation):
        cls._logger.debug("save: user_id = %d, word = %s, translation = %s", user_id, word, translation)

        try:
            with cls._translation_db.connect() as conn:
                conn.execute(
                    cls.SAVE_TRANSLATION_QUERY,
                    user_id=user_id,
                    word=word,
                    translation=translation,
                    source_lang=cls._source_lang,
                    translation_lang=cls._translation_lang
                )

        except Exception as e:
            cls._logger.exception(e)
            return False

        return True
