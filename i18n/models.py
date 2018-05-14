from __future__ import print_function

import json
import os
import sys
import time

from django.conf import settings

from mezzanine.pages.models import Page


class Internationalizable:

    class Meta:
        abstract = True

    @classmethod
    def internationalizable_fields(cls):
        return []

    @classmethod
    def get_i18n_objects(cls):
        return cls.objects

    @classmethod
    def gather_strings(cls):
        strings = {}
        objects = cls.get_i18n_objects()
        total = objects.count()
        index = 0
        elapsed = 0
        for obj in objects.all():
            index += 1
            average = elapsed / index
            expected = elapsed + ((total - index) * average)
            print("%s: %s/%s (%0.2f elapsed, %0.2f expected, %0.4f average)" % (cls.__name__, index, total, elapsed, expected, average), end='\r')
            sys.stdout.flush()
            start = time.time()
            if obj.should_be_translated:
                key = obj.i18n_key
                strings[key] = {}
                for field in cls.internationalizable_fields():
                    string = getattr(obj, field)
                    if string:
                        strings[key][field] = getattr(obj, field)
            end = time.time()
            elapsed += (end - start)
        print("%s: complete (%0.2f elapsed, %0.4f average)                       " % (cls.__name__, elapsed, (elapsed/total)))
        return strings

    @property
    def should_be_translated(self):
        return True

    @property
    def i18n_key(self):
        return self.pk

    def translate_to(self, lang):
        # don't bother to translate the default language
        if lang == settings.LANGUAGE_CODE:
            return

        for field in self.__class__.internationalizable_fields():
            translated = self.get_translated_field(field, lang)
            if translated:
                setattr(self, field, translated)

    def get_translated_field(self, field, lang):
        translation_file = os.path.join(os.path.dirname(__file__), 'static', lang, self.__class__.__name__ + '.json')
        try:
            translation_json = open(translation_file, 'r')
        except IOError:
            # Could not find the translation file; most likely the locale string
            # is malformed or simply referencing a language we are not yet
            # translating
            return ""
        try:
            translations = json.load(translation_json)
        except ValueError:
            # Could not parse the translation file; this should not happen, and
            # probably represents a significant problem in the i18n sync process
            return ""
        try:
            return translations[self.slug][field]
        except KeyError:
            # Could not find the specified string in the translation file,
            # possibly just because the string is new and has not yet been
            # through the sync process. If crowdin is set up to only export
            # translated strings, this might also happen whenever a string
            # exists but has not yet been translated
            return ""

class InternationalizablePage(Internationalizable, Page):

    class Meta:
        abstract = True

    @classmethod
    def get_i18n_objects(cls):
        return super(InternationalizablePage, cls).get_i18n_objects().select_related('parent')

    @property
    def should_be_translated(self):
        if self.parent and isinstance(self.parent, Page):
            real_parent = self.parent.get_content_model()
            if isinstance(real_parent, Internationalizable):
                return real_parent.should_be_translated

        return True;

    @property
    def i18n_key(self):
        return self.slug

    @classmethod
    def internationalizable_fields(cls):
        return ['title', 'description']
