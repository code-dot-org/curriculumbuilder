import json
import os

import django.apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation

from i18n.models import Internationalizable
from i18n.utils import print_clear

from django_slack import slack_message

def should_publish_model(model):
    is_internationalizable = issubclass(model, Internationalizable)
    is_not_proxy = not model._meta.proxy
    has_publish_operation = hasattr(model, 'publish') or hasattr(model, 'publish_pdfs')
    return is_internationalizable and is_not_proxy and has_publish_operation

def log(message):
    print(message)
    slack_message('slack/message.slack', {
        'message': message
    })

class Command(BaseCommand):
    def handle(self, *args, **options):
        log("Publishing translated content")
        models = [model for model in django.apps.apps.get_models() if should_publish_model(model)]
        log("Models to publish: %s" % ', '.join(model.__name__ for model in models))

        for model_index, model in enumerate(models):
            name = model.__name__
            log("Publishing %s (%s/%s)" % (name, model_index + 1, len(models)))
            objects = model.get_i18n_objects()
            total = objects.count()
            success_count = 0

            for index, obj in enumerate(objects.all()):
                if not obj.should_be_translated:
                    continue

                original_lang = translation.get_language()
                for language_code, _ in settings.LANGUAGES:
                    if language_code == settings.LANGUAGE_CODE:
                        continue

                    translation.activate(language_code)
                    if hasattr(obj, 'publish'):
                        list(obj.publish(silent=True))
                    if hasattr(obj, 'publish_pdfs'):
                        list(obj.publish_pdfs(silent=True))
                success_count += 1

                translation.activate(original_lang)
            log("%s/%s %s objects published" % (success_count, total, name))
