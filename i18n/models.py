from __future__ import print_function

import sys
import time

from django.conf import settings
from django.db import models
from django.utils import translation
from django.utils.translation import to_locale

from mezzanine.pages.models import Page

from .utils import I18nFileWrapper


class Internationalizable(models.Model):

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        # add an instance attribute for saving the fields that get overwritten
        # by the translation process
        self._untranslated_values = {}
        return super(Internationalizable, self).__init__(*args, **kwargs)

    @classmethod
    def from_db(cls, *args):
        instance = super(Internationalizable, cls).from_db(*args)
        lang = translation.get_language()
        if lang and lang != settings.LANGUAGE_CODE:
            locale = to_locale(lang)
            instance.translate_to(locale)
        return instance

    @classmethod
    def should_redact(cls):
        return False

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
        if total == 0:
            print("%s: no internationalizable objects to gather from" % cls.__name__)
            return strings

        index = 0
        elapsed = 0
        # Because this process is intended to be invoked from a management
        # command, we don't care about caching the results of the queryset. In
        # fact, in the case of large querysets that cache can have significant
        # performance implications, so here we use iterator() to skip the
        # cache.
        for obj in objects.all().iterator():
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
        return str(self.pk)

    def get_untranslated_field(self, field):
        if field in self._untranslated_values:
            return self._untranslated_values[field]
        elif hasattr(self, field):
            return getattr(self, field)

    def translate_to(self, lang):
        # don't bother to translate the default language
        if lang == settings.LANGUAGE_CODE:
            return

        for field in self.__class__.internationalizable_fields():
            translated = I18nFileWrapper.get_translated_field(self.__class__.__name__, self.i18n_key, field, lang)
            if translated:
                if field not in self._untranslated_values:
                    self._untranslated_values[field] = getattr(self, field)
                setattr(self, field, translated)

class InternationalizablePage(Page, Internationalizable):

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
        return ['title', 'description', 'content']

    @classmethod
    def should_redact(cls):
        return True
