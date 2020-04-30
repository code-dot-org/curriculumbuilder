import re
import warnings

from django.conf import settings
from django.utils import translation
from django.http import HttpResponseRedirect
from django.middleware.locale import LocaleMiddleware

def get_language_from_path_strict(path, allowed_languages):
    language_code_prefix_re = re.compile(r'^/([\w-]+)(/|$)')
    regex_match = language_code_prefix_re.match(path)
    if not regex_match:
        return settings.LANGUAGE_CODE
    lang_code = regex_match.group(1)
    if lang_code not in allowed_languages:
        return settings.LANGUAGE_CODE
    return lang_code

class StrictLocaleMiddleware(LocaleMiddleware):

    def __init__(self):
        super(StrictLocaleMiddleware, self).__init__()
        self.language_codes = [
            language_code for language_code, _ in settings.LANGUAGES
            if language_code != settings.LANGUAGE_CODE
        ]

    # See https://github.com/django/django/blob/6a0dc2176f4ebf907e124d433411e52bba39a28e/django/middleware/locale.py#L29
    # for the original implementation
    # This function simply checks for the language of the request by only looking at the URL.
    # It also requires an exact language match in order to set the language (see above)
    def process_request(self, request):
        language = get_language_from_path_strict(
                request.path_info, self.language_codes)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
