import re

from django.conf import settings
from django.utils import translation
from django.middleware.locale import LocaleMiddleware

from management.utils import get_non_english_language_codes

def get_language_from_path_strict(path, allowed_languages):
    for language_code in allowed_languages:
        if path.startswith('/{}/'.format(language_code)):
            return language_code
    return settings.LANGUAGE_CODE

class StrictLocaleMiddleware(LocaleMiddleware):
    """
    See https://github.com/django/django/blob/6a0dc2176f4ebf907e124d433411e52bba39a28e/django/middleware/locale.py#L29
    for the original implementation
    This function simply checks for the language of the request by only looking at the URL.
    It also requires an exact language match in order to set the language (see above)
    """
    def __init__(self):
        super(StrictLocaleMiddleware, self).__init__()
        self.language_codes = get_non_english_language_codes()

    def process_request(self, request):
        language = get_language_from_path_strict(
                request.path_info, self.language_codes)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
