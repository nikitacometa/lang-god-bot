import asyncio
import os
import telegram
import logging

import account_manager


logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s-%(message)s', level=logging.INFO)
logger = logging.getLogger()
bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])


def process_new_translations(user_id, translation_request):
    word, translations_str = translation_request.split(' - ')
    translations = translations_str.split(',')
    new_translations = 0

    for translation in translations:
        if account_manager.save_translation(user_id, word, translation):
            new_translations += 1

    return "{} new translations were added!".format(new_translations)


def process_show_user_translations(user_id):
    user_translations = account_manager.get_user_translations(user_id)
    return '\n'.join(word + ', '.join(trans) for word, trans in user_translations.items())


async def process_request(user_id, handler, *args):
    response_str = handler(user_id, *args)
    return response_str


def webhook(new_request):
    if new_request.method == "POST":
        update = telegram.Update.de_json(new_request.get_json(force=True), bot)
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        request_str = update.message.text

        if request_str.startswith("/add"):
            asyncio.create_task(process_request())
            response_str = process_new_translations(user_id, request_str)
        elif request_str == "/show":
            response_str = process_show_user_translations(user_id)
        else:
            response_str = "you are pidor"
        bot.sendMessage(chat_id=chat_id, text=response_str)

    return "ok"
