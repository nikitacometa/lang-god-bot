import logging

from os import environ
from environment import Environment


Environment.fetch_variables()


class Settings:
    TELEGRAM_TOKEN = environ.get('TELEGRAM_TOKEN')

    PROXY_SERVER_URL = environ.get('PROXY_SERVER')
    APPLICATION_URL = environ.get('APPLICATION_URL')

    DB_USER = environ.get('DB_USER')
    DB_PASS = environ.get('DB_PASS')

    CLOUD_SQL_CONNECTION_NAME = environ.get('CLOUD_SQL_CONNECTION_NAME')

    WEBHOOK_URL = "{}/{}".format(APPLICATION_URL, TELEGRAM_TOKEN)

    LOG_FORMAT = "[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s"


logging.basicConfig(format=Settings.LOG_FORMAT, level=logging.INFO)
