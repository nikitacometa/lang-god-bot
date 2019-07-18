#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @LangGodBot
# Simple bot for new languages learning.

import telegram
import logging

from telegram.ext import (Dispatcher, ConversationHandler, CallbackQueryHandler)
from telegram.utils.request import Request

from bot.commands.commands import Commands
from bot.commands.handlers import Handlers

from bot.state import QuizState
from bot.settings import Settings


class LangGodBot:
    bot = None
    dispatcher = None

    _logger = logging.getLogger(__name__)

    @classmethod
    def initialized(cls):
        return cls.bot is not None and cls.dispatcher is not None

    @classmethod
    def initialize(cls):
        if cls.bot is None:
            cls.bot = cls._create_bot()
        if cls.dispatcher is None:
            cls.dispatcher = cls._create_dispatcher(cls.bot)
        return cls.initialized()

    @classmethod
    def set_webhook(cls, url):
        return cls.bot.setWebhook(url)

    @classmethod
    def webhook_set(cls):
        webhook_info = cls.bot.get_webhook_info()
        return webhook_info.url.strip() != ''

    @classmethod
    def _create_bot(cls):
        request = Request(proxy_url=Settings.PROXY_SERVER_URL)

        return telegram.Bot(token=Settings.TELEGRAM_TOKEN, request=request)

    @classmethod
    def _create_dispatcher(cls, bot):
        dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

        quiz_handler = ConversationHandler(
            entry_points=[Commands.start_quiz.handler],

            states={
                QuizState.NEXT_QUESTION: [CallbackQueryHandler(Handlers.next_question)],

                QuizState.SELECTING_ANSWER: [CallbackQueryHandler(Handlers.select_option)],

                QuizState.BETWEEN_QUESTIONS: [CallbackQueryHandler(Handlers.continue_quiz)],

                QuizState.END: [CallbackQueryHandler(Handlers.end_quiz)]
            },

            fallbacks=[Commands.end_quiz.handler]
        )

        dispatcher.add_handler(quiz_handler)

        for command in dir(Commands):
            cls._logger.info("Command '%s' registered!", command.name)

            dispatcher.add_handler(command.handler)

        dispatcher.add_error_handler(Handlers.error)

        return dispatcher
