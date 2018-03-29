from __future__ import print_function

import sys
import time

from mezzanine.pages.models import Page
import json
import os

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

    def translate_to(self, lang):
        for field in self.__class__.internationalizable_fields():
            translated = self.get_translated_field(field, lang)
            if translated:
                print(translated)
            else:
                print("nope")
            if translated:
                setattr(self, field, translated)

    def get_translated_field(self, field, lang):
        translation_file = os.path.join(os.path.dirname(__file__), 'static', lang, self.__class__.__name__ + '.json')
        translations = json.load(open(translation_file))
        print(self.slug)
        try:
            return translations[self.slug][field]
        except KeyError:
            return ""
