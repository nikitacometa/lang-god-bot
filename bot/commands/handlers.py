import logging

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)

from data import translation_manager
from bot.state import QuizState


# TODO: make class Handlers

logger = logging.getLogger()


def start(update, context):
    logger.info("Start!")

    context.chat_data['id'] = update.message.chat.id
    context.user_data['username'] = update.message.from_user.username

    update.message.reply_text("Welcome, {}!".format(context.user_data['username']))


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

    update.message.reply_text("Let\'s have fun, {}!".format(update.message.from_user.username))

    context.chat_data['questions_count'] = 0

    return next_question(update, context)


def next_question(update, context):
    logger.info("Next question!")

    button_list = [[
        InlineKeyboardButton("First", callback_data='1'),
        InlineKeyboardButton("Second", callback_data='2'),
        InlineKeyboardButton("Third", callback_data='3'),
        InlineKeyboardButton("Fourth", callback_data='4')
    ]]

    context.bot.send_message(
        chat_id=context.chat_data['id'],
        text="Choose translation that fits best:",
        reply_markup=InlineKeyboardMarkup(button_list)
    )

    return QuizState.SELECTING_ANSWER


def select_option(update, context):
    query = update.callback_query

    logger.info("Option %s was chosen!", query.data)

    query.edit_message_text(text="Selected option: {}".format(query.data))

    context.chat_data['questions_count'] += 1

    button_list = [[
        InlineKeyboardButton("Next", callback_data='next'),
        InlineKeyboardButton("End", callback_data='end'),
    ]]

    context.bot.send_message(
        chat_id=context.chat_data['id'],
        text="Continue?",
        reply_markup=InlineKeyboardMarkup(button_list)
    )

    return QuizState.BETWEEN_QUESTIONS


def continue_quiz(update, context):
    logger.info("Quiz continue!")

    act = update.callback_query.data

    if update.callback_query is not None:
        update.callback_query.message.delete()

    if act == 'next':
        return next_question(update, context)
    elif act == 'end':
        return end_quiz(update, context)
    else:
        logger.error("Quiz continuation callback returned invalid response '%s'.", act)


def end_quiz(update, context):
    logger.info("Quiz end!")

    context.bot.send_message(
        chat_id=context.chat_data['id'],
        text="Well done, {}! {} questions!".format(
            context.user_data['username'],
            context.chat_data['questions_count']
        )
    )

    del context.chat_data['questions_count']

    return QuizState.SELECTING_ANSWER


def error(update, context):
    logger.warning("Update '%s' caused error '%s'", update, context.error)
