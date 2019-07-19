import sqlalchemy

from bot.settings import Settings


def get_db(db_name):
    return sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername='postgres+pg8000',
            username=Settings.DB_USER,
            password=Settings.DB_PASS,
            database=db_name,
            query={
                'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(
                    Settings.CLOUD_SQL_CONNECTION_NAME
                )
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
