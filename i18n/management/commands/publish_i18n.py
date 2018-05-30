import json
import os

import django.apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation

from i18n.models import Internationalizable

class Command(BaseCommand):
    def handle(self, *args, **options):
        for model in django.apps.apps.get_models():
            is_internationalizable = issubclass(model, Internationalizable)
            is_not_proxy = not model._meta.proxy
            if not (is_internationalizable and is_not_proxy):
                continue

            for obj in model.objects.all():
                if not obj.should_be_translated:
                    continue

                original_lang = translation.get_language()
                for language_code, _ in settings.LANGUAGES:
                    if language_code == settings.LANGUAGE_CODE:
                        continue

                    translation.activate(language_code)
                    if hasattr(obj, 'publish'):
                        list(obj.publish())
                    if hasattr(obj, 'publish_pdfs'):
                        list(obj.publish_pdfs())

                translation.activate(original_lang)
