import logging

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)

from data.data_processing import DataProcessing
from bot.state import QuizState


class Handlers:
    _logger = logging.getLogger(__name__)

    @classmethod
    def start(cls, update, context):
        cls._logger.info("Start!")

        context.chat_data['id'] = update.message.chat.id
        context.user_data['username'] = update.message.from_user.username

        update.message.reply_text("Welcome, {}!".format(context.user_data['username']))

    @classmethod
    def add_translations(cls, update, context):
        cls._logger.info("Add translations!")

        translation_string = " ".join(context.args)
        cls._logger.info("Translations = '%s'", translation_string)

        new_entries_count = DataProcessing.process_new_translations(update.message.from_user.id, translation_string)

        update.message.reply_text("{} new translations were added!".format(new_entries_count))

    @classmethod
    def show_translations(cls, update, context):
        cls._logger.info("Show translations!")

        update.message.reply_text(process_show_translations(update.message.from_user.id))

    @classmethod
    def start_quiz(cls, update, context):
        cls._logger.info("Quiz start!")

        update.message.reply_text("Let\'s have fun, {}!".format(update.message.from_user.username))

        context.chat_data['questions_count'] = 0

        return cls.next_question(update, context)

    @classmethod
    def next_question(cls, update, context):
        cls._logger.info("Next question!")

        button_list = [[
            InlineKeyboardButton("Pidor", callback_data='1'),
            InlineKeyboardButton("Master", callback_data='2'),
            InlineKeyboardButton("Kardi-gun))", callback_data='3'),
            InlineKeyboardButton("Mirz", callback_data='4')
        ]]

        context.bot.send_message(
            chat_id=context.chat_data['id'],
            text="Choose translation that fits best:",
            reply_markup=InlineKeyboardMarkup(button_list)
        )

        return QuizState.SELECTING_ANSWER

    @classmethod
    def select_option(cls, update, context):
        query = update.callback_query

        cls._logger.info("Option %s was chosen!", query.data)

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

    @classmethod
    def continue_quiz(cls, update, context):
        cls._logger.info("Quiz continue!")

        act = update.callback_query.data

        if update.callback_query is not None:
            update.callback_query.message.delete()

        if act == 'next':
            return cls.next_question(update, context)
        elif act == 'end':
            return cls.end_quiz(update, context)
        else:
            cls._logger.error("Quiz continuation callback returned invalid response '%s'.", act)

    @classmethod
    def end_quiz(cls, update, context):
        cls._logger.info("Quiz end!")

        context.bot.send_message(
            chat_id=context.chat_data['id'],
            text="Well done, {}! {} questions!".format(
                context.user_data['username'],
                context.chat_data['questions_count']
            )
        )

        del context.chat_data['questions_count']

        return QuizState.SELECTING_ANSWER

    @classmethod
    def error(cls, update, context):
        cls._logger.warning("Update '%s' caused error '%s'", update, context.error)
