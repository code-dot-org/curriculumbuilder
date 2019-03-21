# pylint: disable=missing-docstring,too-few-public-methods,no-self-use
import django.apps

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation

from i18n.management.utils import log, should_sync_model


class Command(BaseCommand):
    def should_publish_model(self, model):
        model_has_publish_operation = hasattr(model, 'publish') or hasattr(model, 'publish_pdfs')
        return should_sync_model(model) and model_has_publish_operation

    def handle(self):
        log("I18n Sync Step 4 of 4: Publish translated content to S3")
        models = [
            model for model in django.apps.apps.get_models()
            if self.should_publish_model(model)
        ]
        log("Models to publish: %s" % ', '.join(model.__name__ for model in models))

        for model_index, model in enumerate(models):
            name = model.__name__
            log("Publishing %s (%s/%s)" % (name, model_index + 1, len(models)))
            objects = model.get_i18n_objects()
            total = objects.count()
            success_count = 0

            for obj in objects.all():
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
