#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @LangGodBot
# Simple bot for new languages learning.

import os
import telegram
import logging

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from telegram.utils.request import Request

from bot.commands import (commands, handlers)
from bot.state import QuizState

logging.basicConfig(format='[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logger = logging.getLogger()
bot_instance = None


def create_bot():
    request = Request(proxy_url=os.environ["PROXY_SERVER"])

    return telegram.Bot(token=os.environ["TELEGRAM_TOKEN"], request=request)


def main():
    global bot_instance
    bot_instance = create_bot()

    additional_arguments = {}
    if "PROXY_SERVER" in os.environ:
        additional_arguments['proxy_url'] = os.environ["PROXY_SERVER"]

    updater = Updater(os.environ["TELEGRAM_TOKEN"], use_context=True, request_kwargs=additional_arguments)
    dispatcher = updater.dispatcher

    quiz_handler = ConversationHandler(
        entry_points=[commands.start_quiz.handler],

        states={
            QuizState.NEXT_QUESTION: [CallbackQueryHandler(handlers.next_question)],

            QuizState.SELECTING_ANSWER: [CallbackQueryHandler(handlers.select_option)],

            QuizState.BETWEEN_QUESTIONS: [CallbackQueryHandler(handlers.continue_quiz)],

            QuizState.END: [CallbackQueryHandler(handlers.end_quiz)]
        },

        fallbacks=[commands.end_quiz.handler]
    )

    dispatcher.add_handler(quiz_handler)

    for command in commands.command_registry.values():
        dispatcher.add_handler(command.handler)

    dispatcher.add_error_handler(handlers.error)

    updater.start_polling()

    logger.info("Bot started!")

    updater.idle()


if __name__ == '__main__':
    main()
