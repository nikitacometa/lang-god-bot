#!/usr/bin/env python

from json import loads
from flask import (Flask, request)
from telegram import Update

import langgodbot
from settings import Settings
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route('/')
def greet():
    logger.info('index')

    return "hey"


@app.route('/set_webhook')
def setup():
    logger.info('set_webhook')

    bot = langgodbot.create_bot()
    langgodbot.create_dispatcher(bot)

    webhook_set = bot.setWebhook(Settings.WEBHOOK_URL)
    if webhook_set:
        return "Webhook set"
    else:
        return "Webhook setup failed"


@app.route('/' + Settings.TELEGRAM_TOKEN, methods=['GET', 'POST'])
def handler():
    logger.info("tg command, data = '%s'", request.data)
    if langgodbot.dispatcher is None:
        return "webhook wasn't set :("

    body = loads(request.data)
    update = Update.de_json(body, langgodbot.bot_instance)
    langgodbot.dispatcher.process_update(update)

    return "ok"


@app.route('/<string>')
def echo(string):
    logger.info("got string '%s'", string)

    return string


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
