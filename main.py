#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @LangGodBot
# Simple bot for new languages learning.

import os
import telegram
import logging

import account_manager

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)
from telegram.utils.request import Request


PROXY_URL = os.environ["PROXY_SERVER"]

logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s-%(message)s', level=logging.INFO)
logger = logging.getLogger()
bot = None


def create_bot():
    request = Request(proxy_url=os.environ["PROXY_SERVER"])

    return telegram.Bot(token=os.environ["TELEGRAM_TOKEN"], request=request)


SELECTING_ANSWER, BEFORE_NEXT_QUESTION, QUIZ_END, IDLE = range(4)


def start(update, context):
    update.message.reply_text('Welcome, {}!'.format(update.message.from_user.username))


def process_new_translations(user_id, translation_request):
    word, translations_str = translation_request.split(' - ')
    translations = translations_str.split(',')
    new_translations = 0

    for translation in translations:
        if account_manager.save_translation(user_id, word, translation):
            new_translations += 1

    return new_translations


def add_translations(update, context):
    new_entries_count = process_new_translations(update.message.from_user.id, update.message.text)

    update.message.reply_text("{} new translations were added!", new_entries_count)

    return IDLE


def process_show_translations(user_id):
    user_translations = account_manager.get_user_translations(user_id)

    return '\n'.join(word + ', '.join(trans) for word, trans in user_translations.items())


def show_translations(update, context):
    update.message.reply_text(process_show_translations(update.message.from_user.id))

    return IDLE


def start_quiz(update, context):
    update.message.reply_text('Let\'s have fun, {}!'.format(update.message.from_user.username))

    return next_question(update, context)


def next_question(update, context):
    button_list = [
        [InlineKeyboardButton("First", callback_data=1),
         InlineKeyboardButton("Second", callback_data=2),
         InlineKeyboardButton("Third", callback_data=3),
         InlineKeyboardButton("Fourth", callback_data=4)]
        ]

    update.message.reply_text("Choose translation that fits the best:", reply_markup=InlineKeyboardMarkup(button_list))

    return SELECTING_ANSWER


def select_option(update, option_number):
    update.message.reply_text("You've chosen the option #{}!", option_number)

    return BEFORE_NEXT_QUESTION


def end_quiz(update, context):
    update.message.reply_text('WTF, {}!?'.format(update.message.from_user.username))


def cancel(update, context):
    # TODO: cancel something here
    update.message.reply_text('All cancelled!')


def log_error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    global bot
    bot = create_bot()

    additional_arguments = {
        'proxy_url': os.environ["PROXY_SERVER"]
    }

    updater = Updater(os.environ["TELEGRAM_TOKEN"], request_kwargs=additional_arguments)
    dp = updater.dispatcher

    quiz_handler = ConversationHandler(
        entry_points=[CommandHandler('quiz', start_quiz)],

        states={
            BEFORE_NEXT_QUESTION: [MessageHandler('next', next_question),
                                   CommandHandler('end', end_quiz)],

            SELECTING_ANSWER: [CallbackQueryHandler(select_option, pass_user_data=True)],

            QUIZ_END: [CallbackQueryHandler(end_quiz)]
        },

        fallbacks=[CommandHandler('end', end_quiz)]
    )

    dictionary_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            IDLE: [MessageHandler('add', add_translations),
                   MessageHandler('show', show_translations)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(quiz_handler)
    dp.add_handler(dictionary_handler)
    dp.add_error_handler(log_error)

    # updater.start_polling()

    updater.start_webhook(webhook_url='https://us-central1-langgodbot.cloudfunctions.net/webhook')

    updater.idle()


if __name__ == '__main__':
    main()

# def webhook(new_request):
#     if new_request.method == "POST":
#         update = telegram.Update.de_json(new_request.get_json(force=True), bot)
#         chat_id = update.message.chat.id
#         user_id = update.message.from_user.id
#         request_str = update.message.text
#
#         if request_str.startswith("/add"):
#             asyncio.create_task(process_request())
#             response_str = process_new_translations(user_id, request_str)
#         elif request_str == "/show":
#             response_str = process_show_user_translations(user_id)
#         else:
#             response_str = "you are pidor"
#         bot.sendMessage(chat_id=chat_id, text=response_str)
#
#     return "ok"
