from telegram.ext import CommandHandler

from bot.commands import handlers

# TODO: make class Commands

command_registry = {}


def register_command(command):
    command_registry[command.name] = command


class LangCommand:
    def __init__(self, name, description, handler_function, show_in_help=True):
        self.name = name
        self.description = description
        self.handler_function = handler_function
        self.show_in_help = show_in_help
        register_command(self)

    @property
    def handler(self):
        return CommandHandler(self.name, self.handler_function)


start = LangCommand(
    'start',
    'show menu',
    handlers.start
)

add_translations = LangCommand(
    'add',
    'add new translations',
    handlers.add_translations
)

show_translations = LangCommand(
    'show',
    'show translations',
    handlers.show_translations
)

start_quiz = LangCommand(
    'quiz',
    'start new quiz',
    handlers.start_quiz
)

end_quiz = LangCommand(
    'end',
    'end current quiz',
    handlers.end_quiz
)
