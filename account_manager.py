import logging
import os
import sqlalchemy


logger = logging.getLogger()

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

source_lang = 'en'
translation_lang = 'ru'

account_db = sqlalchemy.create_engine(
    sqlalchemy.engine.url.URL(
        drivername='postgres+pg8000',
        username=db_user,
        password=db_pass,
        database='account',
        query={
            'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(
                cloud_sql_connection_name)
        }
    ),
    # Pool size is the maximum number of permanent connections to keep.
    pool_size=5,
    # Temporarily exceeds the set pool_size if no connections are available.
    max_overflow=2,
    # The total number of concurrent connections for the application will be
    # a total of pool_size and max_overflow.

    # The maximum number of seconds to wait when retrieving a
    # new connection from the pool. After the specified amount of time, an
    # exception will be thrown.
    pool_timeout=30,  # 30 seconds

    # The maximum number of seconds a connection can persist.
    # Connections that live longer than the specified amount of time will be
    # reestablished
    pool_recycle=1800,  # 30 minutes
)


def get_user_translations(user_id):
    translation_lists = {}
    with account_db.connect() as conn:
        # Execute the query and fetch all results
        recent_translations = conn.execute(
            "SELECT word, translation from account "
            "WHERE user_id = :user_id",
            user_id=user_id
        ).fetchall()
        # Convert the results into a list of dicts representing votes
        for row in recent_translations:
            word = row[0]
            translation = row[1]
            if word not in translation_lists:
                translation_lists[word] = []
            translation_lists[word].append(translation)

    return translation_lists


def save_translation(user_id, word, translation):
    # Preparing a statement before hand can help protect against injections.
    stmt = sqlalchemy.text(
        "INSERT INTO translation (user_id, word, translation, source_lang, translation_lang)"
        " VALUES (:user_id, :word, :translation, :source_lang, :translation_lang)"
    )
    try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with account_db.connect() as conn:
            conn.execute(
                stmt,
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
