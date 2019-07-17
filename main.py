#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @LangGodBot
# Simple bot for new languages learning.

import os
import telegram
import logging

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from telegram.utils.request import Request

import translation_manager


PROXY_URL = os.environ["PROXY_SERVER"]

logging.basicConfig(format='[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
logger = logging.getLogger()
bot_instance = None


def create_bot():
    request = Request(proxy_url=os.environ["PROXY_SERVER"])

    return telegram.Bot(token=os.environ["TELEGRAM_TOKEN"], request=request)


SELECTING_ANSWER, BEFORE_NEXT_QUESTION, QUIZ_END = range(3)


def start(update, context):
    logger.info("Start!")

    context.chat_data['id'] = update.message.chat.id
    context.user_data['username'] = update.message.from_user.username

    update.message.reply_text('Welcome, {}!'.format(context.user_data['username']))


def process_new_translations(user_id, translation_request):
    word, translations_str = translation_request.split(' - ')
    translations = translations_str.split(',')
    new_translations = 0

    for translation in translations:
        if translation_manager.save_translation(user_id, word, translation):
            new_translations += 1

    return new_translations


def add_translations(update, context):
    logger.info("Add translations!")

    new_entries_count = process_new_translations(update.message.from_user.id, update.message.text)

    update.message.reply_text("{} new translations were added!".format(new_entries_count))


def process_show_translations(user_id):
    user_translations = translation_manager.get_user_translations(user_id)

    return '\n'.join(word + ', '.join(trans) for word, trans in user_translations.items())


def show_translations(update, context):
    logger.info("Show translations!")

    update.message.reply_text(process_show_translations(update.message.from_user.id))


def start_quiz(update, context):
    logger.info("Quiz start!")

    update.message.reply_text('Let\'s have fun, {}!'.format(update.message.from_user.username))

    return next_question(update, context)


def next_question(update, context):
    logger.info("Next question!")

    button_list = [[
        InlineKeyboardButton("First", callback_data='1'),
        InlineKeyboardButton("Second", callback_data='2'),
        InlineKeyboardButton("Third", callback_data='3'),
        InlineKeyboardButton("Fourth", callback_data='4')
    ]]

    update.message.reply_text("Choose translation that fits best:", reply_markup=InlineKeyboardMarkup(button_list))

    return SELECTING_ANSWER


def select_option(update, context):
    query = update.callback_query

    logger.info("Option %s was chosen!", query.data)

    query.edit_message_text(text="Selected option: {}".format(query.data))

    button_list = [[
        InlineKeyboardButton("Next", callback_data='next'),
        InlineKeyboardButton("End", callback_data='end'),
    ]]
    markup = InlineKeyboardMarkup(button_list, one_time_keyboard=True)

    context.bot.send_message(
        chat_id=context.chat_data['id'],
        text='Continue?',
        reply_markup=markup
    )

    return BEFORE_NEXT_QUESTION


def end_quiz(update, context):
    logger.info("Quiz end!")

    update.message.reply_text('WTF, {}!?'.format(update.message.from_user.username))


def log_error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    global bot_instance
    bot_instance = create_bot()

    additional_arguments = {}
    if "PROXY_SERVER" in os.environ:
        additional_arguments['proxy_url'] = os.environ["PROXY_SERVER"]

    updater = Updater(os.environ["TELEGRAM_TOKEN"], use_context=True, request_kwargs=additional_arguments)
    dispatcher = updater.dispatcher

    quiz_handler = ConversationHandler(
        entry_points=[CommandHandler('quiz', start_quiz)],

        states={
            BEFORE_NEXT_QUESTION: [MessageHandler(Filters.regex('^Next$'), next_question),
                                   MessageHandler(Filters.regex('^End$'), end_quiz)],

            SELECTING_ANSWER: [CallbackQueryHandler(select_option)]
        },

        fallbacks=[CommandHandler('end', end_quiz)]
    )

    dispatcher.add_handler(quiz_handler)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('add', add_translations))
    dispatcher.add_handler(CommandHandler('show', show_translations))

    dispatcher.add_error_handler(log_error)

    updater.start_polling()

    logger.info("Bot started!")

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
