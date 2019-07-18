from telegram.ext import CommandHandler

from bot.commands.handlers import Handlers


class LangCommand:
    def __init__(self, name, description, handler_function, show_in_help=True):
        self.name = name
        self.description = description
        self.handler_function = handler_function
        self.show_in_help = show_in_help

        Commands.register_command(self)

    @property
    def handler(self):
        return CommandHandler(self.name, self.handler_function)


class Commands:
    registry = {}

    start = LangCommand(
        'start',
        'show menu',
        Handlers.start
    )

    add_translations = LangCommand(
        'add',
        'add new translations',
        Handlers.add_translations
    )

    show_translations = LangCommand(
        'show',
        'show translations',
        Handlers.show_translations
    )

    start_quiz = LangCommand(
        'quiz',
        'start new quiz',
        Handlers.start_quiz
    )

    end_quiz = LangCommand(
        'end',
        'end current quiz',
        Handlers.end_quiz
    )

    @classmethod
    def register_command(cls, command):
        cls.registry[command.name] = command
