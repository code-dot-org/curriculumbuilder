import json
import logging
import os

from django.conf import settings
from django.core.cache import cache
from django.utils.module_loading import import_string

from cStringIO import StringIO

logger = logging.getLogger(__name__)

class I18nFileWrapper:

    _storage = None

    @classmethod
    def _load_translations(cls, name, lang):
        path = os.path.join("translations", lang, name + ".json")
        translations = cache.get(path)
        if translations is None:
            try:
                translation_file = cls.storage().open(path, 'r')
                try:
                    translations = json.load(translation_file)
                except ValueError:
                    logger.error("could not parse %s" % path)
                    # Could not parse the translation file; this should not
                    # happen, and probably represents a significant problem
                    # in the i18n sync process
                    translations = {}
            except IOError:
                logger.error("could not open %s" % path)
                # Could not find the translation file; most likely the locale
                # string is malformed or simply referencing a language we are
                # not yet translating
                translations = {}
            cache.set(path, translations)

        return translations

    @classmethod
    def get_translated_field(cls, name, i18n_key, field, lang):
        translations = cls._load_translations(name, lang)
        try:
            return translations[i18n_key][field]
        except KeyError:
            # Could not find the specified string in the translation file,
            # possibly just because the string is new and has not yet been
            # through the sync process. If crowdin is set up to only export
            # translated strings, this might also happen whenever a string
            # exists but has not yet been translated
            logger.warning("could not find %s[%s][%s] for %s" % (name, i18n_key, field, lang))
            return ""

    @classmethod
    def write_source(cls, name, strings):
        path = os.path.join("source", name + ".json")
        content = json.dumps(strings, indent=4, sort_keys=True)
        cls.storage().save(path, StringIO(content))

    @classmethod
    def storage(cls):
        if cls._storage is None:
            storage = getattr(settings, 'I18N_STORAGE', 'django.core.files.storage.FileSystemStorage')
            storage_cls = import_string(storage)
            cls._storage = storage_cls(location=getattr(settings, 'I18N_STORAGE_LOCATION', 'i18n'))
        return cls._storage
