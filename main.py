#!/usr/bin/env python

from json import loads
from flask import (Flask, request)
from telegram import Update

from bot.langgodbot import LangGodBot
from bot.settings import Settings
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

    if LangGodBot.webhook_set():
        return "Webhook is already set (:"

    if not LangGodBot.initialized():
        if not LangGodBot.initialize():
            return "Failed to initialize LangGotBot :("

    if LangGodBot.set_webhook(Settings.WEBHOOK_URL):
        return "Webhook set! :)"
    else:
        return "Webhook setup failed :("


@app.route('/' + Settings.TELEGRAM_TOKEN, methods=['GET', 'POST'])
def handler():
    logger.info("tg command, data = '%s'", request.data)

    if not LangGodBot.initialized():
        return "LangGodBot isn't initialized"

    body = loads(request.data)
    update = Update.de_json(body, LangGodBot.bot)
    LangGodBot.dispatcher.process_update(update)

    return "command is handled"


@app.route('/<string>')
def echo(string):
    logger.info("got string '%s'", string)

    return string


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
