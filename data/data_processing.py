from data.translation_manager import TranslationManager


class DataProcessing:
    @staticmethod
    def process_new_translations(user_id, translation_request):
        word, translations_str = translation_request.split(' - ')
        translations = translations_str.split(',')
        new_translations = 0

        for translation in translations:
            if TranslationManager.save_translation(user_id, word, translation):
                new_translations += 1

        return new_translations

    @staticmethod
    def process_show_translations(user_id):
        user_translations = TranslationManager.get_user_translations(user_id)

        return '\n'.join(word + ', '.join(trans) for word, trans in user_translations.items())
